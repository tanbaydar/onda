import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const component = readFileSync(new URL("./components/RatingHistogram.jsx", import.meta.url), "utf8");

test("histogram buckets are static presentation rather than microscopic controls", () => {
  assert.doesNotMatch(component, /<button|onClick=|data-tooltip=|aria-pressed=/);
  assert.match(component, /<div className="hist-bars" aria-hidden="true">/);
  assert.match(component, /<span\s+key=\{bucket\.rating\}\s+className=\{`hist-bar/);
});

test("the chart exposes all values semantically without a visual disclosure", () => {
  assert.match(component, /role="img" aria-label="Rating distribution chart" aria-describedby=\{descriptionId\}/);
  assert.match(component, /ratingDistributionDescription\(buckets\)/);
  assert.doesNotMatch(component, /<details|<summary|View distribution/);
});

test("a supplied static label augments one chart description rather than adding a second accessible name", () => {
  assert.match(component, /\[staticLabel, ratingDistributionDescription\(buckets\)\]/);
  assert.doesNotMatch(component, /role=\{staticLabel|aria-label=\{staticLabel/);
});
