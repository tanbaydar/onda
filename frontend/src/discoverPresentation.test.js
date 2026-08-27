import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { compactLineup } from "./discoverPresentation.js";
import { formatCompactEventDateTime, formatEventIdentityDateTime } from "./formatEventDateTime.js";

const page = readFileSync(new URL("./pages/DiscoverPage.jsx", import.meta.url), "utf8");
const eventList = readFileSync(new URL("./components/EventList.jsx", import.meta.url), "utf8");
const eventRow = readFileSync(new URL("./components/EventRowPresenter.jsx", import.meta.url), "utf8");
const styles = readFileSync(new URL("./discover.css", import.meta.url), "utf8");

test("DiscoverPage uses the city as its successful identity and a functional initial-state title", () => {
  assert.match(page, /<h1 className="identity-title">\{selectedCity\.name\}<\/h1>/);
  assert.match(page, /<h1 className="functional-title">Discover<\/h1>/);
});

test("Discover lineup keeps listing order and collapses after two names", () => {
  const artists = [
    { id: 1, name: "System Failure" },
    { id: 2, name: "Echotheism" },
    { id: 3, name: "Third Artist" },
    { id: 4, name: "Fourth Artist" },
  ];
  assert.equal(compactLineup(artists), "System Failure, Echotheism +2");
  assert.equal(compactLineup(artists, 1), "Echotheism, Third Artist +1");
  assert.equal(compactLineup([], null), "");
});

test("EventRowPresenter uses compact dates and contains no prose labels", () => {
  assert.equal(formatCompactEventDateTime("2026-08-06", "22:00:00"), "Thu 6 Aug, 10:00 pm");
  assert.doesNotMatch(eventRow, /Venue:|Artists:/);
  assert.match(eventRow, /discover-event-row/);
  assert.match(eventList, /<EventRowPresenter/);
});

test("event identity date and time stay compact without dropping the year", () => {
  assert.equal(formatEventIdentityDateTime("2026-08-29", "22:00:00"), "Sat, Aug 29, 2026 · 10:00 PM");
  assert.equal(formatEventIdentityDateTime("2026-08-29", null), "Sat, Aug 29, 2026");
});

test("DiscoverPage and CSS sources contain the ruled tabs and two-line title register", () => {
  assert.match(page, /className="section-tabs"/);
  assert.match(styles, /\.discover-event-title\{[^}]*-webkit-line-clamp:2/);
  assert.match(styles, /\.discover-page>\.section-tabs/);
});

test("event rows keep the display title and use one existing information recipe", () => {
  const informationRule = styles.match(/\.discover-event-meta,\.discover-event-lineup\{[^}]+\}/)?.[0] ?? "";
  assert.match(styles, /\.discover-event-title\{[^}]*font-family:var\(--font-display\)/);
  assert.match(informationRule, /color:var\(--text-secondary\)/);
  assert.match(informationRule, /font-family:var\(--font-fn\)/);
  assert.match(informationRule, /font-size:var\(--text-ui\)/);
  assert.match(informationRule, /font-weight:400/);
  assert.match(styles, /\.discover-event-meta time\{color:inherit;font:inherit\}/);
  assert.doesNotMatch(styles, /\.discover-event-meta time\{[^}]*font-weight:500/);
  assert.doesNotMatch(styles, /\.discover-event-lineup\{[^}]*font-size:var\(--text-micro\)/);
});
