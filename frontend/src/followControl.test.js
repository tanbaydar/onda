import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { FOLLOW_CONTROL_LABELS, followControlLabel } from "./followControl.js";

test("follow control exposes all four ruled states through one label path", () => {
  assert.deepEqual(FOLLOW_CONTROL_LABELS, ["Follow", "Unfollow", "Request to follow", "Requested"]);
  assert.equal(followControlLabel({ outgoing_status: null, follow_action: "follow" }), "Follow");
  assert.equal(followControlLabel({ outgoing_status: "approved", follow_action: null }), "Unfollow");
  assert.equal(followControlLabel({ outgoing_status: null, follow_action: "request" }), "Request to follow");
  assert.equal(followControlLabel({ outgoing_status: "pending", follow_action: null }), "Requested");
});

test("all follow states share the same fixed control dimensions", () => {
  const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
  const rule = css.match(/\.profile-follow-control\{([^}]+)\}/)?.[1] ?? "";
  assert.match(rule, /min-width:150px/);
  assert.match(rule, /height:32px/);
  assert.match(rule, /min-height:32px/);
  assert.match(rule, /text-align:center/);
});
