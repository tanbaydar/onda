import assert from "node:assert/strict";
import test from "node:test";

import {
  AUTHENTICATED_LANDING,
  GUEST_DISCOVER,
  homeAccessRedirect,
  landingPath,
  landingPathForSession,
  postAuthDestination,
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

test("auth routing sends only flag-on unverified payloads to email verification", () => {
  assert.equal(postAuthDestination({ id: 1 }), "/home");
  assert.equal(postAuthDestination({ id: 1, email_verified: true }), "/home");
  assert.equal(postAuthDestination({ id: 1, email_verified: false }), "/verify-email");
});

test("legacy city links take precedence and preserve the city for every viewer", () => {
  assert.equal(landingPath(null, "?city_id=2"), "/discover?city_id=2");
  assert.equal(
    landingPath({ id: 1 }, "?city_id=999"),
    "/discover?city_id=999",
  );
});

test("a failed session lookup falls back to public Discover instead of blocking browsing", () => {
  assert.equal(landingPathForSession({ loading: true, user: null }), null);
  assert.equal(
    landingPathForSession({ loading: false, error: new Error("offline"), user: null }),
    GUEST_DISCOVER,
  );
  assert.equal(
    landingPathForSession(
      { loading: false, error: new Error("offline"), user: null },
      "?city_id=2",
    ),
    "/discover?city_id=2",
  );
});
