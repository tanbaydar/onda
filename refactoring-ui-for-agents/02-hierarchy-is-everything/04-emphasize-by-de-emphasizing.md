# Emphasize by De-emphasizing

## Use this module when

- An active item or primary content still does not stand out after added color, weight, or size.
- Too many elements are already high contrast.
- A sidebar, toolbar, or set of alternatives competes with the main task.
- The obvious next step is to make the target even louder.

## Objective

Increase relative prominence by reducing competition, avoiding escalation that makes the whole interface noisy.

## Rules

1. Emphasis is relational. An element cannot stand out when its peers are equally strong.
2. Before adding emphasis, identify and quiet competing elements.
3. De-emphasis must preserve readability, discoverability, and accessible interaction.
4. Use the smallest reduction that establishes a clear distinction.
5. Do not turn inactive or secondary elements into disabled-looking elements.

## Procedure

### 1. Identify the target

Name exactly what should receive attention and why. If several unrelated targets exist, revisit the surface hierarchy.

### 2. Identify competitors

Look for peers sharing the same color, weight, size, fill, border, image area, or elevation.

### 3. Remove redundant emphasis

For competitors, consider:

- Lower neutral contrast.
- Regular instead of emphasized weight.
- No fill or a quieter surface.
- Less border contrast.
- Reduced image prominence.
- More compact spacing or less visual area.
- Moving ancillary actions out of the primary reading path.

### 4. Re-evaluate the target unchanged

Render the interface before adding anything to the target. If it now stands out sufficiently, stop.

### 5. Add one restrained differentiator if necessary

Choose a single authorized channel: weight, underline, indicator, color, or fill. Avoid stacking all channels.

## Typical applications

- Active navigation: quiet inactive items before intensifying the active item.
- Main content vs. sidebar: reduce sidebar chrome and contrast.
- Primary button in a button group: keep secondary actions outlined or text-like.
- Selected row: reduce unselected metadata or use one contained indicator.
- Dashboard metric: quiet labels and secondary metrics instead of enlarging the key number indefinitely.

## Failure modes

- Adding a brighter color every time an active state feels weak.
- Using bold, fill, shadow, border, icon, and animation simultaneously.
- Making inactive items too faint to read or recognize as interactive.
- De-emphasizing required warnings or recovery actions.
- Removing structural context that users need to understand the target.

## Verification

- Compare the target before and after only competitor changes.
- Check grayscale and color-blind simulations when color participates.
- Confirm inactive items remain readable and operable.
- Confirm focus temporarily supersedes resting hierarchy for keyboard users.
- Count emphasis channels on the target; remove any that do not add meaning.

## Related modules

- [Not all elements are equal](./01-not-all-elements-are-equal.md)
- [Semantics are secondary](./07-semantics-are-secondary.md)
- [Not every link needs color](../04-designing-text/06-not-every-link-needs-a-color.md)
