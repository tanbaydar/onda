import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";


const read = (relativePath) => readFileSync(new URL(relativePath, import.meta.url), "utf8");


test("follow changes keep the loaded profile mounted until silent reconciliation finishes", () => {
  const profile = read("./pages/ProfilePage.jsx");
  const follow = read("./components/FollowControl.jsx");

  assert.match(profile, /current\.data\?\.profile\.username === username[\s\S]*\.\.\.current, loading: false, error: null/);
  assert.match(profile, /<FollowControl relationship=\{data\.relationship\} pending=\{followPending\}/);
  assert.match(follow, /disabled=\{pending\} aria-busy=\{pending\}/);
  assert.doesNotMatch(profile.match(/async function changeFollow\(\)[\s\S]*?\n  }\n\n  if \(state\.loading\)/)?.[0] ?? "", /setState/);
});


test("favorites commit locally and owner removals delete only the changed row", () => {
  const favorite = read("./components/FavoriteControl.jsx");
  const profile = read("./pages/ProfilePage.jsx");
  const detailPages = ["ArtistPage.jsx", "VenuePage.jsx", "EventPage.jsx"].map((name) => read(`./pages/${name}`));

  assert.match(favorite, /setFavorite\(nextFavorite\);[\s\S]*onChanged\(nextFavorite\)/);
  assert.match(profile, /filter\(\(favorite\) => favorite\[entityKey\]\.id !== item\.id\)/);
  for (const page of detailPages) assert.match(page, /viewer_favorite: nextFavorite/);
});


test("social collections retain rendered data while they reconcile in the background", () => {
  const sources = [
    read("./components/PublicReviews.jsx"),
    read("./components/YourCircle.jsx"),
    read("./components/WillBeThereAttendees.jsx"),
    read("./components/ActivityFollowRequests.jsx"),
  ];

  for (const source of sources.slice(0, 3)) {
    assert.match(source, /current\.data[\s\S]*\.\.\.current, loading: false, error: null/);
  }
  assert.match(sources[3], /current\.data[\s\S]*\.\.\.current, loading: true, error: null/);
  assert.match(sources[0], /viewer_has_liked: adding, like_count: nextLikeCount/);
  assert.match(sources[1], /viewer_has_liked: adding, like_count: nextLikeCount/);
  assert.match(sources[3], /filter\(\(request\) => request\.user\.id !== userId\)/);
});


test("event mutations preserve the event shell and update Will Be There in place", () => {
  const event = read("./pages/EventPage.jsx");

  assert.match(event, /current\.event\?\.id === eventId[\s\S]*\.\.\.current, loading: false, error: null/);
  assert.match(event, /is_marked: marking,[\s\S]*was_marked: marking/);
  assert.match(event, /active_count: Math\.max\(0,[\s\S]*\+ \(marking \? 1 : -1\)\)/);
});


test("owner review deletion from Been updates only the affected row", () => {
  const profile = read("./pages/ProfilePage.jsx");
  const row = read("./components/EventRowPresenter.jsx");

  assert.match(profile, /\/been\/review\/`, \{ method: "DELETE" \}/);
  assert.match(profile, /entry\.event\.id === event\.id \? \{ \.\.\.entry, has_review: false \}/);
  assert.match(profile, /owner && entry\.has_review \? \(\) => setReviewToDelete/);
  assert.match(row, />Delete review<\/button>/);
});
