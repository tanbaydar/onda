import assert from "node:assert/strict";
import test from "node:test";

import {
  EMPTY_SEARCH_STATE,
  isCurrentSearchRequest,
  MIN_SEARCH_QUERY_LENGTH,
  searchQueryReady,
  scopeTransition,
} from "./searchPageState.js";

test("search waits for two trimmed characters", () => {
  assert.equal(MIN_SEARCH_QUERY_LENGTH, 2);
  for (const query of ["", " ", "a", " a "]) {
    assert.equal(searchQueryReady(query), false, JSON.stringify(query));
  }
  for (const query of ["ab", " ab ", "a b"]) {
    assert.equal(searchQueryReady(query), true, JSON.stringify(query));
  }
});

test("active-query scope switching resets results in both directions", () => {
  assert.deepEqual(scopeTransition("all", "artists"), {
    scope: "artists",
    state: EMPTY_SEARCH_STATE,
    activeIndex: -1,
    loadingMore: false,
  });
  assert.deepEqual(scopeTransition("artists", "all"), {
    scope: "all",
    state: EMPTY_SEARCH_STATE,
    activeIndex: -1,
    loadingMore: false,
  });
});

test("a response from the old scope request is discarded after switching", () => {
  const oldArtistsRequest = 4;
  const activeAllRequest = 5;
  assert.equal(isCurrentSearchRequest(activeAllRequest, oldArtistsRequest), false);
  assert.equal(isCurrentSearchRequest(activeAllRequest, activeAllRequest), true);
});
