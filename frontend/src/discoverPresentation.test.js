import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { compactLineup } from "./discoverPresentation.js";
import { formatCompactEventDateTime } from "./formatEventDateTime.js";

const page = readFileSync(new URL("./pages/DiscoverPage.jsx", import.meta.url), "utf8");
const eventList = readFileSync(new URL("./components/EventList.jsx", import.meta.url), "utf8");
const styles = readFileSync(new URL("./discover.css", import.meta.url), "utf8");

test("Discover title is the selected city and the old heading is absent", () => {
  assert.match(page, /<h1>\{selectedCity\.name\}<\/h1>/);
  assert.doesNotMatch(page, /<h1>Discover<\/h1>/);
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

test("Discover rows use compact dates and contain no prose labels", () => {
  assert.equal(formatCompactEventDateTime("2026-08-06", "22:00:00"), "Thu 6 Aug, 10:00 pm");
  const branchStart = eventList.indexOf("if (discover)");
  const branch = eventList.slice(branchStart, eventList.indexOf("\n  return (", branchStart));
  assert.doesNotMatch(branch, /Venue:|Artists:/);
  assert.match(eventList, /discover-event-row/);
});

test("Discover uses the ruled tab and two-line title registers", () => {
  assert.match(page, /className="section-tabs"/);
  assert.match(styles, /\.discover-event-title\{[^}]*-webkit-line-clamp:2/);
  assert.match(styles, /\.discover-page>\.section-tabs/);
});
