# Use Shadows to Convey Elevation

## Use this module when

- Designing buttons, dropdowns, popovers, draggable items, dialogs, or layered panels.
- Shadows differ component by component.
- A floating element does not clearly separate from content beneath it.
- Building an elevation scale.

## Objective

Map a small set of shadow levels to meaningful positions on a virtual z-axis and interaction states.

## Rules

1. Smaller, tighter shadows imply low elevation.
2. Larger, softer shadows imply greater distance from the background and attract more focus.
3. Elevation should correspond to actual layering and task attention.
4. Define a finite system; roughly a handful of levels is usually sufficient.
5. Interaction may change elevation: dragging lifts; pressing lowers.
6. Stacking order, focus management, backdrop, and shadow must describe the same layer model.
7. Product authority may choose border/spacing instead of shadow.

## Procedure

### 1. Inventory layers

List base content, slightly raised controls, sticky regions, dropdowns/popovers, dragged items, dialogs, toasts, and any system overlays.

### 2. Assign semantic elevation

Group elements that occupy equivalent z-positions. Do not create a level merely because a component wants a different aesthetic.

### 3. Define endpoints

Choose the smallest authorized shadow that separates a low layer and the largest that clearly elevates the highest layer without looking detached. Fill only needed intermediate levels.

### 4. Coordinate related behavior

For each level, define:

- Shadow token.
- Stacking context/z-index token.
- Surface color and border if needed.
- Backdrop behavior.
- Focus containment or dismissal behavior.
- Interaction transitions.

### 5. Test complex backgrounds

Shadows can disappear on dark, patterned, or similarly colored surfaces. Use the product’s surface and border strategy, not arbitrary shadow intensification.

## Failure modes

- Decorative shadow on every card.
- A dropdown with less elevation than content it overlays.
- Huge modal shadow without focus management or backdrop.
- Arbitrary z-index values unrelated to elevation tokens.
- Dragged items that move but do not visually lift.
- Pressed buttons gaining larger shadows.
- Ten near-identical shadow tokens.

## Verification

- List all elevation levels and their semantic owners.
- Compare every level side by side on real surfaces.
- Confirm higher layers have appropriately broader/softer treatment.
- Exercise drag, press, open, close, and focus states.
- Check clipping by overflow containers and stacking contexts.
- Ensure the system works without shadow where high-contrast or reduced-effects modes require alternatives.

## Related modules

- [Emulate a light source](./01-emulate-a-light-source.md)
- [Two-part shadows](./03-shadows-can-have-two-parts.md)
- [Use fewer borders](../08-finishing-touches/05-use-fewer-borders.md)
