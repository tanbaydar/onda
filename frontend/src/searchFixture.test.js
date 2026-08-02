import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const fixture = JSON.parse(
  readFileSync(new URL("../design-fixtures/search-corpus.json", import.meta.url)),
);

test("search corpus covers the three ruled fixture cases", () => {
  assert.deepEqual(
    fixture.cases.map(({ name }) => name),
    [
      "single-character prefix",
      "exact then prefix then popularity",
      "empty result",
    ],
  );
  assert.equal(fixture.cases[0].query.length, 1);
  assert.deepEqual(fixture.cases[2].expected_titles, []);
});
