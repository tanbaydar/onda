import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("Your Circle average has a distinct judgment hierarchy", () => {
  const component = read("./components/YourCircle.jsx");
  const css = read("./styles.css");

  assert.match(component, /className="circle-rating-summary"/);
  assert.match(component, /className="circle-rating-score"/);
  assert.match(component, /<RatingStars className="circle-rating-stars"/);
  assert.match(component, /aria-label=\{`\$\{state\.data\.rating_summary\.average\.toFixed\(1\)\} average from/);
  assert.match(css, /\.circle-rating-score strong\{[^}]*color:var\(--judgment\)[^}]*font-family:var\(--font-display\)[^}]*font-size:var\(--text-numeral-lg\)/);
  assert.doesNotMatch(css, /\.circle-rating-summary\{[^}]*(?:box-shadow|gradient|border-radius)/);
});
