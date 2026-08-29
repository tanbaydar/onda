import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("profile identity applies the governed Instagram-derived spacing without new product features", () => {
  const profile = read("./pages/ProfilePage.jsx");
  const css = read("./styles.css");

  assert.match(profile, /className="profile-header"[\s\S]*<ProfileAvatar[\s\S]*className="profile-identity-copy"[\s\S]*className="profile-bio"[\s\S]*className="profile-header-action"/);
  assert.match(profile, /className="identity-title"[\s\S]*className="profile-handle-line"[\s\S]*className="profile-social-counts"/);
  assert.match(css, /\.profile-header\{[^}]*max-width:var\(--measure-rows\);[^}]*grid-template-columns:var\(--profile-avatar-mobile\) minmax\(0,1fr\)/);
  assert.match(css, /@media \(min-width:768px\)[\s\S]*\.profile-header\{grid-template-columns:var\(--profile-avatar-desktop\) minmax\(0,1fr\)/);
  assert.match(css, /\.profile-header-action\{width:150px;grid-column:2;justify-self:start\}/);
  assert.match(css, /\.profile-header-action \.profile-follow-control\{width:150px;height:32px;min-height:32px/);
  assert.match(css, /\.profile-edit-link\{display:flex;width:150px;height:32px;min-height:32px/);
  assert.match(css, /\.profile-bio\{width:100%;max-width:none;grid-column:1\/-1;margin:0/);
  assert.doesNotMatch(profile, /View archive|New story|Share photos/);
});

test("mobile profile uses the compact Instagram-scale rhythm without changing desktop", () => {
  const tokens = read("../design-tokens.css");
  const css = read("./styles.css");

  assert.match(tokens, /--profile-avatar-mobile:80px; --profile-avatar-desktop:160px/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-header\{row-gap:var\(--sp-16\)\}/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-social-counts\{flex-wrap:nowrap;gap:var\(--sp-8\);margin-top:var\(--sp-4\)\}/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-social-counts>button\.mobile-target\{min-height:44px;[^}]*margin-bottom:-24px\}/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-statistics\{margin-top:var\(--sp-16\)\}/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-statistics-strip\{row-gap:var\(--sp-16\)\}/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-stat\.stat-lead \.stat-value\{font-size:var\(--text-numeral-md\)\}/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-tabs\{margin-top:var\(--sp-16\)\}/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-header-action\{width:100%;grid-column:1\/-1;justify-self:stretch\}/);
  assert.match(css, /@media \(max-width:767px\)\{[\s\S]*\.profile-header-action \.profile-follow-control,\.profile-header-action \.profile-edit-link\{width:100%;min-height:32px;border-color:var\(--judgment\);color:var\(--judgment\)\}/);
  assert.match(css, /@media \(min-width:768px\)[\s\S]*\.profile-header\{grid-template-columns:var\(--profile-avatar-desktop\)/);
});

test("profile diary applies the governed Letterboxd-derived placement and omits past start time", () => {
  const profile = read("./pages/ProfilePage.jsx");
  const presenter = read("./components/EventRowPresenter.jsx");
  const css = read("./styles.css");
  const diaryRow = presenter.slice(presenter.indexOf("function ProfileDiaryEventRow"), presenter.indexOf("function FeedEventRow"));

  for (const role of ["profile-diary-title-line", "profile-diary-year", "profile-diary-venue", "profile-diary-judgment", "profile-diary-review", "profile-diary-likes"]) {
    assert.match(diaryRow, new RegExp(role));
  }
  assert.match(diaryRow, /dateTime=\{event\.event_date\}/);
  assert.doesNotMatch(diaryRow, /event\.start_time/);
  assert.match(presenter, /const visibleStartTime = hasHappened\(event\) \? null : event\.start_time/);
  assert.match(profile, /reviewBody=\{review\.body\} likeCount=\{review\.like_count\}/);
  assert.match(profile, />Avg\. Rating<\/span>/);
  assert.match(css, /\.profile-diary-row\{[^}]*grid-template-columns:var\(--surface-flier\) minmax\(0,1fr\)/);
  assert.match(css, /\.profile-diary-review\{[^}]*font-family:var\(--font-prose\)/);
});
