# Balance Weight and Contrast

## Use this module when

- Icons overpower adjacent labels.
- Thin borders disappear, but darker borders feel harsh.
- Mixed solid and outline elements look visually unbalanced.
- Two elements with the same nominal color feel unequally prominent.

## Objective

Balance perceived emphasis by considering both visual mass and contrast rather than treating color or size in isolation.

## Rules

1. Greater visual mass creates emphasis even when color is unchanged.
2. Reduce contrast to quiet heavy elements.
3. Increase weight or thickness to support low-contrast elements when darkening would create noise.
4. Balance is contextual; compare elements at rendered size beside their actual neighbors.
5. Icon weight, fill, stroke, size, and optical bounds are part of hierarchy.

## Procedure

### 1. Identify visual mass

Look for bold text, solid icons, thick strokes, filled controls, large images, and dense borders. Estimate how much dark or saturated area each contributes.

### 2. Compare intended roles

If an icon supports a label, the label should usually dominate or balance it. If an icon is the control itself, it must remain discoverable but should not dominate neighboring content without reason.

### 3. Counterbalance heavy elements

Try a quieter neutral color, smaller approved size, outline variant, or reduced fill. Do not reduce accessible target size; visual glyph size and hit area are independent.

### 4. Reinforce subtle elements

For a low-contrast border or divider that must remain perceivable, consider a slightly heavier approved width before choosing a much darker color.

### 5. Test in every state

Hover, focus, selected, disabled, and pressed treatments alter weight and contrast. Ensure the balance change communicates state without layout shift.

## Failure modes

- Solid black icons beside regular-weight text of the same color.
- Very dark 1px borders around every surface.
- Increasing both border darkness and thickness without a role change.
- Shrinking icons below legibility to quiet them.
- Low-opacity text used to compensate for heavy bold weight, producing poor readability.
- Mixing icon families with incompatible stroke weights.

## Verification

- View icons and text together at 100% rendering scale.
- Compare a grayscale screenshot and reduced thumbnail.
- Inspect optical rather than bounding-box size.
- Confirm target areas remain accessible after visual resizing.
- Check that focus indicators are deliberately prominent and not confused with resting borders.
- Ensure sibling components use compatible icon families and stroke/fill conventions.

## Related modules

- [Size is not everything](./02-size-is-not-everything.md)
- [Intended size](../07-working-with-images/03-everything-has-an-intended-size.md)
- [Use fewer borders](../08-finishing-touches/05-use-fewer-borders.md)
