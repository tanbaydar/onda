import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { compactRelativeTime, groupFeedItems, homeFeedVerb, HOME_EMPTY_COPY, HOME_FEED_VERBS } from "./homeFeedPresentation.js";

const dense = JSON.parse(readFileSync(new URL("../design-fixtures/home-feed-dense.json", import.meta.url)));
const empty = JSON.parse(readFileSync(new URL("../design-fixtures/home-feed-empty.json", import.meta.url)));
const pageSource = readFileSync(new URL("./pages/HomePage.jsx", import.meta.url), "utf8");
const presenterSource = readFileSync(new URL("./components/EventRowPresenter.jsx", import.meta.url), "utf8");
const excerptSource = readFileSync(new URL("./components/FeedReviewExcerpt.jsx", import.meta.url), "utf8");
const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf8");

test("dense Home fixture and HomePage source cover the seven supported activity types", () => {
  const types = [...new Set(dense.results.map(({ type }) => type))].sort();
  assert.deepEqual(types, Object.keys(HOME_FEED_VERBS).sort());
  assert.match(pageSource, /homeFeedVerb\(item\)/);
  assert.ok(dense.results.some(({ actor }) => actor.avatar === null));
  assert.ok(dense.results.some(({ target }) => target.event?.cover_image_url === null));
});

test("Home feed identity metadata uses one functional-font line with bold actors and objects", () => {
  assert.deepEqual(Object.values(HOME_FEED_VERBS), ["has been to", "rated", "reviewed", "will be at", "liked a review from", "favorited", "favorited"]);
  assert.ok(dense.results.some(({ actor }) => actor.display_name.length > 35));
  assert.ok(dense.results.some(({ target }) => (target.event?.title ?? target.artist?.name ?? "").length > 60));
  assert.match(styles, /\.home-feed-verb\{[^}]*flex:none[^}]*white-space:nowrap/);
  assert.match(styles, /\.home-feed-actor-name\{[^}]*text-overflow:ellipsis/);
  assert.match(styles, /\.home-feed-actor-line\{[^}]*font-family:var\(--font-fn\)[^}]*font-size:var\(--text-ui\)/);
  assert.match(styles, /\.home-feed-object\{[^}]*flex:1 1 auto[^}]*font:inherit[^}]*font-weight:600/);
  assert.match(styles, /\.home-feed-actor-line time\{[^}]*font:inherit/);
  assert.match(presenterSource, /home-feed-verb[\s\S]{0,300}home-feed-object[\s\S]{0,300}<time/);
  assert.match(pageSource, /home-feed-verb[\s\S]{0,300}home-feed-object[\s\S]{0,300}<time/);
});

test("Been, rated, and reviewed states are presented as one diary activity each", () => {
  const reviewed = dense.results.find((item) => item.type === "review" && item.context?.review);
  assert.ok(reviewed);
  assert.equal(homeFeedVerb(reviewed), "reviewed");
  assert.equal(
    dense.results.filter((item) => item.target.event?.id === reviewed.target.event.id && ["been", "rated_been", "review"].includes(item.type)).length,
    1,
  );
  assert.equal(HOME_FEED_VERBS.been, "has been to");
  assert.equal(HOME_FEED_VERBS.rated_been, "rated");
  assert.equal(HOME_FEED_VERBS.review, "reviewed");
  assert.equal(HOME_FEED_VERBS.review_like, "liked a review from");
});

test("compact timestamps use the shared feed register", () => {
  const now = new Date("2026-08-02T12:00:00Z");
  assert.equal(compactRelativeTime("2026-08-02T11:42:00Z", now), "18m");
  assert.equal(compactRelativeTime("2026-08-01T18:00:00Z", now), "18h");
  assert.equal(compactRelativeTime("2026-07-31T12:00:00Z", now), "2d");
  assert.equal(compactRelativeTime("2026-07-12T12:00:00Z", now), "3w");
});

test("empty Home fixture and HomePage source contain the ruled empty affordance", () => {
  assert.deepEqual(empty.results, []);
  assert.equal(HOME_EMPTY_COPY, "No activity from people you follow yet.");
  assert.doesNotMatch(HOME_EMPTY_COPY, /\n/);
  assert.match(pageSource, /to="\/discover">Discover events<\/Link>/);
});

test("FeedReviewExcerpt and CSS sources gate a clear inline Read more marker on measurement", () => {
  assert.match(excerptSource, /probe\.scrollHeight <= maxHeight/);
  assert.match(excerptSource, /rendered\.truncated \? <>… <small>Read more<\/small><\/> : null/);
  assert.match(excerptSource, /lineLimit = 4/);
  assert.match(excerptSource, /Math\.ceil\(Number\.parseFloat\(styles\.lineHeight\) \* lineLimit\)/);
  assert.doesNotMatch(styles, /\.home-feed-review small\{[^}]*position:/);
  assert.match(styles, /\.home-feed-review small\{display:inline/);
});

test("review-like rows expose the review author, rating, and three-line excerpt", () => {
  assert.match(presenterSource, /Review by <strong>\{likedReview\.author\.display_name\}<\/strong>/);
  assert.match(presenterSource, /likedReview\?\.rating != null \? <RatingStars/);
  assert.match(presenterSource, /isDiaryJudgment && item\.context\.review/);
  assert.match(presenterSource, /<FeedReviewExcerpt lineLimit=\{3\}>\{likedReview\.body\}<\/FeedReviewExcerpt>/);
});

test("grouping applies only to favorites and never diary or WBT rows", () => {
  const actor = { id: 1, username: "actor" };
  const make = (type, id) => ({ type, actor, activity_at: `2026-08-02T12:00:0${id}Z`, target: { event: { id, title: `${type} ${id}` } } });
  const results = groupFeedItems([make("favorite_event", 1), make("favorite_event", 2), make("rated_been", 3), make("rated_been", 4), make("will_be_there", 5), make("will_be_there", 6)]);
  assert.equal(results[0].grouped.length, 2);
  assert.equal(results.length, 5);
  assert.equal(results.filter((item) => item.grouped).length, 1);
});
