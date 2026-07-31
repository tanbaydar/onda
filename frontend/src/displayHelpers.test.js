import test from "node:test";
import assert from "node:assert/strict";

import { formatTimestamp } from "./lib/formatTimestamp.js";
import { pluralize } from "./lib/plural.js";


test("pluralize chooses one shared singular and plural form", () => {
  assert.equal(pluralize(0, "review"), "0 reviews");
  assert.equal(pluralize(1, "review"), "1 review");
  assert.equal(pluralize(2, "person", "people"), "2 people");
  assert.equal(pluralize("1.0", "star"), "1.0 star");
});

test("formatTimestamp is a stable absolute UTC calendar date", () => {
  assert.equal(formatTimestamp("2026-01-14T23:30:00Z"), "Jan 14, 2026");
});
