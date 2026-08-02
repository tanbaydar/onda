import assert from "node:assert/strict";
import test from "node:test";

import {
  histogramBarHeight,
  profileRatingBuckets,
} from "./ratingHistogram.js";

test("zero ratings render ten baseline stubs", () => {
  const buckets = profileRatingBuckets({ state: "empty" });
  assert.equal(buckets.length, 10);
  assert.deepEqual(
    buckets.map((bucket) => histogramBarHeight(bucket.relative_value)),
    Array(10).fill("var(--sp-2)"),
  );
});

test("one rating renders one full bar and nine baseline stubs", () => {
  const buckets = profileRatingBuckets({
    state: "available",
    buckets: Array.from({ length: 10 }, (_, index) => ({
      rating: (index + 1) / 2,
      count: index === 7 ? 1 : 0,
      relative_value: index === 7 ? 1 : 0,
    })),
  });
  assert.deepEqual(
    buckets.map((bucket) => histogramBarHeight(bucket.relative_value)),
    [
      ...Array(7).fill("var(--sp-2)"),
      "100%",
      ...Array(2).fill("var(--sp-2)"),
    ],
  );
});
