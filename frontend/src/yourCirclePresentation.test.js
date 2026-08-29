import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("Your Circle average keeps a compact, text-only judgment hierarchy", () => {
  const component = read("./components/YourCircle.jsx");
  const css = read("./styles.css");

  assert.match(component, /className="circle-rating-summary"/);
  assert.match(component, /<strong className="circle-rating-score"/);
  assert.doesNotMatch(component, /RatingStars|circle-rating-stars|Including yours/);
  assert.match(component, /aria-label=\{`\$\{state\.data\.rating_summary\.average\.toFixed\(1\)\} average from/);
  assert.match(css, /\.circle-rating-score\{[^}]*color:var\(--judgment\)[^}]*font-family:var\(--font-display\)[^}]*font-size:var\(--text-numeral-md\)/);
  assert.doesNotMatch(css, /\.circle-rating-stars/);
  assert.doesNotMatch(css, /\.circle-rating-summary\{[^}]*(?:box-shadow|gradient|border-radius)/);
});
