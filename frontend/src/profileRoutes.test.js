import assert from "node:assert/strict";
import test from "node:test";

import { legacyBeenRedirect, profilePath } from "./profileRoutes.js";


test("profile paths use the collision-safe canonical username namespace", () => {
  assert.equal(profilePath("tan"), "/u/tan");
  assert.equal(profilePath("Mixed.Case"), "/u/mixed.case");
});

test("legacy Been redirects owners to Profile and guests to login", () => {
  assert.equal(legacyBeenRedirect({ username: "tan" }), "/u/tan");
  assert.equal(legacyBeenRedirect(null), "/login");
});
