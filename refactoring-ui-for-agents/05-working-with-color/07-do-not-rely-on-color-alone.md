# Do Not Rely on Color Alone

## Use this module when

- Showing success/failure, increase/decrease, selection, categories, chart series, or validation.
- Red and green, multiple hues, or subtle color changes carry meaning.
- Designing maps, graphs, calendars, tags, or status indicators.

## Objective

Use color to reinforce information already communicated through text, shape, icon, pattern, position, contrast, or structure.

## Rules

1. Every meaningful color difference needs a non-color counterpart.
2. Color can improve scanning but cannot be the only decoding key.
3. For quantitative or ordered data, luminance/contrast progression may be more robust than unrelated hues.
4. Labels and direct annotations are preferable to distant legends when space permits.
5. Selected, error, and focus states must remain identifiable in grayscale and assistive modes.
6. Redundant signals should be concise, not decorative clutter.

## Signal options

- Text label or status word.
- Directional or semantic icon plus accessible name.
- Shape or marker change.
- Solid vs. dashed pattern.
- Position, order, or grouping.
- Luminance/contrast difference.
- Direct annotation on a chart line or region.
- Border, underline, checkmark, or selection indicator.

## Procedure

### 1. List color-encoded meanings

For every colored element, state what users would lose if the UI were grayscale.

### 2. Choose a redundant channel

Match the data:

- Positive/negative → arrow/icon plus text.
- Selected/unselected → checkmark, border, or indicator.
- Error field → message and semantic association.
- Chart series → direct label, pattern, marker, or contrast.
- Calendar categories → text/shape/pattern plus color.

### 3. Preserve hierarchy

The redundant cue should be clear but not larger or louder than the underlying information requires.

### 4. Test simulations and modes

Use grayscale, common color-vision simulations, forced colors, and actual low-quality display conditions where relevant.

### 5. Verify accessible semantics

Expose status, selection, values, and relationships programmatically, not only visually.

## Failure modes

- Red/green text with no symbols or labels.
- Chart lines differentiated only by hue.
- Selected tabs indicated only by color change.
- Required field errors indicated only by a red border.
- Status dots without text or accessible names.
- Adding decorative icons that do not clearly encode the meaning.

## Verification

- Remove or desaturate color; all required meaning remains.
- Check assistive output for state and relationship.
- Confirm redundant cues remain distinct at actual rendered size.
- Test dense views where patterns, markers, or labels may collide.
- Verify legends and annotations match data after filtering or reordering.
- Ensure color still supports rather than contradicts the non-color signal.

## Related modules

- [Accessible color](./06-accessible-does-not-have-to-mean-ugly.md)
- [Semantics are secondary](../02-hierarchy-is-everything/07-semantics-are-secondary.md)
- [Alignment](../04-designing-text/07-align-with-readability-in-mind.md)
