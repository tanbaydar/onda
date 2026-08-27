# PROFILE RATING DISTRIBUTION — incremental handoff (delta; replaces the built module)
Ruled 2026-08-01. Zero new tokens. Visual truth: spec/rating-distribution.html (hover is live there).

## REPLACE entirely
Kill the 10-row horizontal-bar list (rows, hairline separators, per-row labels, single green bar). Replace with one compact vertical histogram.

## Module spec
- Container: 160px wide (≈ stats column), bar area 100px tall (max ~120).
- Ten bars, ½★→5★ left→right: flex row, gap 2px, each bar flex:1 (existing .hist grammar, vertical).
- Height = count / max(bucket counts) × 100%. Zero-count bucket = 2px baseline stub (--sp-2), never a full bar, never omitted.
- Color: ALL ten bars `--judgment`, uniformly. No highlighting any bar, no mixed treatments. (Ruled fallback if judged too loud in situ: ALL bars `--text-secondary` — one treatment for all, never mixed.)
- Axis labels: "½" left end, "5" right end only — 11px fn `--text-muted`, space-between under the bars. No other permanent text, no separators, no per-bar labels.
- Counts on hover/tap: per-bar tooltip "N · X★" — 11px fn `--text` on `--bg`, 1px `--border-strong` outline, above the bar. Tap toggles on touch.
- Section header keeps the existing caps-overline register: fn 12/500/caps/+0.05em `--text-muted`, 32 above / 12 below.
- Placement (locked): B-tier, within the stats area — mobile below the venues/cities subline; desktop right-aligned under the numerals. Renders only at ≥5 ratings; absent below (no collapse machinery).

## Data mapping
`rating_distribution.buckets[].relative_value` already normalizes to the largest bucket — height = relative_value × 100%; relative_value 0 → 2px stub.

## Flag
No ≥5-rating profile fixture exists — spec render uses flagged stand-in counts; add a dense-profile fixture before integration QA.

## Dated delta — 2026-08-27 static distribution and accessible detail

- Ten microscopic bucket controls are withdrawn at every placement. Bars are static chart marks: no button role, per-bar focus, hover-only tooltip, or tap toggle.
- The chart has one accessible description that exposes all ten `rating: count` values in order, including zero-count buckets.
- Event placement adds one native `View distribution` disclosure below the chart. Its expanded content is a readable ten-row label/value list and its summary meets the mobile target rule.
- Profile statistics placement remains a static 104×30 sparkline without a visible disclosure; all values remain available to assistive technology through the chart description.
- Existing proportional height, uniform judgment color, axis endpoints, rating threshold, and zero-stub rulings remain unchanged.
