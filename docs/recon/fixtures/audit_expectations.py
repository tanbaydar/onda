#!/usr/bin/env python3
"""Read-only mechanical audit of the ingestion fixture expectations."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


FIXTURE_DIR = Path(__file__).resolve().parent
README_PATH = FIXTURE_DIR / "README.md"
BASELINE = "ra_listing_complete.synthetic.json"
ALLOWED_REASONS = {"PARSE_FAILURE", "NO_ARTIST", "EMPTY_TITLE", "BAD_DATE"}
CAPTURED_SKIPS = {
    "ra_event_listings_historical_response.sample.json":
        "sanitized capture has an original-response totalResults and is not exact-count input",
    "ra_cancelled_event_detail.sample.json":
        "detail-query evidence is not Transformer listing input",
}
TEXT_SKIP = {
    "ra_listing_malformed_payload.synthetic.txt":
        "intentional non-JSON payload-grain failure",
}


def section_between(text: str, start_marker: str, end_pattern: str) -> str | None:
    start = text.find(start_marker)
    if start < 0:
        return None
    body_start = start + len(start_marker)
    match = re.search(end_pattern, text[body_start:], flags=re.MULTILINE)
    body_end = body_start + match.start() if match else len(text)
    return text[body_start:body_end]


def fixture_block(readme: str, filename: str) -> str | None:
    if filename.startswith("ra_listing_paginated_page_"):
        pagination = section_between(
            readme,
            "## Pagination scenario",
            r"^## Cross-cutting expectations$",
        )
        if pagination is None:
            return None
        page = "1" if "_page_1." in filename else "2"
        return section_between(
            pagination,
            f"### Page {page} expected outcomes",
            r"^### ",
        )
    return section_between(
        readme,
        f"## `{filename}`",
        r"^## ",
    )


def bullet_text(block: str, label: str) -> str | None:
    match = re.search(
        rf"^- {re.escape(label)}:(.*?)(?=^\s*- |\Z)",
        block,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else None


def integer_bullet(block: str, label: str) -> int | None:
    value = bullet_text(block, label)
    if value is None:
        return None
    match = re.match(r"\**(\d+)", value)
    return int(match.group(1)) if match else None


def event_facts(path: Path) -> tuple[int, list[str], int]:
    payload = json.loads(path.read_text())
    events = payload["data"]["eventListings"]["data"]
    event_ids = [
        wrapper["event"]["id"]
        for wrapper in events
        if "id" in wrapper["event"]
    ]
    unique_event_ids = list(dict.fromkeys(event_ids))
    return len(events), unique_event_ids, len(events) - len(event_ids)


def main() -> int:
    readme = README_PATH.read_text()
    discrepancies: list[str] = []

    baseline_count, baseline_ids, baseline_idless = event_facts(FIXTURE_DIR / BASELINE)
    expected_baseline_ids = ["syn-event-complete-1", "syn-event-complete-2"]
    if (
        baseline_count != 2
        or baseline_ids != expected_baseline_ids
        or baseline_idless != 0
    ):
        print(
            "CALIBRATION FAILED: expected 2 baseline events with IDs "
            f"{expected_baseline_ids}; got count={baseline_count}, "
            f"ids={baseline_ids}, idless={baseline_idless}"
        )
        return 1
    print(
        "CALIBRATION OK: ra_listing_complete.synthetic.json -> "
        "2 events; syn-event-complete-1, syn-event-complete-2"
    )

    for filename, reason in sorted(CAPTURED_SKIPS.items()):
        print(f"SKIP: {filename} — {reason}")
    for filename, reason in sorted(TEXT_SKIP.items()):
        print(f"SKIP: {filename} — {reason}")

    exercised_reasons: set[str] = set()
    synthetic_paths = sorted(FIXTURE_DIR.glob("ra_listing_*.synthetic.json"))
    for path in synthetic_paths:
        block = fixture_block(readme, path.name)
        if block is None:
            discrepancies.append(f"{path.name}: no corresponding README block")
            continue

        try:
            payload_count, payload_ids, idless_count = event_facts(path)
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            discrepancies.append(f"{path.name}: fixture extraction failed: {error}")
            continue

        admitted = integer_bullet(block, "events admitted")
        quarantined = integer_bullet(block, "events quarantined")
        observed_text = bullet_text(block, "observed source IDs")
        if admitted is None:
            discrepancies.append(f"{path.name}: missing or invalid events admitted")
        if quarantined is None:
            discrepancies.append(f"{path.name}: missing or invalid events quarantined")
        if observed_text is None:
            discrepancies.append(f"{path.name}: missing observed source IDs")
            readme_observed: list[str] = []
        else:
            readme_observed = re.findall(r"`(syn-event-[^`]+)`", observed_text)

        if admitted is not None and quarantined is not None:
            if admitted + quarantined != payload_count:
                discrepancies.append(
                    f"{path.name}: admitted({admitted}) + quarantined({quarantined}) "
                    f"!= payload events({payload_count})"
                )

        expected_observed_count = len(payload_ids)
        if len(readme_observed) != expected_observed_count:
            discrepancies.append(
                f"{path.name}: README observed count {len(readme_observed)} != "
                f"payload events({payload_count}) - ID-less events({idless_count})"
            )
        if readme_observed != payload_ids:
            discrepancies.append(
                f"{path.name}: README observed IDs {readme_observed} != "
                f"unique payload event.id values {payload_ids}"
            )
        if payload_count < len(readme_observed):
            discrepancies.append(
                f"{path.name}: payload count {payload_count} < "
                f"observed-ID count {len(readme_observed)}"
            )

        block_event_ids = set(re.findall(r"`(syn-event-[^`]+)`", block))
        if block_event_ids != set(payload_ids):
            discrepancies.append(
                f"{path.name}: scenario event-ID claims {sorted(block_event_ids)} != "
                f"payload event IDs {sorted(payload_ids)}"
            )

        quarantine_text = bullet_text(block, "events quarantined") or ""
        reasons = set(re.findall(r"`([A-Z][A-Z_]+)`", quarantine_text))
        unexpected = reasons - ALLOWED_REASONS
        if unexpected:
            discrepancies.append(
                f"{path.name}: unexpected quarantine reasons {sorted(unexpected)}"
            )
        exercised_reasons.update(reasons & ALLOWED_REASONS)

    missing_reasons = ALLOWED_REASONS - exercised_reasons
    if missing_reasons:
        discrepancies.append(
            f"reachable rejection reasons not exercised: {sorted(missing_reasons)}"
        )

    if discrepancies:
        for discrepancy in discrepancies:
            print(f"DISCREPANCY: {discrepancy}")
        return 1

    print(
        f"AUDIT CLEAN: {len(synthetic_paths)} JSON fixtures; "
        "counts, observed IDs, scenario IDs, and rejection coverage agree"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
