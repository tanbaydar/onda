import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const fixture = JSON.parse(readFileSync(new URL("../design-fixtures/profile-rating-dense.json", import.meta.url)));
const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
const profilePage = readFileSync(new URL("./pages/ProfilePage.jsx", import.meta.url), "utf8");

test("dense profile fixture carries four-digit identity and strip counts", () => {
  assert.ok(fixture.profile.follower_count >= 1000);
  assert.ok(fixture.profile.following_count >= 1000);
  for (const key of ["events_in_been", "written_reviews", "venues_visited", "cities_visited"]) {
    assert.ok(fixture.statistics[key] >= 1000);
  }
});

test("profile histogram CSS source declares one contextualized placement size outside media overrides", () => {
  const occurrences = css.match(/\.profile-histogram-group\{grid-area:histogram;width:104px;align-self:end\}/g) ?? [];
  assert.equal(occurrences.length, 1);
  assert.match(css, /\.rating-histogram\.profile-stat-histogram\{width:100%\}/);
  assert.match(css, /\.profile-stat-histogram \.hist-bars\{height:30px\}/);
  assert.match(css, /\.profile-histogram-group\.is-empty \.hist-fill\{background:var\(--border-strong\)\}/);
  assert.doesNotMatch(css, /\.hist-bar(?:\[data-tooltip\])?[^}]*::after/);
  assert.match(css, /\.rating-histogram-details>summary\{[^}]*min-height:44px/);
  assert.doesNotMatch(css, /@media[^}]+(?:profile-histogram-group|profile-stat-histogram)[^}]+(?:width|height)/s);
});

test("statistics use the ruled six-cell desktop and mobile order", () => {
  assert.match(css, /grid-template-areas:"lead venues cities" "reviews average histogram"/);
  assert.match(css, /grid-template-columns:minmax\(0,1fr\) minmax\(0,1fr\) 104px/);
  assert.match(css, /@media \(min-width:768px\)\{[\s\S]*grid-template-areas:"lead venues cities reviews average histogram"/);
  assert.match(css, /\.profile-stat\.stat-average\{grid-area:average\}/);
  assert.match(css, /\.profile-histogram-group\{grid-area:histogram;width:104px;align-self:end\}/);
  assert.match(css, /\.profile-stat-histogram \.hist-axis\{margin-top:var\(--sp-4\)\}/);
  assert.doesNotMatch(css, /profile-histogram-note|profile-judgment-unit/);

  const orderedClasses = ["stat-lead", "stat-venues", "stat-cities", "stat-reviews", "stat-average", "profile-histogram-group"];
  for (let index = 1; index < orderedClasses.length; index += 1) {
    assert.ok(profilePage.indexOf(orderedClasses[index - 1]) < profilePage.indexOf(orderedClasses[index]));
  }
  assert.doesNotMatch(profilePage, /profileRatingLowVolumeNote|profile-histogram-note/);
});
