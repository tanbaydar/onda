import assert from "node:assert/strict";
import test from "node:test";

import { appendUniqueEvents } from "./eventListPresentation.js";


test("infinite event ledgers append each canonical id once", () => {
  const current = [{ id: 1 }, { id: 2 }];
  const incoming = [{ id: 2 }, { id: 3 }, { id: 3 }, { id: 4 }];

  assert.deepEqual(
    appendUniqueEvents(current, incoming).map((event) => event.id),
    [1, 2, 3, 4],
  );
});
