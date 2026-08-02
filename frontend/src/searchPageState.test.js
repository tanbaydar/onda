import assert from "node:assert/strict";
import test from "node:test";

import {
  EMPTY_SEARCH_STATE,
  isCurrentSearchRequest,
  scopeTransition,
} from "./searchPageState.js";

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
