import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
const reviewStyles = readFileSync(new URL("./eventReviews.css", import.meta.url), "utf8");
const eventPage = readFileSync(new URL("./pages/EventPage.jsx", import.meta.url), "utf8");

test("event detail uses the compact Home-derived spacing register", () => {
  assert.match(styles, /\.event-page\{padding-top:var\(--sp-24\)\}/);
  assert.match(styles, /\.event-page>section,\.event-page>article\+section\{margin-top:var\(--sp-24\)\}/);
  assert.match(styles, /\.event-page \.event-lineup,\.event-page \.event-rating-block,\.event-page \.event-owner-block\{margin-top:var\(--sp-16\)\}/);
  assert.match(styles, /\.event-page \.event-rating-block\{width:max-content;max-width:100%;grid-template-columns:auto 120px;align-items:end;column-gap:var\(--sp-32\)\}/);
  assert.match(styles, /\.event-page \.event-rating-block \.rating-histogram\{width:120px\}/);
  assert.match(styles, /\.event-page \.event-rating-block \.hist-bars\{height:26px\}/);
  assert.match(styles, /\.event-rating-block>\.event-rating-label,\.event-rating-block>\.event-rating-empty\{margin:0;color:var\(--text-secondary\);font-size:var\(--text-micro\)\}/);
  assert.match(eventPage, /<p className="event-rating-label">Avg\. Rating<\/p><p className="event-rating-label">rating distribution<\/p>/);
  assert.doesNotMatch(eventPage, /Average from \$\{pluralize/);
  assert.match(reviewStyles, /\.event-review-row\{padding:var\(--sp-12\) 0\}/);
});
