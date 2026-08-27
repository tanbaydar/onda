# Relative Sizing Does Not Scale

## Use this module when

- Mobile is produced by reducing every desktop value proportionally.
- Heading/body ratios or padding/font ratios are encoded as fixed multipliers.
- Small and large component variants look like zoomed copies.
- Nested relative units produce values outside the design scale.

## Objective

Allow typography, padding, controls, and layout relationships to change independently across contexts so each composition is optically and functionally appropriate.

## Rules

1. Relationships that work at one viewport do not automatically remain correct at another.
2. Large elements usually shrink more than already-small elements on narrow screens.
3. Component padding need not scale proportionally with text.
4. Small and large variants should feel intentionally compact or generous, not uniformly zoomed.
5. Relative units are implementation tools, not proof of a valid visual relationship.
6. Values must still resolve to the product’s defined scales where required.

## Procedure

### 1. List coupled values

Find `em`-based font sizes, percentage widths, proportional paddings, transforms, or calculations that tie unrelated roles together.

### 2. Evaluate each role per context

At every relevant breakpoint or component size, choose:

- Body text for readability.
- Heading size for hierarchy without excessive wrapping.
- Padding for target size and density.
- Gap for grouping.
- Media size for content importance.

### 3. Compress the hierarchy range on small screens

Keep body and UI text readable while reducing large titles and display elements more aggressively. Preserve role distinction with weight and spacing.

### 4. Tune component variants independently

A compact button may reduce padding more than font size. A large button may add disproportionately more padding to feel generous and improve target size.

### 5. Use relative units deliberately

Use `rem`, `em`, percentages, viewport units, container units, or fluid functions when their dependency matches the intended behavior. Verify computed values and caps.

## Failure modes

- Desktop headline ratio applied unchanged to mobile.
- Every component property multiplied by 0.75 at a breakpoint.
- Nested `em` values producing off-scale computed sizes.
- Tiny body text used to preserve a desktop composition.
- Large controls that merely magnify icons and text without appropriate spacing.
- Fluid viewport text without minimum and maximum bounds.

## Verification

- Inspect computed sizes at narrow, typical, and wide contexts.
- Confirm large/small hierarchy differences are less extreme on small screens.
- Confirm body and control text remain readable.
- Compare component variants side by side; they should feel purpose-built.
- Check zoom and user font-size preferences according to project accessibility requirements.
- Verify no computed value accidentally falls between required system steps.

## Related modules

- [Type scale](../04-designing-text/01-establish-a-type-scale.md)
- [Grids are overrated](./04-grids-are-overrated.md)
- [Spacing system](./02-establish-a-spacing-and-sizing-system.md)
