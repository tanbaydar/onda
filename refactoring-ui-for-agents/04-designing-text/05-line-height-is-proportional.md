# Line-height Is Proportional

## Use this module when

- One global line-height is applied to all text.
- Long lines are hard to track.
- Small text feels cramped or large headings look loose.
- Buttons and labels inherit body leading unexpectedly.

## Objective

Choose line height according to font size, font metrics, line length, and text role.

## Rules

1. Longer lines generally need more leading.
2. Smaller text generally needs more relative leading.
3. Large display text generally needs tighter relative leading and may approach `1` when appropriate.
4. Single-line controls need explicit geometry; do not inherit prose settings accidentally.
5. The font’s metrics and language can alter the required value.
6. Define role-based line-height tokens instead of one universal ratio.

## Procedure

### 1. Classify role and wrapping

Determine whether text is single-line UI, multiline UI, body prose, metadata, heading, or display. Note expected measure and number of lines.

### 2. Start with role-appropriate leading

Use the product’s existing token. If defining a system, begin with comfortable body leading, a more generous ratio for small multiline text, and progressively tighter ratios for larger headings.

### 3. Render real paragraphs and headings

Use actual font, weight, width, and language. Font metrics make numeric ratios non-transferable between families.

### 4. Check line tracking

Read several lines quickly. The eye should move from the end of one line to the correct start of the next without hesitation.

### 5. Check block shape

Headings should read as cohesive blocks. Excess leading separates wrapped lines; insufficient leading causes collisions and visual heaviness.

### 6. Separate control geometry

Buttons and inputs should use padding/min-height and alignment rules. Do not use large line height as a substitute for target size.

## Failure modes

- `line-height: 1.5` applied to everything.
- Wide prose with tight leading.
- Large multi-line headings with body-like leading.
- Small legal or metadata text packed tightly.
- Using line height to vertically center controls.
- Cropping accents or scripts because a fixed height ignores font metrics.

## Verification

- Read representative multiline blocks at every text role.
- Test the widest allowed prose measure and the narrowest mobile measure.
- Check headings that wrap to two and three lines.
- Check diacritics, descenders, and target scripts.
- Verify controls retain target size independently from text leading.
- Inventory role tokens; avoid unrelated local line-height values.

## Related modules

- [Line length](./03-keep-your-line-length-in-check.md)
- [Type scale](./01-establish-a-type-scale.md)
- [Relative sizing](../03-layout-and-spacing/05-relative-sizing-does-not-scale.md)
