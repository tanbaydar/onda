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

test("profile histogram has one fixed data-register size at both widths", () => {
  const occurrences = css.match(/\.rating-histogram\.profile-stat-histogram\{width:104px;flex:0 0 104px\}/g) ?? [];
  assert.equal(occurrences.length, 1);
  assert.match(css, /\.profile-stat-histogram \.hist-bars\{height:30px\}/);
  assert.doesNotMatch(css, /@media[^}]+profile-stat-histogram[^}]+(?:width|height)/s);
});
