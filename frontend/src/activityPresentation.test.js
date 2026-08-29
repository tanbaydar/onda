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
  assert.equal(activityNotificationVerb({ type: "will_be_there" }), "will be at");
  assert.equal(
    activityNotificationPath({ actor: { username: "dancer" }, event: { id: 42, title: "Open Air" } }),
    "/e/open-air-42",
  );
});

test("follow-request decisions use the existing endpoints in both Activity locations", () => {
  const activity = readFileSync(new URL("./pages/ActivityPage.jsx", import.meta.url), "utf8");
  const source = readFileSync(new URL("./components/ActivityFollowRequests.jsx", import.meta.url), "utf8");

  assert.ok(activity.indexOf("<ActivityFollowRequests") < activity.indexOf('<ol className="activity-list ledger-list">'));
  assert.match(source, /follow-requests\/\$\{userId\}\/\$\{action\}\//);
  assert.match(source, />Approve<\/button>/);
  assert.match(source, />Delete<\/button>/);
  assert.match(activity, /follow-requests\/\$\{notification\.actor\.id\}\/\$\{action\}\//);
  assert.match(activity, /className="activity-request-actions"/);
  assert.match(activity, />Approve<\/button>[\s\S]*>Delete<\/button>/);
  assert.doesNotMatch(source, /location\.(?:assign|reload)|window\.location/);
});
