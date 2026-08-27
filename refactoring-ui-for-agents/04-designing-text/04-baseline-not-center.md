# Baseline, Not Center

## Use this module when

- Different font sizes share one row.
- Titles and actions look subtly misaligned despite flex centering.
- Numerals, units, prices, or metadata sit together.
- Icon/text alignment appears optically unstable.

## Objective

Align mixed text using the baseline the eye already perceives, while handling icons and non-text objects with deliberate optical alignment.

## Rules

1. Text of different sizes on the same line should usually align by baseline.
2. Geometric centering is not the same as typographic alignment.
3. Use layout features that expose baseline alignment rather than arbitrary pixel nudges.
4. Icons require optical evaluation; their view boxes may not reflect visible mass.
5. Wrapped text changes the problem and may require top alignment or a different composition.

## Procedure

### 1. Confirm a shared typographic line

Use baseline alignment for title/action rows, price/unit groups, label/value pairs, and mixed-size inline metadata. If the elements are separate blocks, shared baseline may not be appropriate.

### 2. Apply baseline-aware layout

Use inline layout, flex/grid baseline alignment, or component primitives that preserve font metrics. Avoid fixed vertical transforms as the first solution.

### 3. Inspect actual fonts

Different families and weights have different ascenders, descenders, cap heights, and x-heights. Render the exact combination.

### 4. Handle icons separately

Align an icon to cap height, text center, or baseline according to its role. Normalize inconsistent SVG view boxes before adding local offsets.

### 5. Test wrapping

Long titles may wrap while actions remain single-line. Decide whether the action aligns with the first baseline, last baseline, or top edge, and document the component behavior.

## Failure modes

- `align-items: center` for every mixed-type row.
- Repeated `top: 1px` or transforms compensating for inconsistent primitives.
- Assuming two fonts share baseline metrics.
- Centering price and unit labels so their baselines visibly diverge.
- Aligning icons by their SVG box despite internal whitespace.
- Preserving a single-line row at the cost of truncated critical text.

## Verification

- Draw or inspect a baseline guide across mixed text.
- Test letters with ascenders/descenders and representative numerals.
- Compare at browser zoom levels relevant to the project.
- Test longest plausible strings and wrapping.
- Confirm icon optical alignment in resting, focus, and pressed states.
- Verify no layout shift occurs when text weight or state changes.

## Related modules

- [Balance weight and contrast](../02-hierarchy-is-everything/06-balance-weight-and-contrast.md)
- [Type scale](./01-establish-a-type-scale.md)
- [Intended size](../07-working-with-images/03-everything-has-an-intended-size.md)
