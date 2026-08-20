import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("the header wordmark is a router home link", () => {
  assert.match(read("./App.jsx"), /<Link className="site-wordmark" to="\/" aria-label="Onda home">/);
  assert.match(read("./App.jsx"), /<img src="\/logo.png" alt="Onda" \/>/);
});

test("entity search rows use browser-native router links", () => {
  const results = read("./components/SearchResults.jsx");
  assert.match(results, /<Link className="search-result-row" to=\{resultPath\(type, item\)\}/);
  assert.doesNotMatch(results, /navigate\(resultPath\(type, item\)\)/);
});

test("search scope and dynamic statuses expose accessible state", () => {
  const search = read("./pages/SearchPage.jsx");
  const styles = read("./styles.css");
  assert.match(search, /aria-pressed=\{scope === value\}/);
  assert.match(search, /className="search-status" role="status" aria-live="polite"/);
  assert.match(search, /className="search-empty" role="status" aria-live="polite"/);
  assert.match(styles, /\.search-result-row:focus-visible/);
  assert.match(styles, /\.search-scopes button:focus-visible/);
});

test("compact search exposes retryable failures without clearing the query", () => {
  const search = read("./components/DiscoverSearch.jsx");
  assert.match(search, /Search failed\. <button type="button" onClick=\{\(\) => setRetry/);
  assert.match(search, /\[cityId, retry, trimmed\]/);
  assert.doesNotMatch(search, /catch\(\(error\) => \{ if \(error\.name !== "AbortError"\) setData\(null\); \}\)/);
});
