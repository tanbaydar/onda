import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("App and CSS sources place session failure controls outside hidden header children", () => {
  const app = read("./App.jsx");
  const styles = read("./styles.css");
  assert.match(app, /<\/header>\s*\{session\.error \? \(\s*<div className="session-error-slot" role="alert">/);
  assert.match(styles, /\.session-error-slot\{[^}]*var\(--danger-text\)/);
});

test("ProfileAvatar and People-search sources use one null and failed-image fallback", () => {
  const avatar = read("./components/ProfileAvatar.jsx");
  const search = read("./components/SearchResults.jsx");
  assert.match(avatar, /onError=\{\(\) => setFailedSource\(profile\.avatar\)\}/);
  assert.match(avatar, /profileInitials\(profile\.display_name\)/);
  assert.match(search, /<ProfileAvatar profile=\{item\} small className="search-avatar"/);
});

test("ConfirmDialog source dispatches confirm and cancel only from onClose", () => {
  const dialog = read("./components/ConfirmDialog.jsx");
  assert.equal((dialog.match(/onConfirm\(\)/g) ?? []).length, 1);
  assert.equal((dialog.match(/onCancel\(\)/g) ?? []).length, 1);
  assert.match(dialog, /onClose=\{\(\) =>/);
  assert.match(dialog, /closingReason\.current = event\.nativeEvent\.submitter/);
});

test("CSS source reserves the action fill for destructive confirmation", () => {
  const styles = [read("./styles.css"), read("./discover.css"), read("./eventReviews.css")].join("\n");
  assert.equal((styles.match(/background(?:-color)?:var\(--action\)/g) ?? []).length, 1);
  assert.match(styles, /dialog \.destructive\{[^}]*background:var\(--action\)[^}]*color:var\(--bg\)/);
  assert.doesNotMatch(styles, /background(?:-color)?:#[0-9a-f]{3,8}/i);
});

test("event-list sources compose DiscoverEventRow and contain no labeled prose", () => {
  const list = read("./components/EventList.jsx");
  const row = read("./components/DiscoverEventRow.jsx");
  const search = read("./components/SearchResults.jsx");
  const artist = read("./pages/ArtistPage.jsx");
  const venue = read("./pages/VenuePage.jsx");
  assert.match(list, /<DiscoverEventRow/);
  assert.match(search, /<DiscoverEventRow/);
  assert.match(artist, /<EventList/);
  assert.match(venue, /<EventList/);
  assert.doesNotMatch(list + row, /Venue:|Artists:/);
});

test("profile and event-review sources compose the neutral SortMenu", () => {
  assert.match(read("./pages/ProfilePage.jsx"), /<SortMenu/);
  assert.match(read("./components/PublicReviews.jsx"), /<SortMenu/);
  assert.doesNotMatch(read("./styles.css") + read("./eventReviews.css"), /profile-sort-/);
});
