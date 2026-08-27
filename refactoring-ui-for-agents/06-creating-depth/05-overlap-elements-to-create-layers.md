# Overlap Elements to Create Layers

## Use this module when

- A composition needs depth or continuity across adjacent regions.
- Cards, callouts, media, controls, or avatars cross section boundaries.
- Overlapping user images clash.
- A flat design needs layering without heavy shadow.

## Objective

Create intentional layers through overlap while preserving readability, separation, responsive stability, and interaction access.

## Rules

1. Overlap must express a relationship between the layers.
2. The foreground object needs sufficient separation from every possible background.
3. User media may need a background-colored ring or equivalent separator.
4. Overlap must not clip focus indicators, hit targets, text, or dynamic content.
5. Responsive layouts may reduce, reposition, or remove overlap when space becomes unstable.
6. Stacking order must be explicit and limited.

## Procedure

### 1. Define the layer story

Examples: a booking panel bridges hero and content; an avatar belongs to both cover and profile identity; carousel controls sit above media. If the relationship cannot be stated, avoid overlap.

### 2. Choose the overlap amount from the sizing system

Use a repeatable scale value or proportion tied to the component’s dimensions. Avoid arbitrary negative margins.

### 3. Stabilize separation

Use surface, border, ring, or shadow tokens authorized by the product. For stacked images, a ring matching the underlying surface can prevent visual collision.

### 4. Define stacking and containment

Specify z-index role, overflow behavior, containing block, and focus outline strategy. Avoid creating accidental stacking contexts.

### 5. Test responsive escape behavior

At narrow widths, ensure overlap does not cover text or force horizontal overflow. Replace with ordinary flow when necessary.

### 6. Test dynamic content

Long titles, missing images, loading states, and variable card heights must not shift the overlap into unrelated content.

## Failure modes

- Decorative overlap with no content relationship.
- Negative margins scattered as one-off values.
- Foreground card disappearing against similar backgrounds.
- Avatar stacks whose images visually merge.
- Focus rings clipped by parent overflow.
- Mobile overlap covering headings or actions.
- Arbitrary high z-index values.

## Verification

- The layer relationship remains clear with shadows disabled.
- Overlap amount maps to an existing scale or documented component geometry.
- All focusable elements show full focus treatment.
- Missing media and long content remain stable.
- Narrow viewport behavior is explicitly checked.
- Stacking order is compatible with menus, dialogs, and sticky regions.

## Related modules

- [Flat depth](./04-even-flat-designs-can-have-depth.md)
- [Beware user uploads](../07-working-with-images/04-beware-user-uploaded-content.md)
- [Elevation system](./02-use-shadows-to-convey-elevation.md)
