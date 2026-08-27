import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const component = readFileSync(new URL("./components/RatingHistogram.jsx", import.meta.url), "utf8");

test("histogram buckets are static presentation rather than microscopic controls", () => {
  assert.doesNotMatch(component, /<button|onClick=|data-tooltip=|aria-pressed=/);
  assert.match(component, /<div className="hist-bars" aria-hidden="true">/);
  assert.match(component, /<span\s+key=\{bucket\.rating\}\s+className=\{`hist-bar/);
});

test("the chart exposes all values semantically and one event disclosure", () => {
  assert.match(component, /role="img" aria-label="Rating distribution chart" aria-describedby=\{descriptionId\}/);
  assert.match(component, /ratingDistributionDescription\(buckets\)/);
  assert.match(component, /<details className="rating-histogram-details">/);
  assert.equal(component.match(/<summary>View distribution<\/summary>/g)?.length, 1);
  assert.match(component, /buckets\.map\(\(bucket\) => <li key=\{bucket\.rating\}>\{ratingBucketLabel\(bucket\)\}<\/li>\)/);
});

test("the compact profile chart omits the event disclosure", () => {
  assert.match(component, /className\.split\(\/\\s\+\/\)\.includes\("profile-stat-histogram"\)/);
  assert.match(component, /\{!isCompact \? \(/);
});

test("a supplied static label augments one chart description rather than adding a second accessible name", () => {
  assert.match(component, /\[staticLabel, ratingDistributionDescription\(buckets\)\]/);
  assert.doesNotMatch(component, /role=\{staticLabel|aria-label=\{staticLabel/);
});
