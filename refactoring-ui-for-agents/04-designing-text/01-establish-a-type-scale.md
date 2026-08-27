# Establish a Type Scale

## Use this module when

- A product contains many one-off font sizes.
- New components choose type size locally.
- Building typography tokens or repairing hierarchy.
- Nested relative units produce unexpected computed sizes.

## Objective

Create a compact set of distinct, reusable type sizes mapped to interface roles and stable across browsers and nesting contexts.

## Rules

1. Small sizes need closer steps; large display sizes can use wider steps.
2. A mathematically pure modular scale is optional, not inherently superior.
3. Hand-crafted integer values are often more practical for interfaces.
4. Use `rem` or explicit project-approved units so nesting does not move text off-scale.
5. Every size must have a role; every role should reuse a size unless a documented exception exists.
6. Responsive roles may map to different scale steps; do not scale all roles proportionally.

## Procedure

### 1. Inventory computed sizes

Inspect rendered values, not only source tokens. Group occurrences by purpose: micro metadata, UI labels, body, large body, row title, page title, display, numeral, and so on.

### 2. Identify the base

Choose the main reading or UI size required by the product. Do not reduce it simply to fit more layout.

### 3. Build practical steps

Add sizes needed for real roles. Keep smaller increments near body/UI text, where one step materially affects readability; use larger jumps for headings and display text.

### 4. Compare adjacent candidates

Render each role with the likely size, one step below, and one above. Use real fonts, weight, line height, and content. Select the least exaggerated option that establishes the required hierarchy.

### 5. Map responsive behavior

Large display roles may step down more aggressively on narrow screens. Body and UI text should remain stable unless product accessibility and content evidence support change.

### 6. Encode roles

Prefer semantic aliases over repeated raw steps when the product benefits from them, for example `text-body`, `text-meta`, or `text-title`. Keep the underlying scale available when appropriate.

### 7. Remove drift carefully

Consolidate near-duplicates within task scope. Do not rewrite unrelated surfaces merely to make the inventory cleaner.

## Failure modes

- Every integer size from a narrow range appears somewhere.
- A modular scale creates fractional values and missing practical sizes.
- `em` nesting produces unintended computed sizes.
- Heading levels map mechanically to descending sizes.
- Mobile type is a uniform percentage of desktop.
- New roles are encoded as component-specific literals.

## Verification

- List all computed sizes on the changed surface; each maps to a role.
- Adjacent steps are perceptibly distinct in the actual font.
- Body and UI text remain readable at supported zoom and widths.
- Heading hierarchy is clear without extreme jumps.
- Nested components remain on-scale.
- Long translated or user-generated content does not force ad hoc size reductions.

## Related modules

- [Size is not everything](../02-hierarchy-is-everything/02-size-is-not-everything.md)
- [Relative sizing](../03-layout-and-spacing/05-relative-sizing-does-not-scale.md)
- [Line height](./05-line-height-is-proportional.md)
