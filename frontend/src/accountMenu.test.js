import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const component = readFileSync(new URL("./components/AccountMenu.jsx", import.meta.url), "utf8");
const app = readFileSync(new URL("./App.jsx", import.meta.url), "utf8");

test("AccountMenu source wires disclosure, Escape, outside-click, and selection handlers", () => {
  assert.match(component, /aria-expanded=\{open\}/);
  assert.match(component, /setOpen\(\(current\) => !current\)/);
  assert.match(component, /event\.key === "Escape"/);
  assert.match(component, /!rootRef\.current\?\.contains\(event\.target\)/);
  assert.match(component, /role="menuitem" to="\/settings\/profile" onClick=\{\(\) => setOpen\(false\)\}/);
  assert.equal((component.match(/>Edit profile<\/Link>/g) ?? []).length, 1);
  assert.match(component, /logoutState\.pending \? "Logging out…" : "Log out"/);
  assert.equal((component.match(/role="menuitem"/g) ?? []).length, 2);
});

test("App source wires logout to the shipped endpoint, session clear, and guest destination", () => {
  assert.match(app, /fetchWithCsrf\("\/api\/auth\/logout\/"/);
  assert.match(app, /setSession\(\{ loading: false, error: null, user: null \}\)/);
  assert.match(app, /navigate\(GUEST_DISCOVER, \{ replace: true \}\)/);
});

test("App source gates AccountMenu to signed-in sessions and exposes guest auth links", () => {
  assert.match(app, /session\.user \? \(\s*<AccountMenu/);
  assert.doesNotMatch(component, /Register|Log in/);
  assert.match(app, /className="guest-register account-action" to="\/register">Register<\/Link>/);
  assert.match(app, /className="account-action" to="\/login">Log in<\/Link>/);
});
