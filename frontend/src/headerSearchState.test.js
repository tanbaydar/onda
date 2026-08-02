import assert from "node:assert/strict";
import test from "node:test";

import { headerSearchMode, shouldExpandHeaderSearch } from "./headerSearchState.js";

test("header Search remains text on the Search route", () => {
  assert.equal(headerSearchMode("/search", false), "text");
  assert.equal(headerSearchMode("/search", true), "text");
});

test("expanded header Search collapses when navigation reaches Search", () => {
  assert.equal(headerSearchMode("/discover", true), "input");
  assert.equal(headerSearchMode("/search", true), "text");
});

test("header quick search activates only on desktop away from Search", () => {
  assert.equal(shouldExpandHeaderSearch("/discover", true), true);
  assert.equal(shouldExpandHeaderSearch("/discover", false), false);
  assert.equal(shouldExpandHeaderSearch("/search", true), false);
});
