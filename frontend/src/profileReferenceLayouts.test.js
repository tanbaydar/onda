import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("profile identity applies the governed Instagram-derived spacing without new product features", () => {
  const profile = read("./pages/ProfilePage.jsx");
  const css = read("./styles.css");

  assert.match(profile, /className="profile-header"[\s\S]*<ProfileAvatar[\s\S]*className="profile-identity-copy"[\s\S]*className="profile-header-action"/);
  assert.match(css, /\.profile-header\{[^}]*max-width:var\(--measure-rows\);[^}]*grid-template-columns:var\(--flier-sm\) minmax\(0,1fr\)/);
  assert.match(css, /@media \(min-width:768px\)[\s\S]*\.profile-header\{grid-template-columns:var\(--flier-md\) minmax\(0,1fr\)/);
  assert.match(css, /\.profile-header-action\{grid-column:1\/-1;width:100%\}/);
  assert.match(css, /\.profile-edit-link\{display:flex;width:100%/);
  assert.doesNotMatch(profile, /View archive|New story|Share photos/);
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
  assert.match(css, /\.profile-diary-row\{[^}]*grid-template-columns:var\(--flier-sm\) minmax\(0,1fr\)/);
  assert.match(css, /\.profile-diary-review\{[^}]*font-family:var\(--font-prose\)/);
});
