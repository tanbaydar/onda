import assert from "node:assert/strict";
import test from "node:test";

import {
  REMEDIATION_ROUTE_CLASSES,
  REMEDIATION_STATE_FAMILIES,
  REMEDIATION_VIEWPORTS,
} from "./remediationAcceptance.js";

test("the system remediation freezes every R00-R17 route class", () => {
  assert.deepEqual(REMEDIATION_ROUTE_CLASSES.map(({ id }) => id), Array.from({ length: 18 }, (_, index) => `R${String(index).padStart(2, "0")}`));
  assert.equal(new Set(REMEDIATION_ROUTE_CLASSES.flatMap(({ routes }) => routes)).size, REMEDIATION_ROUTE_CLASSES.flatMap(({ routes }) => routes).length);
});

test("the mechanical viewport contract includes boundary and wide-desktop capacities", () => {
  assert.deepEqual(REMEDIATION_VIEWPORTS.map(({ width }) => width), [320, 390, 767, 768, 1280, 1440]);
});

test("the fixture contract retains every promised density, media, network, interaction, and enlargement family", () => {
  for (const family of ["empty", "sparse", "normal", "dense-extreme", "media-present", "media-absent", "media-failed", "initial-loading", "initial-error", "continuation-error", "mutation-error", "hover", "keyboard-focus", "selected", "disabled", "open-dismiss", "text-enlargement-200"]) {
    assert.ok(REMEDIATION_STATE_FAMILIES.includes(family), `${family} must remain in the remediation acceptance contract`);
  }
});
