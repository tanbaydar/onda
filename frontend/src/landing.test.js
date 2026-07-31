import assert from "node:assert/strict";
import test from "node:test";

import {
  AUTHENTICATED_LANDING,
  GUEST_DISCOVER,
  homeAccessRedirect,
  landingPath,
} from "./landing.js";


test("guests land on Discover and signed-in users land on Home", () => {
  assert.equal(landingPath(null), "/discover");
  assert.equal(landingPath({ id: 1 }), "/home");
});

test("auth success targets Home and direct guest Home access targets Discover", () => {
  assert.equal(AUTHENTICATED_LANDING, "/home");
  assert.equal(homeAccessRedirect(null), GUEST_DISCOVER);
  assert.equal(homeAccessRedirect({ id: 1 }), null);
});

test("legacy city links take precedence and preserve the city for every viewer", () => {
  assert.equal(landingPath(null, "?city_id=2"), "/discover?city_id=2");
  assert.equal(
    landingPath({ id: 1 }, "?city_id=999"),
    "/discover?city_id=999",
  );
});
