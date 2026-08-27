import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("visual roles are explicit instead of inherited from product-wide tag selectors", () => {
  const css = read("./styles.css");
  assert.match(css, /\.identity-title\{/);
  assert.match(css, /\.functional-title\{/);
  assert.match(css, /\.section-heading\{/);
  assert.match(css, /\.ledger-list/);
  assert.match(css, /\.field-error-list/);
  assert.doesNotMatch(css, /h1,h3\{/);
  assert.doesNotMatch(css, /main (?:ol|ul)>li/);
  assert.doesNotMatch(css, /body:has\(main\.auth-page\)/);
});

test("target sizing is owned by named action roles rather than a selector inventory", () => {
  const css = read("./styles.css");
  assert.match(css, /\.navigation-action,\.account-action,\.menu-action,\.tab-action,\.recovery-action,\.pagination-action/);
  assert.match(css, /min-height:var\(--target-mobile\)/);
  assert.doesNotMatch(css, /\.city-dropdown-options button,\.discover-search-clear/);
});

test("approved constrained compositions are encoded at the system boundary", () => {
  const css = read("./styles.css");
  const search = read("./pages/SearchPage.jsx");
  assert.match(css, /--gutter-page:clamp/);
  assert.match(search, /className="search-scopes-rail"/);
  assert.match(search, /scrollIntoView\(\{ block: "nearest", inline: "nearest" \}\)/);
  assert.match(search, /search-scopes-cue\$\{scopeHasMore \? "" : " is-end"\}/);
  assert.match(css, /@media \(max-width:420px\)[\s\S]*\.star-input-wrap\{[^}]*flex-direction:column/);
});

test("initial, continuation, logout, and mutation feedback keep separate owners", () => {
  const app = read("./App.jsx");
  const home = read("./pages/HomePage.jsx");
  const activity = read("./pages/ActivityPage.jsx");
  assert.match(app, /logoutState/);
  assert.doesNotMatch(app, /setSession\(\(current\) => \(\{ \.\.\.current, error \}\)\)/);
  assert.match(home, /loadMoreError/);
  assert.match(activity, /actionError/);
  assert.match(activity, /read_at: notification\.read_at \?\? readAt/);
});

test("approved hierarchy and availability decisions are represented directly", () => {
  const event = read("./pages/EventPage.jsx");
  const publicReviews = read("./components/PublicReviews.jsx");
  const profile = read("./pages/ProfilePage.jsx");
  assert.ok(event.indexOf("<PublicReviews") < event.lastIndexOf("<EventLineup"));
  assert.match(event, /!isPast && !user \? <><WillBeThereAttendees eventId=\{event\.id\} scope="public"[\s\S]*scope="circle"/);
  assert.match(publicReviews, /state\.data\?\.results\.length \? <SortMenu/);
  assert.match(profile, /state\.data\?\.results\.length \? <div className="profile-review-sort"><SortMenu/);
});

test("the compact Discover result remains in the shared event presenter family", () => {
  const results = read("./components/SearchResults.jsx");
  assert.match(results, /<DiscoverEventRow[\s\S]*variant=\{compact \? "overlay" : "standard"\}/);
  assert.doesNotMatch(results, /function CompactEventResultRow/);
});
