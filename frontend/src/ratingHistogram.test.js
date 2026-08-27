import assert from "node:assert/strict";
import test from "node:test";

import {
  histogramBarHeight,
  profileRatingBuckets,
  profileRatingCount,
  profileRatingLowVolumeNote,
  ratingBucketLabel,
  ratingDistributionDescription,
} from "./ratingHistogram.js";

test("an empty profile distribution renders a complete neutral frame with honest copy", () => {
  const buckets = profileRatingBuckets({ state: "empty" });
  assert.equal(buckets.length, 10);
  assert.deepEqual(
    buckets.map((bucket) => histogramBarHeight(bucket.relative_value)),
    Array(10).fill("var(--sp-2)"),
  );
  assert.equal(profileRatingCount({ state: "empty" }), 0);
  assert.equal(profileRatingLowVolumeNote({ state: "empty" }), "No ratings given yet.");
});

function distributionWithCount(count) {
  return {
    state: "available",
    buckets: Array.from({ length: 10 }, (_, index) => ({
      rating: (index + 1) / 2,
      count: index === 7 ? count : 0,
      relative_value: index === 7 ? 1 : 0,
    })),
  };
}

test("one through four ratings retain the real distribution and disclose the sample size", () => {
  for (const [count, note] of [[1, "1 rating given"], [4, "4 ratings given"]]) {
    const distribution = distributionWithCount(count);
    assert.equal(profileRatingCount(distribution), count);
    assert.equal(profileRatingLowVolumeNote(distribution), note);
    assert.equal(profileRatingBuckets(distribution)[7].relative_value, 1);
  }
});

test("five or more ratings keep the established histogram without low-volume copy", () => {
  assert.equal(profileRatingCount(distributionWithCount(5)), 5);
  assert.equal(profileRatingLowVolumeNote(distributionWithCount(5)), null);
});

test("the profile rating count sums ratings across buckets", () => {
  const distribution = distributionWithCount(0);
  distribution.buckets[0].count = 2;
  distribution.buckets[9].count = 3;
  assert.equal(profileRatingCount(distribution), 5);
  assert.equal(profileRatingLowVolumeNote(distribution), null);
});

test("an available profile retains all ten histogram buckets", () => {
  const buckets = profileRatingBuckets(distributionWithCount(1));
  assert.deepEqual(
    buckets.map((bucket) => histogramBarHeight(bucket.relative_value)),
    [
      ...Array(7).fill("var(--sp-2)"),
      "100%",
      ...Array(2).fill("var(--sp-2)"),
    ],
  );
});

test("a rating bucket has a complete accessible value with correct plurality", () => {
  assert.equal(ratingBucketLabel({ rating: 0.5, count: 0 }), "0.5 stars: 0 ratings");
  assert.equal(ratingBucketLabel({ rating: 3.5, count: 1 }), "3.5 stars: 1 rating");
  assert.equal(ratingBucketLabel({ rating: 5, count: 12 }), "5.0 stars: 12 ratings");
});

test("the semantic distribution description includes all ten buckets", () => {
  const buckets = distributionWithCount(5).buckets;
  const description = ratingDistributionDescription(buckets);

  assert.equal(description.match(/stars:/g)?.length, 10);
  assert.match(description, /^0\.5 stars: 0 ratings\./);
  assert.match(description, /4\.0 stars: 5 ratings\./);
  assert.match(description, /5\.0 stars: 0 ratings\.$/);
});
