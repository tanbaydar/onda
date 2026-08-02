import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { artistPath, entityIdFromRoute, entityResultPath, entitySlug, eventPath, venuePath } from "./entityRoutes.js";
import { canonicalReplacement } from "./useCanonicalEntityRoute.js";

test("canonical entity paths use the slug-first ID-last contract", () => {
  assert.equal(eventPath({ id: 1687, title: "MMF Society: Open Decks" }), "/e/mmf-society-open-decks-1687");
  assert.equal(venuePath({ id: 42, name: "Nowadays" }), "/v/nowadays-42");
  assert.equal(artistPath({ id: 9, name: "Björk" }), "/a/bjork-9");
});

test("slug sanitization folds diacritics, symbols, length, and empty names", () => {
  assert.equal(entitySlug("  Héloïse & Øresund — B2B!  "), "heloise-oresund-b2b");
  assert.equal(entitySlug("🎉🪩"), "");
  assert.ok(entitySlug("word ".repeat(30)).length <= 60);
  assert.equal(eventPath({ id: 7, title: "🎉🪩" }), "/e/7");
});

test("route parsing uses only the trailing numeric segment", () => {
  assert.equal(entityIdFromRoute("current-name-301"), 301);
  assert.equal(entityIdFromRoute("301"), 301);
  assert.equal(entityIdFromRoute("301-stale"), null);
  assert.equal(entityIdFromRoute("name-no-id"), null);
});

test("all search entity links use the shared canonical builder", () => {
  assert.equal(entityResultPath("events", { id: 1, title: "One" }), "/e/one-1");
  assert.equal(entityResultPath("artists", { id: 2, name: "Two" }), "/a/two-2");
  assert.equal(entityResultPath("venues", { id: 3, name: "Three" }), "/v/three-3");
  assert.equal(entityResultPath("people", { username: "listener" }), "/u/listener");
});

test("App source retains legacy and canonical detail route declarations", () => {
  const app = readFileSync(new URL("./App.jsx", import.meta.url), "utf8");
  for (const path of ["/e/:eventKey", "/v/:venueKey", "/a/:artistKey", "/events/:eventKey", "/venues/:venueKey", "/artists/:artistKey"]) {
    assert.match(app, new RegExp(`path="${path.replaceAll("/", "\\/")}"`));
  }
});

test("bare, stale, and legacy paths replace while canonical paths remain", () => {
  const event = { id: 1687, title: "MMF Society Open Decks" };
  const canonical = "/e/mmf-society-open-decks-1687";
  assert.equal(canonicalReplacement("/e/1687", event, eventPath), canonical);
  assert.equal(canonicalReplacement("/e/old-name-1687", event, eventPath), canonical);
  assert.equal(canonicalReplacement("/events/1687", event, eventPath), canonical);
  assert.equal(canonicalReplacement(canonical, event, eventPath), null);
  assert.equal(canonicalReplacement("/e/7", { id: 7, title: "🎉" }, eventPath), null);
});

test("named internal-link source files contain no legacy entity path literals", () => {
  for (const file of [
    "./components/EventList.jsx", "./components/ProfileDiaryRow.jsx", "./components/SearchResults.jsx",
    "./homeFeedPresentation.js", "./pages/ActivityPage.jsx", "./pages/EventPage.jsx", "./pages/ProfilePage.jsx",
  ]) {
    const source = readFileSync(new URL(file, import.meta.url), "utf8");
    assert.doesNotMatch(source, /(?:to=|navigate\()[^\n]*(?:\/events\/|\/venues\/|\/artists\/)/);
  }
});
