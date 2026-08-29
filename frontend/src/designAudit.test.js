import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { formatVenueLocation } from "./venuePresentation.js";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("guest navigation and account actions share one persistent chrome", () => {
  const app = read("./App.jsx");
  const css = read("./styles.css");
  assert.match(app, /<header className="site-header">/);
  assert.doesNotMatch(app + css, /auth-chrome/);
  assert.match(app, /primaryNavigationItems\(session\.user\)/);
  assert.match(app, /className="guest-auth-controls"/);
});

test("Discover advances through an observed sentinel and preserves loaded rows on failure", () => {
  const list = read("./components/EventList.jsx");
  assert.match(list, /new IntersectionObserver/);
  assert.match(list, /className="discover-scroll-sentinel" ref=\{loadMoreRef\}/);
  assert.match(list, /data: page > 1 \? current\.data : null/);
  assert.doesNotMatch(list, />Load more</);
  assert.match(list, /appendUniqueEvents\(current\.data\.results, data\.results\)/);
});

test("search focus is one inset border rather than a second outer rectangle", () => {
  const css = read("./styles.css");
  assert.match(css, /\.search-primary:focus-visible\{outline:none;box-shadow:inset/);
  assert.doesNotMatch(css, /\.search-primary:focus-visible\{[^}]*outline-offset/);
});

test("artist detail and search rows share a circular failed-image placeholder", () => {
  const avatar = read("./components/ArtistAvatar.jsx");
  const artist = read("./pages/ArtistPage.jsx");
  const profile = read("./pages/ProfilePage.jsx");
  const search = read("./components/SearchResults.jsx");
  const css = read("./styles.css");
  assert.match(avatar, /onError=\{\(\) => setFailedSource\(source\)\}/);
  assert.match(avatar, /artist-avatar-placeholder/);
  assert.match(artist, /<ArtistAvatar artist=\{artist\} loading="eager"/);
  assert.match(search, /<ArtistAvatar artist=\{item\} small/);
  assert.match(profile, /<ArtistAvatar artist=\{item\.artist\} small/);
  assert.match(css, /\.artist-avatar\{[^}]*border-radius:50%/);
});

test("profile favorites separate entity types into three-column flyer groups with a heart-only owner control", () => {
  const profile = read("./pages/ProfilePage.jsx");
  const favorite = read("./components/FavoriteControl.jsx");
  const css = read("./styles.css");
  assert.match(profile, /key: "events", label: "Events"/);
  assert.match(profile, /key: "artists", label: "Artists"/);
  assert.match(profile, /key: "venues", label: "Venues"/);
  assert.match(profile, /<ProfileFavoriteGroup key=\{group\.key\}/);
  assert.match(profile, /className="profile-favorite-link"/);
  assert.match(profile, /className="profile-favorite-copy"/);
  assert.match(favorite, /if \(row\) return <div className="profile-favorite-control">/);
  assert.match(css, /\.profile-favorite-groups\{display:grid;gap:var\(--sp-32\)\}/);
  assert.match(css, /\.profile-favorite-list\{display:grid;grid-template-columns:repeat\(3,minmax\(0,1fr\)\)/);
  assert.match(css, /\.profile-favorite-thumb\{[^}]*width:100%;aspect-ratio:4\/5/);
  assert.match(css, /\.profile-favorite-control\{position:absolute;top:0;right:0/);
});

test("profile social counts open a responsive, infinitely scrolling people list", () => {
  const profile = read("./pages/ProfilePage.jsx");
  const connections = read("./components/ProfileConnectionsDialog.jsx");
  const css = read("./styles.css");
  assert.match(profile, /setConnections\("followers"\)/);
  assert.match(profile, /setConnections\("following"\)/);
  assert.match(connections, /<dialog/);
  assert.match(connections, /new IntersectionObserver/);
  assert.match(connections, /\/\$\{kind\}\/\?page=1/);
  assert.match(connections, /<ProfileAvatar profile=\{person\} small/);
  assert.match(css, /\.profile-connections-dialog\{width:100%;max-width:none;height:100dvh/);
  assert.match(css, /@media \(min-width:768px\)[\s\S]*\.profile-connections-dialog\{width:min\(calc\(100% - 48px\),480px\)/);
});

test("one-page detail collections do not render inert pagination chrome", () => {
  assert.match(read("./components/EventList.jsx"), /pagination\.total_pages > 1 \? <nav/);
  assert.match(read("./components/PublicReviews.jsx"), /pagination\.total_pages > 1 \? <nav/);
  assert.match(read("./components/WillBeThereAttendees.jsx"), /pagination\.total_pages > 1 \? <nav/);
  assert.match(read("./pages/ProfilePage.jsx"), /if \(pagination\.total_pages <= 1\) return null/);
});

test("event attendee lists use the shared profile-row identity grammar", () => {
  const attendees = read("./components/WillBeThereAttendees.jsx");
  assert.match(attendees, /<ProfileAvatar profile=\{attendee\.user\} small/);
  assert.match(attendees, /className="event-attendee-row"/);
});

test("sparse upcoming events keep one standardized artwork hierarchy, withhold a zero WBT numeral, and omit Favorite", () => {
  const eventPage = read("./pages/EventPage.jsx");
  const attendees = read("./components/WillBeThereAttendees.jsx");
  const css = read("./styles.css");
  assert.match(eventPage, /<main className="event-page has-event-art">/);
  assert.match(eventPage, /<ImageSlot name=\{event\.title\} src=\{event\.cover_image_url\}/);
  assert.match(eventPage, /<div className="event-attendance">/);
  assert.match(eventPage, /wbtCount > 0 \? <p className="wbt-count">/);
  assert.equal((eventPage.match(/<FavoriteControl compact/g) ?? []).length, 1);
  assert.match(eventPage, /wbt-action/);
  assert.match(eventPage, /: "Will Be There"/);
  assert.match(eventPage, /activeCount=\{wbtCount\}/);
  assert.match(attendees, /"No active marks yet\."/);
  assert.match(attendees, /"No public marks are visible\."/);
  assert.doesNotMatch(eventPage, /event-page-no-artwork/);
});

test("event lineup gives every artist one subordinate functional-text treatment", () => {
  const css = read("./styles.css");
  assert.match(css, /\.event-lineup-title\{[^}]*font-size:var\(--text-ui\);font-weight:600/);
  assert.match(css, /\.event-lineup a\{[^}]*color:var\(--text-secondary\);font-family:var\(--font-fn\);font-size:var\(--text-ui\);font-weight:400/);
  assert.doesNotMatch(css, /\.event-lineup li:first-child/);
});

test("event identity uses one information recipe and keeps the attendance decision green", () => {
  const eventPage = read("./pages/EventPage.jsx");
  const css = read("./styles.css");
  assert.match(eventPage, /className="event-location-line"/);
  assert.match(eventPage, /formatEventIdentityDateTime/);
  assert.match(eventPage, /isPast \? <p>[\s\S]*dateTime=\{event\.event_date\}[\s\S]*formatEventIdentityDateTime\(event\.event_date, null\)/);
  assert.match(css, /\.event-meta-stack\{[^}]*color:var\(--text-secondary\);[^}]*font-size:var\(--text-ui\);font-weight:400/);
  assert.doesNotMatch(css, /\.wbt-count>span|\.wbt-count p/);
  assert.match(eventPage, /wbt-action\$\{event\.viewer_will_be_there\.is_marked \? " is-marked" : ""\}/);
  assert.match(css, /\.event-owner-block>button\.wbt-action\{border-color:var\(--judgment\);color:var\(--judgment\)\}/);
});

test("venue identity presents a natural location and omits operational geography", () => {
  const venue = read("./pages/VenuePage.jsx");
  assert.equal(formatVenueLocation({ name: "Boston", region_name: "Massachusetts", country_code: "US" }), "Boston, Massachusetts · United States");
  assert.equal(formatVenueLocation({ name: "Singapore", region_name: "Singapore", country_code: "SG" }), "Singapore");
  assert.match(venue, /className="venue-identity"/);
  assert.match(venue, /<FavoriteControl compact/);
  assert.doesNotMatch(venue, /<dl>|<dt>|timezone|City:/i);
});
