# You Do Not Have to Fill the Whole Screen

## Use this module when

- Desktop content stretches across a wide viewport.
- Forms, prose, tables, or cards are widened merely to align with full-width navigation.
- Large screens contain empty grid columns that agents feel compelled to fill.
- A narrow task surface looks visually unbalanced in a broad shell.

## Objective

Give each element the width required by its content and task, using max-widths, columns, and surrounding space without degrading readability or interpretation.

## Rules

1. Available width is not required width.
2. Different sections on the same page may have different optimal measures.
3. Use a content cap when further width stops helping.
4. Add a second column only when it contains useful supporting material with a real relationship to the primary task.
5. Begin responsive composition under real narrow constraints, then relax only genuine compromises on wider screens.
6. Do not force a narrow composition when content genuinely needs space.

## Procedure

### 1. Determine intrinsic task measure

For each region, ask what width supports:

- Readable line length.
- Efficient scanning and comparison.
- Reasonable control lengths.
- Stable media presentation.
- Necessary simultaneous data.

### 2. Cap the region

Use an existing max-width or propose a role-based measure. Let the surrounding layout absorb excess viewport space.

### 3. Decouple section widths

Navigation, data tables, prose, forms, and media may use different caps. Align meaningful edges, not every outer boundary.

### 4. Use columns to balance, not stretch

When a narrow primary region appears stranded on desktop, place genuinely helpful instructions, summary, or context in a separate column. Keep the form or prose at its optimal width.

### 5. Validate mobile-first constraints

Start near the narrowest supported width. Move to wide screens and change only relationships that were compromised by narrowness.

## Failure modes

- Full-width paragraphs or forms on large monitors.
- Inputs stretched to match the page even when expected values are short.
- Dashboard cards enlarged to occupy every grid track.
- Filler metrics or imagery added to consume blank space.
- Centering a very narrow region without considering useful contextual composition.
- Arbitrarily capping a table that requires horizontal comparison.

## Verification

- At wide desktop, line length and scanning remain comfortable.
- Each region has an explainable width role.
- Narrow surfaces do not expand merely because the header does.
- Secondary columns add task value and disappear or reorder coherently on mobile.
- Dense content has sufficient width and a deliberate overflow strategy.
- Removing viewport width beyond the content cap does not alter the internal composition.

## Related modules

- [Line length](../04-designing-text/03-keep-your-line-length-in-check.md)
- [Grids are overrated](./04-grids-are-overrated.md)
- [Feature before layout](../01-starting-from-scratch/01-feature-before-layout.md)
