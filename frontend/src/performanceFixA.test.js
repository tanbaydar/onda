import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("Discover source renders one active ledger and retains separate ledger state", () => {
  const page = read("./pages/DiscoverPage.jsx");
  const list = read("./components/EventList.jsx");
  assert.match(page, /useState\(\{ upcoming: emptyLedger\(\), recent: emptyLedger\(\) \}\)/);
  assert.match(page, /view === "upcoming" \? <EventList/);
  assert.match(page, /ledger=\{ledgers\.upcoming\}/);
  assert.match(page, /ledger=\{ledgers\.recent\}/);
  assert.doesNotMatch(page, /hidden=\{/);
  assert.match(list, /ledger\?\.requestKey === requestKey/);
  assert.match(list, /results: \[\.\.\.current\.data\.results, \.\.\.data\.results\]/);
});

test("viewer-sensitive route sources wait for session resolution", () => {
  const app = read("./App.jsx");
  assert.equal((app.match(/sessionReady=\{!session\.loading\}/g) ?? []).length, 6);
  for (const path of ["./pages/EventPage.jsx", "./pages/ArtistPage.jsx", "./pages/VenuePage.jsx"]) {
    assert.match(read(path), /if \(!sessionReady\) return/);
  }
  assert.match(read("./pages/ProfilePage.jsx"), /if \(session\.loading\) return/);
});

test("shared thumbnails are lazy while identity imagery is explicitly eager", () => {
  const imageSlot = read("./components/ImageSlot.jsx");
  const avatar = read("./components/ProfileAvatar.jsx");
  assert.match(imageSlot, /loading = "lazy"/);
  assert.match(imageSlot, /loading=\{loading\}/);
  assert.match(avatar, /loading=\{small \? "lazy" : "eager"\}/);
  assert.match(read("./pages/EventPage.jsx"), /loading="eager"/);
  assert.match(read("./pages/ArtistPage.jsx"), /loading="eager"/);
});
