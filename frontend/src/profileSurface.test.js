import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { PROFILE_EMPTY_STATES, PROFILE_REVIEW_SORTS, profileBioCount, profileInitials, profileTabPath } from "./profilePresentation.js";

test("initials avatar uses one or two display-name initials", () => {
  assert.equal(profileInitials("Cher"), "CH");
  assert.equal(profileInitials("Review Public Test"), "RT");
  assert.equal(profileInitials("  "), "?");
});

test("bio counter reports the live stored character count", () => {
  assert.equal(profileBioCount(""), "0 / 150");
  assert.equal(profileBioCount("dance"), "5 / 150");
});

test("profile tab empty states are the ruled single lines", () => {
  assert.equal(PROFILE_EMPTY_STATES.been, "No events in Been yet.");
  assert.equal(PROFILE_EMPTY_STATES.reviews, "No reviews yet.");
  assert.doesNotMatch(PROFILE_EMPTY_STATES.been + PROFILE_EMPTY_STATES.reviews, /\n/);
});

test("ProfilePage source places tab-selected content below the shared shell", () => {
  assert.equal(profileTabPath("Listener", "been"), "/u/listener");
  assert.equal(profileTabPath("Listener", "reviews"), "/u/listener/reviews");
  const source = readFileSync(new URL("./pages/ProfilePage.jsx", import.meta.url), "utf8");
  assert.ok(source.indexOf("<ProfileStatistics") < source.indexOf('className="profile-tabs"'));
  assert.ok(source.indexOf('className="profile-tabs"') < source.indexOf('tab === "reviews" ? <ReviewsTab'));
});

test("profile page sources omit the retired default-avatar copy", () => {
  const profile = readFileSync(new URL("./pages/ProfilePage.jsx", import.meta.url), "utf8");
  const editor = readFileSync(new URL("./pages/EditProfilePage.jsx", import.meta.url), "utf8");
  assert.doesNotMatch(profile + editor, /Default avatar/);
});

test("ProfilePage source uses the four-option custom sort contract without select markup", () => {
  assert.deepEqual(PROFILE_REVIEW_SORTS.map(({ label }) => label), ["Newest", "Most liked", "Oldest", "Longest entry"]);
  const profile = readFileSync(new URL("./pages/ProfilePage.jsx", import.meta.url), "utf8");
  assert.doesNotMatch(profile, /<select/);
  assert.doesNotMatch(profile, /Sort reviews<\/label>/);
});

test("ProfilePage gives empty favorites purposeful owner and viewer states", () => {
  const profile = readFileSync(new URL("./pages/ProfilePage.jsx", import.meta.url), "utf8");
  assert.match(profile, /const hasFavorites = groups\.some\(\(group\) => group\.items\.length > 0\)/);
  assert.match(profile, /className="profile-favorites-empty"><p>No favorites yet\.<\/p>/);
  assert.match(profile, /owner \? <Link to="\/discover">Discover events<\/Link> : null/);
  assert.match(profile, /hasFavorites \? <div className="profile-favorite-groups">/);
});
