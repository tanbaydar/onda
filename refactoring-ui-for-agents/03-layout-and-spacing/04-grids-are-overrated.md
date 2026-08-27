# Grids Are Overrated

## Use this module when

- A grid system is dictating component width regardless of content.
- Sidebars or cards become too wide on large screens and too narrow on medium screens.
- Percentage widths create non-monotonic or unstable responsive behavior.
- A component should remain fixed or capped until the viewport requires shrinkage.

## Objective

Use grids as optional alignment tools while selecting fixed, fluid, and capped dimensions according to content behavior.

## Rules

1. Do not use percentages unless the element should actually scale with its container.
2. Content-driven sidebars and controls often need fixed or capped widths.
3. Let flexible regions absorb remaining space.
4. Do not shrink a component before available space forces it.
5. Grids may govern local arrangements without governing every page region.
6. Breakpoint behavior should be monotonic and understandable.

## Dimension decision tree

1. **Does the element have a stable optimal width?** Use width plus `max-width: 100%` or an equivalent capped strategy.
2. **Should it absorb remaining room?** Use flexible growth with a sensible minimum.
3. **Should multiple peers share available space?** Use grid/flex fractions with min/max constraints.
4. **Should it scale with media or container ratio?** Use relative sizing intentionally.
5. **Does content determine size?** Prefer intrinsic sizing.

## Procedure

### 1. Identify grid-induced compromises

Resize slowly and observe wrapping, truncation, blank space, and surprising width changes. Record the ranges where content suffers despite available room.

### 2. Assign independent behavior

For each region, set minimum, preferred, maximum, and overflow behavior. A sidebar can stay stable while the main content flexes.

### 3. Delay breakpoints

Keep a component at preferred width until the viewport can no longer accommodate it. Then allow shrinkage, wrapping, stacking, or alternate composition.

### 4. Retain useful alignment

Use shared edges, gaps, and internal grids where they improve order. Reject religious adherence to global columns.

## Failure modes

- A 25% sidebar that grows indefinitely with the viewport.
- A form wider on medium screens than on large screens because column spans change.
- Cards shrinking while empty columns remain.
- Every component width expressed as a grid fraction.
- Breakpoints selected from framework defaults rather than content failure.
- Fixed widths without `max-width` or narrow-screen escape behavior.

## Verification

- Drag through all widths rather than checking only preset screenshots.
- Preferred-width components remain stable until necessary.
- No component becomes narrower when more usable width becomes available unless composition intentionally changes.
- Text wraps and controls fit at defined minima.
- Flexible regions receive surplus space.
- Grid use can be explained by alignment or equal distribution, not convention.

## Related modules

- [Do not fill the screen](./03-you-do-not-have-to-fill-the-whole-screen.md)
- [Relative sizing](./05-relative-sizing-does-not-scale.md)
- [Spacing system](./02-establish-a-spacing-and-sizing-system.md)
