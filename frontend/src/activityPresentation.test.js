import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { activityNotificationPath, activityNotificationVerb, followRequestKey } from "./activityPresentation.js";


test("follow requests match their exact actor and request time", () => {
  const request = { user: { id: 7 }, created_at: "2026-08-21T08:00:00Z" };
  const currentNotification = { actor: { id: 7 }, created_at: "2026-08-21T08:00:00Z" };
  const historicalNotification = { actor: { id: 7 }, created_at: "2026-08-20T08:00:00Z" };

  assert.equal(followRequestKey(request), followRequestKey(currentNotification));
  assert.notEqual(followRequestKey(request), followRequestKey(historicalNotification));
});

test("activity copy and destinations preserve notification hierarchy", () => {
  assert.equal(activityNotificationVerb({ type: "follow_request" }), "requested to follow you.");
  assert.equal(
    activityNotificationPath({ actor: { username: "onda.listener" }, review: null }),
    "/u/onda.listener",
  );
  assert.equal(
    activityNotificationPath({ actor: { username: "critic" }, review: { event_id: 12, event_title: "Night Shift" } }),
    "/e/night-shift-12",
  );
});

test("follow-request decisions use the existing endpoints and stay in place", () => {
  const source = readFileSync(new URL("./pages/ActivityPage.jsx", import.meta.url), "utf8");

  assert.match(source, /follow-requests\/\$\{notification\.actor\.id\}\/\$\{action\}\//);
  assert.match(source, /setPendingRequestKeys/);
  assert.match(source, /result: action === "accept" \? "Approved" : "Deleted"/);
  assert.doesNotMatch(source, /location\.(?:assign|reload)|window\.location/);
});
