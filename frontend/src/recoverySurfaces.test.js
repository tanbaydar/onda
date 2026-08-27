import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");
const section = (source, start, end) => {
  const startIndex = source.indexOf(start);
  return source.slice(startIndex, source.indexOf(end, startIndex));
};

test("Search exposes an explicit clear action and separate retries for initial and paginated failures", () => {
  const source = read("./pages/SearchPage.jsx");
  const loadMore = section(source, "async function loadMore", "  return (");

  assert.match(source, /aria-label="Clear search" onClick=\{clearSearch\}/);
  assert.match(source, /function clearSearch\(\)[\s\S]*setQuery\(""\)[\s\S]*setState\(EMPTY_SEARCH_STATE\)[\s\S]*setLoadMoreError\(null\)/);
  assert.match(source, /Search could not be loaded\.[\s\S]*setRetry/);
  assert.match(source, /More results could not be loaded\.[\s\S]*onClick=\{loadMore\}/);
  assert.match(loadMore, /setLoadMoreError\(error\)/);
  assert.doesNotMatch(loadMore, /setState\(\(current\) => \(\{ \.\.\.current, error \}\)\)/);
});

test("Activity displays notifications even when mark-all-read bookkeeping fails", () => {
  const source = read("./pages/ActivityPage.jsx");
  const initialLoad = section(source, "useEffect(() =>", "  async function markAllRead");

  assert.doesNotMatch(initialLoad, /Promise\.all\([\s\S]*notifications\/read-all/);
  assert.ok(initialLoad.indexOf("results: data.results") < initialLoad.indexOf("markAllRead(controller.signal)"));
  assert.match(source, /Activity is visible, but it could not be marked as read\./);
  assert.match(source, /Retry marking as read/);
  assert.match(source, /follow-requests\/\?page_size=100/);
  assert.match(source, /decideRequest\(notification, "accept"\)/);
  assert.match(source, /decideRequest\(notification, "decline"\)/);
});

test("Profile follow failures stay local and preserve profile connections", () => {
  const source = read("./pages/ProfilePage.jsx");
  const changeFollow = section(source, "async function changeFollow", "  if (state.loading)");

  assert.match(changeFollow, /setFollowError\("The follow could not be changed\."\)/);
  assert.doesNotMatch(changeFollow, /setState\(/);
  assert.match(source, /className="profile-follow-error" role="alert"/);
  assert.match(source, /onClick=\{retryFollow\}/);
  assert.match(source, /<ProfileConnectionsDialog/);
});

test("Edit Profile initial-load failure has a working retry state", () => {
  const source = read("./pages/EditProfilePage.jsx");
  const errorBranch = source.indexOf("if (state.error)");
  const loadingBranch = source.indexOf("if (state.loading || !form)");

  assert.ok(errorBranch > -1 && errorBranch < loadingBranch);
  assert.match(source, /setLoadRetry\(\(value\) => value \+ 1\)/);
  assert.match(source, /\[loadRetry, session\.user\]/);
});

test("Event Lineup renders calm copy instead of an empty list", () => {
  const source = read("./pages/EventPage.jsx");

  assert.match(source, /artists\.length \? <ol className="inline-list">/);
  assert.match(source, /No lineup has been listed\./);
});
