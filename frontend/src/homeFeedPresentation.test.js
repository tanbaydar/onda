import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { compactRelativeTime, groupFeedItems, HOME_EMPTY_COPY, HOME_FEED_VERBS } from "./homeFeedPresentation.js";

const dense = JSON.parse(readFileSync(new URL("../design-fixtures/home-feed-dense.json", import.meta.url)));
const empty = JSON.parse(readFileSync(new URL("../design-fixtures/home-feed-empty.json", import.meta.url)));
const pageSource = readFileSync(new URL("./pages/HomePage.jsx", import.meta.url), "utf8");
const excerptSource = readFileSync(new URL("./components/FeedReviewExcerpt.jsx", import.meta.url), "utf8");
const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf8");

test("dense Home fixture renders all six feed activity types", () => {
  const types = [...new Set(dense.results.map(({ type }) => type))].sort();
  assert.deepEqual(types, Object.keys(HOME_FEED_VERBS).sort());
  for (const type of types) assert.match(pageSource, /HOME_FEED_VERBS\[item\.type\]/);
  assert.ok(dense.results.some(({ actor }) => actor.avatar === null));
  assert.ok(dense.results.some(({ target }) => target.event?.cover_image_url === null));
});

test("actor verbs survive name and object truncation", () => {
  assert.deepEqual(Object.values(HOME_FEED_VERBS), ["rated", "will be at", "followed", "liked a review of", "favorited", "favorited"]);
  assert.ok(dense.results.some(({ actor }) => actor.display_name.length > 35));
  assert.ok(dense.results.some(({ target }) => (target.event?.title ?? target.artist?.name ?? "").length > 60));
  assert.match(styles, /\.home-feed-verb\{[^}]*flex:none[^}]*white-space:nowrap/);
  assert.match(styles, /\.home-feed-actor-name,[^{]+\{[^}]*text-overflow:ellipsis/);
});

test("compact timestamps use the shared feed register", () => {
  const now = new Date("2026-08-02T12:00:00Z");
  assert.equal(compactRelativeTime("2026-08-02T11:42:00Z", now), "18m");
  assert.equal(compactRelativeTime("2026-08-01T18:00:00Z", now), "18h");
  assert.equal(compactRelativeTime("2026-07-31T12:00:00Z", now), "2d");
  assert.equal(compactRelativeTime("2026-07-12T12:00:00Z", now), "3w");
});

test("empty Home fixture uses one ruled line and one Discover affordance", () => {
  assert.deepEqual(empty.results, []);
  assert.equal(HOME_EMPTY_COPY, "No activity from people you follow yet.");
  assert.doesNotMatch(HOME_EMPTY_COPY, /\n/);
  assert.match(pageSource, /to="\/discover">Discover events<\/Link>/);
});

test("feed more is inline and only renders for measured truncation", () => {
  assert.match(excerptSource, /probe\.scrollHeight <= maxHeight/);
  assert.match(excerptSource, /rendered\.truncated \? <>… <small>more<\/small><\/> : null/);
  assert.doesNotMatch(styles, /\.home-feed-review small\{[^}]*position:/);
  assert.match(styles, /\.home-feed-review small\{display:inline/);
});

test("grouping applies only to one-liners and never rated or WBT rows", () => {
  const actor = { id: 1, username: "actor" };
  const make = (type, id) => ({ type, actor, activity_at: `2026-08-02T12:00:0${id}Z`, target: { event: { id, title: `${type} ${id}` } } });
  const results = groupFeedItems([make("favorite_event", 1), make("favorite_event", 2), make("rated_been", 3), make("rated_been", 4), make("will_be_there", 5), make("will_be_there", 6)]);
  assert.equal(results[0].grouped.length, 2);
  assert.equal(results.length, 5);
  assert.equal(results.filter((item) => item.grouped).length, 1);
});
