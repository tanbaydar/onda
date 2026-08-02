import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { PROFILE_EMPTY_STATES, profileBioCount, profileInitials, profileTabPath } from "./profilePresentation.js";

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

test("tab routes change only the content selection below the shared profile shell", () => {
  assert.equal(profileTabPath("Listener", "been"), "/u/listener");
  assert.equal(profileTabPath("Listener", "reviews"), "/u/listener/reviews");
  const source = readFileSync(new URL("./pages/ProfilePage.jsx", import.meta.url), "utf8");
  assert.ok(source.indexOf("<ProfileStatistics") < source.indexOf('className="profile-tabs"'));
  assert.ok(source.indexOf('className="profile-tabs"') < source.indexOf('tab === "reviews" ? <ReviewsTab'));
});

test("profile surfaces never render the old default-avatar words", () => {
  const profile = readFileSync(new URL("./pages/ProfilePage.jsx", import.meta.url), "utf8");
  const editor = readFileSync(new URL("./pages/EditProfilePage.jsx", import.meta.url), "utf8");
  assert.doesNotMatch(profile + editor, /Default avatar/);
});
