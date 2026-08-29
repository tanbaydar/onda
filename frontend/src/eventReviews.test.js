import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const row = readFileSync(new URL("./components/EventReviewRow.jsx", import.meta.url), "utf8");
const page = readFileSync(new URL("./pages/EventPage.jsx", import.meta.url), "utf8");
const circle = readFileSync(new URL("./components/YourCircle.jsx", import.meta.url), "utf8");
const publicReviews = readFileSync(new URL("./components/PublicReviews.jsx", import.meta.url), "utf8");
const fixture = JSON.parse(readFileSync(new URL("../design-fixtures/event-past-dense.json", import.meta.url)));

test("event review source files all compose EventReviewRow", () => {
  assert.match(page, /<EventReviewRow/);
  assert.match(circle, /<EventReviewRow/);
  assert.match(publicReviews, /<EventReviewRow/);
  assert.match(row, /<ProfileAvatar profile=\{person\} small/);
  assert.match(row, /event-review-name/);
  assert.match(row, /event-review-handle/);
});

test("EventReviewRow source composes RatingStars and omits rating prose", () => {
  assert.match(row, /<RatingStars className="event-review-stars" value=\{rating\}/);
  assert.doesNotMatch(row + circle + publicReviews, /Rating:\s*\{/);
  assert.match(row, /event-review-stars/);
});

test("event review fixtures cover image and initials avatar paths", () => {
  const avatars = Object.values(fixture).flatMap((payload) => (payload.results ?? []).map((item) => item.author?.avatar ?? item.user?.avatar));
  assert.ok(avatars.some((avatar) => typeof avatar === "string"));
  assert.ok(avatars.some((avatar) => avatar === null));
});

test("PublicReviews source composes SortMenu with the two-option event contract", () => {
  assert.match(publicReviews, /<SortMenu/);
  assert.match(publicReviews, /value: "most_liked", label: "Most liked"/);
  assert.match(publicReviews, /value: "newest", label: "Newest"/);
  assert.doesNotMatch(page + circle + publicReviews, /<select/);
});

test("owner review editing keeps review actions separate from the Been control", () => {
  const beenControl = readFileSync(new URL("./components/BeenControl.jsx", import.meta.url), "utf8");
  const reviewActions = readFileSync(new URL("./components/ReviewActionsMenu.jsx", import.meta.url), "utf8");
  assert.match(page, /<BeenControl marked=\{viewerHasRating\} disabled=\{saving\} onMark=\{markBeen\} onRemove=\{removeEntry\}/);
  assert.match(page, /\{event\.viewer_entry\.review \? "Edit review" : "Publish review"\}/);
  assert.match(reviewActions, /Edit review/);
  assert.match(reviewActions, /Delete review/);
  assert.doesNotMatch(reviewActions, /hasReview/);
  assert.doesNotMatch(reviewActions, /onRemoveFromBeen/);
  assert.doesNotMatch(reviewActions, /Remove from Been/);
  assert.match(beenControl, /"\/assets\/been-hand-filled\.svg" : "\/assets\/been-hand\.svg"/);
  assert.match(beenControl, /marked \? "Been" : "Mark Been"/);
  assert.match(page, /ratingComposerRef\.current\?\.querySelector\('\[role="slider"\]'\)\?\.focus\(\)/);
});
