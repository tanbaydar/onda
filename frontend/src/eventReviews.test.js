import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const row = readFileSync(new URL("./components/EventReviewRow.jsx", import.meta.url), "utf8");
const page = readFileSync(new URL("./pages/EventPage.jsx", import.meta.url), "utf8");
const circle = readFileSync(new URL("./components/YourCircle.jsx", import.meta.url), "utf8");
const publicReviews = readFileSync(new URL("./components/PublicReviews.jsx", import.meta.url), "utf8");
const fixture = JSON.parse(readFileSync(new URL("../design-fixtures/event-past-dense.json", import.meta.url)));

test("event review surfaces share the attributed row anatomy", () => {
  assert.match(page, /<EventReviewRow/);
  assert.match(circle, /<EventReviewRow/);
  assert.match(publicReviews, /<EventReviewRow/);
  assert.match(row, /<ProfileAvatar profile=\{person\} small/);
  assert.match(row, /event-review-name/);
  assert.match(row, /event-review-handle/);
});

test("event review ratings render glyphs rather than rating prose", () => {
  assert.match(row, /ratingStars\(rating\)/);
  assert.doesNotMatch(row + circle + publicReviews, /Rating:\s*\{/);
  assert.match(row, /event-review-stars/);
});

test("event review fixtures cover image and initials avatar paths", () => {
  const avatars = Object.values(fixture).flatMap((payload) => (payload.results ?? []).map((item) => item.author?.avatar ?? item.user?.avatar));
  assert.ok(avatars.some((avatar) => typeof avatar === "string"));
  assert.ok(avatars.some((avatar) => avatar === null));
});

test("event review sort reuses the custom menu with its existing two-option contract", () => {
  assert.match(publicReviews, /<ProfileSortMenu/);
  assert.match(publicReviews, /value: "most_liked", label: "Most liked"/);
  assert.match(publicReviews, /value: "newest", label: "Newest"/);
  assert.doesNotMatch(page + circle + publicReviews, /<select/);
});
