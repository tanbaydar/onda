import assert from "node:assert/strict";
import test from "node:test";

import { readRecentSearches, recordRecentSearch } from "./recentSearches.js";

function memoryStorage(initial = []) {
  let value = JSON.stringify(initial);
  return {
    getItem() { return value; },
    setItem(_key, next) { value = next; },
  };
}

test("typing without a commit records nothing", () => {
  const storage = memoryStorage();
  const typedQueries = ["f", "fr", "fran", "frank"];
  typedQueries.forEach((query) => query.trim());
  assert.deepEqual(readRecentSearches(storage), []);
});

test("a result-click commit records the live trimmed query", () => {
  const storage = memoryStorage();
  recordRecentSearch("  frank  ", storage);
  assert.deepEqual(readRecentSearches(storage), ["frank"]);
});

test("recording removes case-insensitive duplicates and existing prefixes", () => {
  const storage = memoryStorage(["F", "fr", "Frank", "house"]);
  recordRecentSearch("Frankie", storage);
  assert.deepEqual(readRecentSearches(storage), ["Frankie", "house"]);
});
