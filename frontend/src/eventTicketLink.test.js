import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";


const eventPage = readFileSync(
  new URL("./pages/EventPage.jsx", import.meta.url),
  "utf8",
);


test("event detail gates the outbound RA ticket link on true ticket status and a URL", () => {
  assert.match(
    eventPage,
    /event\.is_ticketed === true && event\.ticket_url/,
  );
  assert.match(eventPage, />Get tickets<\/a>/);
  assert.match(eventPage, /target="_blank"/);
  assert.match(eventPage, /rel="noopener noreferrer"/);
});
