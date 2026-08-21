import assert from "node:assert/strict";
import test from "node:test";

import {
  histogramBarHeight,
  profileRatingBuckets,
  profileRatingCount,
  profileRatingHistogramVisible,
} from "./ratingHistogram.js";

test("an unavailable profile distribution does not synthesize chart data", () => {
  const buckets = profileRatingBuckets({ state: "empty" });
  assert.deepEqual(buckets, []);
  assert.equal(profileRatingCount({ state: "empty" }), 0);
  assert.equal(profileRatingHistogramVisible({ state: "empty" }), false);
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

test("the profile histogram gate changes only at five ratings", () => {
  assert.equal(profileRatingCount(distributionWithCount(4)), 4);
  assert.equal(profileRatingHistogramVisible(distributionWithCount(4)), false);
  assert.equal(profileRatingCount(distributionWithCount(5)), 5);
  assert.equal(profileRatingHistogramVisible(distributionWithCount(5)), true);
});

test("the profile histogram threshold sums ratings across buckets", () => {
  const distribution = distributionWithCount(0);
  distribution.buckets[0].count = 2;
  distribution.buckets[9].count = 3;
  assert.equal(profileRatingCount(distribution), 5);
  assert.equal(profileRatingHistogramVisible(distribution), true);
});

test("an eligible profile retains all ten histogram buckets", () => {
  const buckets = profileRatingBuckets(distributionWithCount(5));
  assert.deepEqual(
    buckets.map((bucket) => histogramBarHeight(bucket.relative_value)),
    [
      ...Array(7).fill("var(--sp-2)"),
      "100%",
      ...Array(2).fill("var(--sp-2)"),
    ],
  );
});
