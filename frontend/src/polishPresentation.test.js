import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { imageSlotInitial, recentRatingVisible } from "./polishPresentation.js";

test("placeholder initials preserve the first rendered character", () => {
  assert.equal(imageSlotInitial("  basement"), "B");
  assert.equal(imageSlotInitial("7th Heaven"), "7");
  assert.equal(imageSlotInitial("#Afterhours"), "#");
});

test("Discover Recent judgment renders only at the three-rating gate", () => {
  assert.equal(recentRatingVisible({ state: "not_enough_ratings", count: 2 }), false);
  assert.equal(recentRatingVisible({ state: "available", count: 3, average: 4 }), true);
});

test("named surface sources compose the shared image, heart, and rating-star implementations", () => {
  const presenter = readFileSync(new URL("./components/EventRowPresenter.jsx", import.meta.url), "utf8");
  assert.match(presenter, /ImageSlot/);
  for (const path of ["components/SearchResults.jsx", "pages/HomePage.jsx", "pages/ProfilePage.jsx"]) {
    assert.match(readFileSync(new URL(path, import.meta.url), "utf8"), /EventRowPresenter/);
  }
  assert.match(readFileSync(new URL("./pages/EventPage.jsx", import.meta.url), "utf8"), /ImageSlot/);
  const favorite = readFileSync(new URL("./components/FavoriteControl.jsx", import.meta.url), "utf8");
  assert.match(favorite, /\/assets\/favorite-heart\.svg/); assert.match(favorite, /\/assets\/favorite-heart-filled\.svg/); assert.match(favorite, /favorite-heart-row/);
  assert.match(favorite, /setTimeout\(\(\) => setFilled\(false\), 120\)/);
});

test("ImageSlot source wires failed-source fallback", () => {
  const source = readFileSync(new URL("./components/ImageSlot.jsx", import.meta.url), "utf8");
  assert.match(source, /onError=.*setFailedSource/);
  assert.match(source, /failedSource !== src/);
});
