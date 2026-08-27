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
  assert.match(css, /\.navigation-action\.navigation-action,\.account-action\.account-action,\.menu-action\.menu-action,\.tab-action\.tab-action,\.recovery-action\.recovery-action,\.pagination-action\.pagination-action/);
  assert.match(css, /min-height:var\(--target-mobile\)/);
  assert.doesNotMatch(css, /\.city-dropdown-options button,\.discover-search-clear/);
  assert.match(css, /\.event-list-error button\{min-height:0[^}]+\}[\s\S]*\.recovery-action\.recovery-action[^}]+min-height:var\(--target-min\)/);
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
  const reviewActions = read("./components/ReviewActionsMenu.jsx");
  const activity = read("./pages/ActivityPage.jsx");
  const editProfile = read("./pages/EditProfilePage.jsx");
  const publicReviews = read("./components/PublicReviews.jsx");
  const profile = read("./pages/ProfilePage.jsx");
  assert.ok(event.indexOf("<EventLineup") < event.indexOf("<PublicReviews"));
  assert.equal(event.indexOf("<EventLineup"), event.lastIndexOf("<EventLineup"));
  assert.match(reviewActions, />Edit review<\/button>[\s\S]*>Remove review<\/button>[\s\S]*>Remove from Been<\/button>/);
  assert.doesNotMatch(event, /Remove rating|removeRating/);
  assert.ok(activity.indexOf("<ActivityFollowRequests") < activity.indexOf('<ol className="activity-list ledger-list">'));
  assert.match(activity, /notification\.type === "follow_request"[\s\S]*className="activity-request-actions"/);
  assert.doesNotMatch(editProfile, /FollowRequests|Follow requests|follow-requests/);
  assert.match(event, /!isPast && !user \? <><WillBeThereAttendees eventId=\{event\.id\} scope="public"[\s\S]*scope="circle"/);
  assert.match(publicReviews, /state\.data\?\.results\.length \? <SortMenu/);
  assert.match(profile, /state\.data\?\.results\.length \? <div className="profile-review-sort"><SortMenu/);
  assert.match(profile, />Avg\. Rating<\/span>/);
  assert.match(profile, /reviewBody=\{review\.body\} likeCount=\{review\.like_count\}/);
});

test("all four governed event-row variants remain in one presenter family", () => {
  const results = read("./components/SearchResults.jsx");
  const profile = read("./pages/ProfilePage.jsx");
  const home = read("./pages/HomePage.jsx");
  const presenter = read("./components/EventRowPresenter.jsx");
  assert.match(results, /<EventRowPresenter[\s\S]*variant=\{compact \? "compact-overlay" : "standard-ledger"\}/);
  assert.match(profile, /<EventRowPresenter[^>]*variant="profile-diary"/);
  assert.match(home, /<EventRowPresenter variant="feed-object"/);
  for (const variant of ["standard-ledger", "compact-overlay", "profile-diary", "feed-object"]) assert.match(presenter, new RegExp(variant));
  assert.doesNotMatch(results, /function CompactEventResultRow/);
});
