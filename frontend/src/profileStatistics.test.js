import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const fixture = JSON.parse(readFileSync(new URL("../design-fixtures/profile-rating-dense.json", import.meta.url)));
const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");

test("dense profile fixture carries four-digit identity and strip counts", () => {
  assert.ok(fixture.profile.follower_count >= 1000);
  assert.ok(fixture.profile.following_count >= 1000);
  for (const key of ["events_in_been", "written_reviews", "venues_visited", "cities_visited"]) {
    assert.ok(fixture.statistics[key] >= 1000);
  }
});

test("profile histogram CSS source declares one contextualized placement size outside media overrides", () => {
  const occurrences = css.match(/\.profile-histogram-group\{width:104px;flex:0 0 104px\}/g) ?? [];
  assert.equal(occurrences.length, 1);
  assert.match(css, /\.rating-histogram\.profile-stat-histogram\{width:100%\}/);
  assert.match(css, /\.profile-stat-histogram \.hist-bars\{height:30px\}/);
  assert.match(css, /\.profile-histogram-group\.is-empty \.hist-fill\{background:var\(--border-strong\)\}/);
  assert.doesNotMatch(css, /\.hist-bar(?:\[data-tooltip\])?[^}]*::after/);
  assert.match(css, /\.rating-histogram-details>summary\{[^}]*min-height:44px/);
  assert.doesNotMatch(css, /@media[^}]+(?:profile-histogram-group|profile-stat-histogram)[^}]+(?:width|height)/s);
});

test("desktop rating and histogram occupy one aligned judgment unit", () => {
  assert.match(css, /@container \(min-width:680px\)\{[\s\S]*grid-template-columns:repeat\(4,minmax\(0,1fr\)\) 224px/);
  assert.match(css, /\.profile-statistics-strip:has\(\.profile-histogram-note\)\{padding-bottom:var\(--sp-24\)\}/);
  assert.match(css, /\.profile-judgment-unit\{width:224px;align-items:flex-start\}/);
  assert.match(css, /\.profile-judgment-unit \.profile-stat\{width:108px;max-width:none;flex:0 0 108px\}/);
  assert.match(css, /\.profile-judgment-unit \.stat-label\{max-width:none;white-space:nowrap\}/);
  assert.match(css, /\.profile-histogram-group\{position:relative\}/);
  assert.match(css, /\.profile-histogram-note\{position:absolute;top:100%;left:0\}/);
  assert.match(css, /\.profile-stat-histogram \.hist-axis\{margin-top:var\(--sp-4\)\}/);
});
