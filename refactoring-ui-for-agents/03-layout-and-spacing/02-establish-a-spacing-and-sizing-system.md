# Establish a Spacing and Sizing System

## Use this module when

- Repeated gaps and dimensions use many arbitrary values.
- Agents debate values one pixel at a time.
- Creating tokens for spacing, controls, icons, media, or containers.
- Similar components feel subtly inconsistent.

## Objective

Create a constrained nonlinear scale whose adjacent options produce meaningful perceptual differences across small and large dimensions.

## Rules

1. A simple “multiple of 4” rule is insufficient if it leaves too many indistinguishable large values.
2. Small values need closer numeric steps because a few pixels create large proportional change.
3. Large values need wider numeric steps because small absolute changes are imperceptible.
4. Build from a sensible base and use factors/multiples as scaffolding, then validate visually.
5. Separate spacing roles from fixed component dimensions even when they share numeric values.
6. Prefer existing tokens; new steps require recurring need.

## Procedure

### 1. Inventory and normalize

Extract margins, gaps, padding, widths, heights, icon sizes, and control dimensions. Normalize units and group by role.

### 2. Choose a base

A base related to the product’s body text or established grid can be useful. The source uses 16px as an illustrative base, not a universal mandate.

### 3. Construct a nonlinear candidate scale

At the small end, include steps suitable for icon gaps, compact padding, and control internals. Increase proportional separation toward section gaps and large layout dimensions. Adjacent values should generally feel visibly different in their intended contexts.

### 4. Separate categories

Maintain clear intent:

- **Spacing tokens:** relationships between elements.
- **Size tokens:** control heights, icons, avatars, media slots.
- **Measure tokens:** readable widths and container caps.
- **Optical exceptions:** documented one-off alignment corrections.

### 5. Map existing values

Snap arbitrary values to nearest candidates only after rendering. Preserve a value when changing it would break a required composition; record the exception instead of corrupting the scale.

### 6. Select by adjacency

For each new use, compare the likely token with one step smaller and one larger in context. Do not introduce intermediate values simply because two candidates both feel plausible.

### 7. Encode and document

Use project-native tokens or constants. Document intended roles and examples, not exhaustive component ownership.

## Failure modes

- A linear scale continuing in tiny increments at large sizes.
- Tokens for every historical literal.
- Using the same token category for layout gaps and exact media ratios without documenting roles.
- Arbitrary decimal `rem` values created by conversion.
- Adding a new value to avoid choosing between adjacent system steps.
- Mechanical snapping without visual verification.

## Verification

- Adjacent scale steps are distinguishable at intended use sizes.
- Similar components share internal spacing and size anatomy.
- Large layout dimensions do not proliferate in tiny increments.
- Token names reveal role or scale position.
- Dense and sparse layouts both work with the same vocabulary.
- No value was changed outside task scope merely to improve token statistics.

## Related modules

- [Limit your choices](../01-starting-from-scratch/05-limit-your-choices.md)
- [Start with too much whitespace](./01-start-with-too-much-white-space.md)
- [Relative sizing](./05-relative-sizing-does-not-scale.md)
