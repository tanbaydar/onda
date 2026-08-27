# Limit Your Choices

## Use this module when

- A codebase contains many near-duplicate values.
- An agent is choosing colors, sizes, weights, radii, or shadows component by component.
- Reviews stall on tiny numeric differences.
- Building or repairing a design system.

## Objective

Replace repeated arbitrary decisions with a constrained vocabulary whose options are distinct, reusable, and tied to roles.

## Rules

1. Define a bounded scale for every recurring visual dimension.
2. Adjacent options must differ enough to support confident selection.
3. Choose from the system before proposing a new value.
4. A new value needs a reusable role, not merely a component name.
5. Do not attempt to define every system before evidence exists; systematize recurring decisions as they appear.
6. Avoid near-duplicates that users cannot perceive and agents cannot justify.

## Systems to inventory

- Font families, sizes, weights, line heights, and tracking.
- Neutral, primary, accent, and semantic color scales.
- Spacing and sizing steps.
- Content widths and max-widths.
- Icon, avatar, control, and media sizes.
- Border widths and radii.
- Elevation/shadow levels.
- Opacity values.
- Motion durations and easing, when product authority allows motion.

## Procedure

### 1. Extract current values

List literal and tokenized values by category. Normalize equivalent formats before counting them. Distinguish true optical exceptions from arbitrary drift.

### 2. Group by role

Map values to semantic roles such as `text-body`, `space-group`, `control-medium`, or `surface-overlay`. Do not begin by naming tokens after pages or components.

### 3. Remove imperceptible distinctions

If two values serve the same role and cannot be reliably distinguished in context, consolidate them under the higher-authority or more prevalent system value.

### 4. Select by elimination

When choosing a value, render one likely option plus its adjacent smaller and larger system values. Reject obviously wrong extremes. If an outer value wins, repeat around it. This is more reliable than pixel-by-pixel tuning.

### 5. Document exceptions

An exception should state:

- Why no system value satisfies the role.
- Why the case is unlikely to recur.
- What property is optically adjusted.
- Which product authority permits it.

### 6. Prevent regression

Prefer tokens, primitives, lint rules, visual tests, or documented review checks that make the constrained vocabulary easy to follow. Enforcement must match project tooling and scope.

## Token naming guidance

Prefer role-based names when meaning is stable:

- `text-primary`, `text-muted`, `surface-raised`, `space-section`, `control-height-sm`.

Use scale names when the values are intentionally general-purpose:

- `space-2`, `space-3`, `font-size-4`, `shadow-2`.

Avoid appearance-only or component-local names when the value is shared:

- `slightly-lighter-grey`, `profile-gap`, `nice-shadow`, `button-blue`.

## Failure modes

- One-off literals for every new component.
- Scales with adjacent steps too similar to choose confidently.
- A token for every literal, preserving inconsistency under names.
- Global tokens named after one route.
- Adding a value before comparing existing adjacent choices.
- Forcing a system value where a documented optical exception is necessary.
- Creating a comprehensive theoretical system that no current feature needs.

## Verification

- Every recurring value maps to a token or documented role.
- Similar components use the same anatomy and scale choices.
- Adjacent options create visible, useful differences.
- A new agent can select values without inventing decimals or one-pixel variants.
- The surface remains coherent across sparse, typical, and dense data.
- New values include evidence of reuse and authority.

## Related modules

- [Spacing and sizing system](../03-layout-and-spacing/02-establish-a-spacing-and-sizing-system.md)
- [Type scale](../04-designing-text/01-establish-a-type-scale.md)
- [Define shades up front](../05-working-with-color/03-define-your-shades-up-front.md)
- [Elevation system](../06-creating-depth/02-use-shadows-to-convey-elevation.md)
