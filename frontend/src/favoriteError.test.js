import test from "node:test";
import assert from "node:assert/strict";

import { classifyFavoriteError } from "./favoriteError.js";
import { favoriteRequestRejected, favoriteRequestStarted } from "./favoriteControlState.js";


test("favorite limit conflicts preserve the field message without refetching", () => {
  assert.deepEqual(
    classifyFavoriteError({ status: 409, data: { errors: { favorite: ["You may favorite at most 3 items of this type."] } } }),
    {
      message: "Favorites are limited to 3 per type.",
      refetch: false,
      authenticationRequired: false,
    },
  );
});

test("missing favorite targets reconcile while other failures render honestly", () => {
  assert.equal(classifyFavoriteError({ status: 404 }).refetch, true);
  assert.equal(classifyFavoriteError({ status: 500 }).message, "The favorite could not be changed.");
  assert.equal(classifyFavoriteError({}).message, "The favorite could not be changed.");
});

test("favorite rejection preserves its message and returns the control to resting", () => {
  assert.deepEqual(favoriteRequestStarted(), { pending: true, message: null });
  assert.deepEqual(favoriteRequestRejected("Favorites are limited to 3 per type."), {
    pending: false,
    message: "Favorites are limited to 3 per type.",
  });
});
