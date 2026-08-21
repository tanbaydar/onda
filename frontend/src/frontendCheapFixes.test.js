import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("document chrome uses the onda title and favicon", () => {
  const html = read("../index.html");
  assert.match(html, /<title>onda<\/title>/);
  assert.match(html, /rel="icon"[^>]+href="\/favicon\.png"/);
  assert.match(html, /rel="shortcut icon"[^>]+href="\/favicon\.png"/);
});

test("the header wordmark is a router home link", () => {
  assert.match(read("./App.jsx"), /<Link className="site-wordmark" to="\/" aria-label="Onda home">/);
  assert.match(read("./App.jsx"), /<img src="\/logo.png" alt="Onda" \/>/);
});

test("mobile chrome reserves a fixed top bar without an invalid nested has selector", () => {
  const css = read("./styles.css");
  assert.match(css, /header>section:has\(\.guest-auth-controls\).*position:fixed/);
  assert.match(css, /body>div\{[^}]*padding-top:var\(--sp-64\)/);
  assert.match(css, /header>\.site-wordmark\{[^}]*position:fixed/);
  assert.doesNotMatch(css, /:has\([^)]*:has\(/);
  assert.match(css, /@media \(min-width:768px\)[\s\S]*header>section:has\(\.guest-auth-controls\).*position:static/);
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
  assert.match(search, /\[cityId, retry, searchReady, trimmed\]/);
  assert.doesNotMatch(search, /catch\(\(error\) => \{ if \(error\.name !== "AbortError"\) setData\(null\); \}\)/);
});

test("both search surfaces use the ruled minimum and Onda brand", () => {
  const page = read("./pages/SearchPage.jsx");
  const discover = read("./components/DiscoverSearch.jsx");
  assert.match(page, /const searchReady = searchQueryReady\(trimmed\)/);
  assert.match(discover, /const searchReady = searchQueryReady\(trimmed\)/);
  assert.match(page, /aria-label="Search Onda"/);
  assert.doesNotMatch(page, /Search Danced/);
});

test("profile statistics and empty favorites follow their ruled data gates", () => {
  const profile = read("./pages/ProfilePage.jsx");
  assert.match(profile, /profileRatingHistogramVisible\(distribution\)/);
  assert.match(profile, /showRatingHistogram \? <RatingHistogram/);
  assert.match(profile, /if \(items\.length === 0\) return null/);
});

test("edit fields expose validation ownership and one-page requests omit pagination", () => {
  const editor = read("./pages/EditProfilePage.jsx");
  const city = read("./components/CityDropdown.jsx");
  assert.match(editor, /aria-invalid=\{Boolean\(errors\.display_name\)\}/);
  assert.match(editor, /aria-describedby=\{errors\.bio/);
  assert.match(editor, /invalid=\{Boolean\(errors\.home_city_id\)\}/);
  assert.match(editor, /aria-invalid=\{Boolean\(errors\.is_private\)\}/);
  assert.match(editor, /if \(pagination\.total_pages <= 1\) return null/);
  assert.match(city, /aria-describedby=\{describedBy\} aria-invalid=\{invalid \|\| undefined\}/);
});

test("async screen states expose busy, status, and alert semantics", () => {
  for (const path of ["./pages/DiscoverPage.jsx", "./pages/HomePage.jsx", "./pages/ActivityPage.jsx"]) {
    const source = read(path);
    assert.match(source, /aria-busy=\{state\.loading\}/, path);
    assert.match(source, /role="status" aria-live="polite"/, path);
    assert.match(source, /role="alert"/, path);
  }
});

test("event action failures and custom controls use their established visible registers", () => {
  const styles = read("./styles.css");
  for (const path of ["./pages/EventPage.jsx", "./components/PublicReviews.jsx", "./components/YourCircle.jsx"]) {
    assert.match(read(path), /className="favorite-notice" role="alert"/, path);
  }
  assert.match(styles, /\.avatar-upload-control:focus-within\{outline:2px solid var\(--action\)/);
  assert.match(styles, /dialog \.destructive:focus-visible\{outline:2px solid var\(--action\)/);
});
