import test from "node:test";
import assert from "node:assert/strict";

import { classifyFavoriteError } from "./favoriteError.js";


test("favorite limit conflicts preserve the field message without refetching", () => {
  assert.deepEqual(
    classifyFavoriteError({ status: 409, data: { errors: { favorite: ["You may favorite at most 3 items of this type."] } } }),
    {
      message: "You may favorite at most 3 items of this type.",
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
