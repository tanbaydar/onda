# Accessible Does Not Have to Mean Ugly

## Use this module when

- Text or controls fail contrast requirements.
- Dark colored surfaces dominate the page merely to support white text.
- Secondary text on color is indistinguishable from primary text.
- Accessibility remediation threatens the intended hierarchy.

## Objective

Meet current accessibility requirements while preserving a controlled hierarchy by choosing different foreground/background relationships, not by defaulting to the loudest dark surface.

## Rules

1. Accessibility requirements are constraints, not optional polish.
2. Validate actual rendered foreground/background pairs and states.
3. When white-on-color requires an overly dominant background, consider dark text on a light tint.
4. For colored text on colored surfaces, hue as well as lightness can increase perceived and measured contrast.
5. Primary and secondary text must remain distinguishable without making secondary text inaccessible.
6. Current project and regulatory standards supersede numeric examples from any older source.
7. Contrast is only one accessibility dimension; focus, target size, semantics, motion, and non-color signals still apply.

## Procedure

### 1. Identify the role and required standard

Classify normal text, large text, essential icon, control boundary, focus indicator, decorative content, or state signal. Apply the project’s authoritative criterion.

### 2. Measure the real pair

Include opacity compositing, gradients, images, hover/pressed states, disabled treatment, and anti-aliased rendering assumptions supported by the evaluation method.

### 3. Try contrast inversion

If light text forces a dark, attention-heavy background, test a pale colored surface with a dark related foreground. This often retains color semantics with less visual mass.

### 4. Adjust hue intentionally

When secondary colored text on a dark surface approaches white, explore a nearby inherently brighter hue while keeping the family coherent.

### 5. Rebuild hierarchy

Use weight, size, spacing, and position to distinguish text roles when contrast cannot be reduced further.

### 6. Test all states and modes

Include focus, selected, error, disabled, high-contrast/forced-colors, themes, and user preferences required by scope.

## Failure modes

- Darkening every colored surface until it dominates.
- Making secondary text too faint to preserve hierarchy.
- Checking only resting text, not interactions.
- Assuming large/bold treatment without verifying the applicable standard.
- Treating automated contrast output as complete accessibility proof.
- Using contrast-compliant colors that are indistinguishable as status signals.

## Verification

- All in-scope pairs pass current authoritative criteria.
- Primary/secondary hierarchy remains clear through multiple channels.
- Light-tint alternatives were considered where dark surfaces became too loud.
- Focus and interaction states are visible.
- Color is not the only signal.
- Manual rendered review complements automated measurement.

## Related modules

- [Colored-background text](../02-hierarchy-is-everything/03-do-not-use-grey-text-on-colored-backgrounds.md)
- [Do not rely on color alone](./07-do-not-rely-on-color-alone.md)
- [Text over images](../07-working-with-images/02-text-needs-consistent-contrast.md)
