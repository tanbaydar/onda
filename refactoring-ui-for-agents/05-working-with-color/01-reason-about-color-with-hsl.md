# Reason About Color with HSL

## Use this module when

- Comparing or adjusting colors whose encoded values are hard to interpret.
- Building shade families.
- Discussing hue, vividness, and relative light/dark behavior.
- Agents are using `lighten`, `darken`, alpha overlays, or hex edits without visual rationale.

## Objective

Use perceptually meaningful dimensions—hue, saturation, and lightness—as a reasoning model while respecting the project’s chosen color format and the limitations of HSL.

## Model

- **Hue:** position around the color family wheel; the property that makes colors read as blue, green, red, and so on.
- **Saturation:** intensity or distance from neutral.
- **Lightness:** position between black and white in the HSL model.

HSL is easier to reason about than raw RGB/hex, but equal HSL changes do not guarantee equal perceived changes. Use it to form a hypothesis, then inspect rendered results and accessibility metrics.

## Rules

1. Change one dimension intentionally and observe the others perceptually.
2. Do not confuse HSL lightness with HSB/HSV brightness.
3. Do not assume equal numeric lightness means equal perceived brightness across hues.
4. Preserve the project’s source-of-truth format; conversion for analysis does not authorize a system rewrite.
5. Use explicit palette values for production roles rather than runtime improvisation.

## Procedure

### 1. Convert for understanding

When inspecting a hex or RGB palette, view equivalent hue, saturation, and lightness values. Group colors by semantic role and hue family.

### 2. State the intended adjustment

Examples:

- Quieter but still in the same hue family.
- Dark enough for text.
- Light enough for a subtle surface.
- More vivid at a pale step.
- Warmer neutral without looking colored.

### 3. Adjust deliberately

Modify lightness, saturation, and—when needed—hue in small controlled steps. Do not assume a single automated function preserves character.

### 4. Validate in context

Render swatches beside neighbors and apply them to actual text, controls, backgrounds, and states. Colors that look distinct in a picker may collapse in UI.

### 5. Record explicit tokens

Once chosen, store the exact approved values in the project’s normal color system with semantic or scale names.

## Failure modes

- Editing hex digits by intuition.
- Treating HSL as perceptually uniform.
- Confusing brightness and lightness models.
- Generating runtime shades that proliferate near-duplicates.
- Evaluating isolated swatches on a checkerboard instead of product surfaces.
- Reformatting an entire palette without a task requirement.

## Verification

- Each change has an explicit hue/saturation/lightness rationale.
- Adjacent shades are visibly distinct in actual UI roles.
- Contrast is computed from rendered color pairs using current project standards.
- Color character remains coherent across light and dark ends.
- Production code uses approved explicit values or tokens.

## Related modules

- [Define shades up front](./03-define-your-shades-up-front.md)
- [Saturation across lightness](./04-do-not-let-lightness-kill-saturation.md)
- [Tinted greys](./05-greys-do-not-have-to-be-grey.md)
