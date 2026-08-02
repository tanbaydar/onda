import assert from "node:assert/strict";
import test from "node:test";

import { eventIsPast } from "./eventTime.js";

const event = { event_date: "2026-08-01", start_time: "22:00:00", venue: { city: { timezone: "America/New_York" } } };

test("event owner state changes at the scheduled venue-local start", () => {
  assert.equal(eventIsPast(event, new Date("2026-08-02T01:59:00Z")), false);
  assert.equal(eventIsPast(event, new Date("2026-08-02T02:00:00Z")), true);
});
