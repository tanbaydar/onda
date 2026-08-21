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
  assert.match(list, /data: discover && page > 1 \? current\.data : null/);
  assert.doesNotMatch(list, />Load more</);
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

test("profile favorites separate entity types while keeping row-scale artwork and a heart-only owner control", () => {
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
  assert.match(css, /\.profile-favorite-list \.artist-avatar\{width:var\(--thumb\);height:var\(--thumb\)\}/);
  assert.match(css, /\.profile-favorite-link\{[^}]*min-height:var\(--thumb-h\)/);
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

test("sparse upcoming events keep one hierarchy and withhold a zero WBT numeral", () => {
  const eventPage = read("./pages/EventPage.jsx");
  const attendees = read("./components/WillBeThereAttendees.jsx");
  const css = read("./styles.css");
  assert.match(eventPage, /event-page-no-artwork/);
  assert.match(eventPage, /!isPast && wbtCount > 0 \? <div className="wbt-count">/);
  assert.match(eventPage, /activeCount=\{wbtCount\}/);
  assert.match(attendees, /"No active marks yet\."/);
  assert.match(attendees, /"No public marks are visible\."/);
  assert.match(css, /\.event-page-no-artwork>\.event-identity,\.event-page-no-artwork>section\{max-width:var\(--measure-prose\)\}/);
  assert.match(css, /\.event-page\.event-page-no-artwork>section\{margin-left:0\}/);
});

test("venue identity presents a natural location and omits operational geography", () => {
  const venue = read("./pages/VenuePage.jsx");
  assert.equal(formatVenueLocation({ name: "Boston", region_name: "Massachusetts", country_code: "US" }), "Boston, Massachusetts · United States");
  assert.equal(formatVenueLocation({ name: "Singapore", region_name: "Singapore", country_code: "SG" }), "Singapore");
  assert.match(venue, /className="venue-identity"/);
  assert.match(venue, /<FavoriteControl compact/);
  assert.doesNotMatch(venue, /<dl>|<dt>|timezone|City:/i);
});
