import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
const reviewStyles = readFileSync(new URL("./eventReviews.css", import.meta.url), "utf8");

test("event detail uses the compact Home-derived spacing register", () => {
  assert.match(styles, /\.event-page\{padding-top:var\(--sp-24\)\}/);
  assert.match(styles, /\.event-page>section,\.event-page>article\+section\{margin-top:var\(--sp-24\)\}/);
  assert.match(styles, /\.event-page \.event-lineup,\.event-page \.event-rating-block,\.event-page \.event-owner-block\{margin-top:var\(--sp-16\)\}/);
  assert.match(styles, /\.event-page \.event-rating-block\{width:max-content;max-width:100%;grid-template-columns:auto 120px;align-items:start\}/);
  assert.match(styles, /\.event-page \.event-rating-block>\.rating-histogram\{display:contents\}/);
  assert.match(styles, /\.event-page \.event-rating-block>\.rating-histogram>\[role=img\]\{grid-column:2;grid-row:1;align-self:center;width:120px\}/);
  assert.match(styles, /\.event-page \.event-rating-block>\.rating-histogram>\.rating-histogram-details\{grid-column:2;grid-row:2;margin-top:0\}/);
  assert.match(styles, /\.event-page \.event-rating-block>p:last-child\{grid-column:1;grid-row:2;align-self:start\}/);
  assert.match(styles, /\.event-page \.event-rating-block \.hist-bars\{height:26px\}/);
  assert.match(reviewStyles, /\.event-review-row\{padding:var\(--sp-12\) 0\}/);
});
