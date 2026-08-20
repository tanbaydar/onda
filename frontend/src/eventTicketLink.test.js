import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { eventCanShowTicketLink } from "./eventTime.js";

const eventPage = readFileSync(
  new URL("./pages/EventPage.jsx", import.meta.url),
  "utf8",
);


const event = {
  event_date: "2026-08-10",
  is_ticketed: true,
  ticket_url: "https://ra.co/events/123",
  venue: { city: { timezone: "America/New_York" } },
};


test("ticket link visibility uses the event date in the venue timezone", () => {
  const lateNewYorkEvening = new Date("2026-08-11T03:30:00Z");
  assert.equal(eventCanShowTicketLink(event, lateNewYorkEvening), true);
  assert.equal(
    eventCanShowTicketLink(
      { ...event, event_date: "2026-08-11" },
      lateNewYorkEvening,
    ),
    true,
  );
  assert.equal(
    eventCanShowTicketLink(
      { ...event, event_date: "2026-08-09" },
      lateNewYorkEvening,
    ),
    false,
  );
});

test("event detail uses the ticket visibility helper and safe outbound link attributes", () => {
  assert.match(
    eventPage,
    /eventCanShowTicketLink\(event\)/,
  );
  assert.match(eventPage, />Get tickets<\/a>/);
  assert.match(eventPage, /target="_blank"/);
  assert.match(eventPage, /rel="noopener noreferrer"/);
});
