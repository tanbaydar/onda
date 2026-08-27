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
  assert.match(component, /aria-label=\{`Account menu for \$\{user\.display_name\}`\}/);
  assert.match(component, /<ProfileAvatar profile=\{user\} small \/>/);
  assert.doesNotMatch(component, /@\{user\.username\}/);
  assert.match(component, /role="menuitem" to="\/settings\/profile" onClick=\{\(\) => setOpen\(false\)\}/);
  assert.equal((component.match(/>Edit profile<\/Link>/g) ?? []).length, 1);
  assert.match(component, /logoutState\.pending \? "Logging out…" : "Log out"/);
  assert.equal((component.match(/role="menuitem"/g) ?? []).length, 2);
});

test("account trigger and panel use the governed avatar, target, and flat alignment grammar", () => {
  const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
  assert.match(css, /\.account-menu-trigger\{display:flex;width:44px;height:44px;align-items:center;justify-content:center;padding:var\(--sp-8\);border:0\}/);
  assert.match(css, /\.account-menu-panel\{position:absolute;top:calc\(100% \+ var\(--sp-12\)\);right:0;/);
  assert.match(css, /\.account-menu-panel\{[^}]*box-shadow:none;filter:none/);
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

test("App synchronizes the session avatar after profile changes", () => {
  const editProfile = readFileSync(new URL("./pages/EditProfilePage.jsx", import.meta.url), "utf8");
  assert.doesNotMatch(app, /accountProfile/);
  assert.match(app, /function handleProfileUpdated\(profile\)/);
  assert.match(app, /avatar: profile\.avatar/);
  assert.match(app, /<AccountMenu user=\{session\.user\}/);
  assert.match(app, /<EditProfilePage session=\{session\} onProfileUpdated=\{handleProfileUpdated\}/);
  assert.equal((editProfile.match(/onProfileUpdated\(data\.profile\)/g) ?? []).length, 3);
});
