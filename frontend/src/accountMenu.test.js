import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const component = readFileSync(new URL("./components/AccountMenu.jsx", import.meta.url), "utf8");
const app = readFileSync(new URL("./App.jsx", import.meta.url), "utf8");

test("account menu opens from the username and closes by selection, Escape, or outside click", () => {
  assert.match(component, /aria-expanded=\{open\}/);
  assert.match(component, /setOpen\(\(current\) => !current\)/);
  assert.match(component, /event\.key === "Escape"/);
  assert.match(component, /!rootRef\.current\?\.contains\(event\.target\)/);
  assert.match(component, /to="\/settings\/profile" onClick=\{\(\) => setOpen\(false\)\}/);
  assert.equal((component.match(/>Edit profile<\/Link>/g) ?? []).length, 1);
  assert.equal((component.match(/>Log out<\/button>/g) ?? []).length, 1);
  assert.equal((component.match(/role="menuitem"/g) ?? []).length, 2);
});

test("logout uses the shipped endpoint, clears session, and lands on guest Discover", () => {
  assert.match(app, /fetchWithCsrf\("\/api\/auth\/logout\/"/);
  assert.match(app, /setSession\(\{ loading: false, error: null, user: null \}\)/);
  assert.match(app, /navigate\(GUEST_DISCOVER, \{ replace: true \}\)/);
});

test("guest header has no account menu", () => {
  assert.match(app, /session\.user \? \(\s*<AccountMenu/);
  assert.doesNotMatch(component, /Register|Log in/);
});
