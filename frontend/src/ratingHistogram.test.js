import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  histogramBarHeight,
  ratingTooltip,
  shouldRenderRatingHistogram,
} from "./ratingHistogram.js";

const fixture = JSON.parse(
  readFileSync(new URL("../design-fixtures/profile-rating-dense.json", import.meta.url)),
);
const buckets = fixture.rating_distribution.buckets;

test("dense profile fixture exercises the locked histogram anatomy", () => {
  assert.equal(buckets.length, 10);
  assert.equal(shouldRenderRatingHistogram(buckets), true);
  assert.ok(buckets.reduce((total, bucket) => total + bucket.count, 0) >= 5);
  assert.ok(buckets.some((bucket) => bucket.relative_value === 0));
  assert.equal(histogramBarHeight(0), "var(--sp-2)");
  assert.equal(histogramBarHeight(0.375), "37.5%");
  assert.equal(ratingTooltip(buckets[0]), "1 · 0.5★");
});

test("profiles below five ratings omit the histogram", () => {
  assert.equal(
    shouldRenderRatingHistogram([{ rating: 5, count: 1, relative_value: 1 }]),
    false,
  );
});
