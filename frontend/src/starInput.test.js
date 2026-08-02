import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { keyboardStep, valueAtClientX } from "./starInputInteraction.js";

const stars = Array.from({ length: 5 }, (_, index) => ({ left: index * 50, right: index * 50 + 44 }));

test("every real-size star resolves its left and right halves at the boundary", () => {
  for (let index = 0; index < 5; index += 1) {
    assert.equal(valueAtClientX(stars[index].left, stars), index + 0.5);
    assert.equal(valueAtClientX(stars[index].left + 21.99, stars), index + 0.5);
    assert.equal(valueAtClientX(stars[index].left + 22, stars), index + 1);
    assert.equal(valueAtClientX(stars[index].right, stars), index + 1);
  }
  assert.equal(valueAtClientX(-20, stars), 0.5);
  assert.equal(valueAtClientX(300, stars), 5);
});

test("keyboard arrows retain half-star steps and clamp to the slider range", () => {
  assert.equal(keyboardStep(0, "ArrowLeft"), 0.5);
  assert.equal(keyboardStep(0.5, "ArrowRight"), 1);
  assert.equal(keyboardStep(3, "ArrowLeft"), 2.5);
  assert.equal(keyboardStep(5, "ArrowRight"), 5);
});

test("shared StarInput retains Enter commit and pointer capture interaction", () => {
  const source = readFileSync(new URL("./components/StarInput.jsx", import.meta.url), "utf8");
  assert.match(source, /event\.key === "Enter"/);
  assert.match(source, /onCommit\(numericValue\)/);
  assert.match(source, /setPointerCapture/);
  assert.match(source, /onPointerMove/);
  assert.match(source, /onPointerCancel/);
  assert.match(source, /role="slider"/);
});

test("the effective target remains 44px around each 32px glyph", () => {
  const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
  assert.match(css, /\.star-input-glyph\{[^}]*width:44px;height:44px;padding:var\(--sp-6\)[^}]*font-size:32px/);
});
