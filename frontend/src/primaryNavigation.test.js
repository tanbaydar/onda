import assert from "node:assert/strict";
import test from "node:test";

import { primaryNavigationItems } from "./primaryNavigation.js";

test("signed-in primary navigation keeps the five-position text skeleton", () => {
  const items = primaryNavigationItems({ username: "listener" });
  assert.deepEqual(items.map(({ label }) => label), ["Home", "Discover", "Search", "Activity", "Profile"]);
  assert.equal(items[2].to, "/search");
});

test("Search remains a public primary destination", () => {
  const guestSearch = primaryNavigationItems(null).find(({ label }) => label === "Search");
  const signedInSearch = primaryNavigationItems({ username: "listener" }).find(({ label }) => label === "Search");
  assert.equal(guestSearch?.to, "/search");
  assert.equal(signedInSearch?.to, "/search");
});
