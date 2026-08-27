# Do Not Let Lightness Kill Saturation

## Use this module when

- Light and dark palette steps look washed out, dirty, or lifeless.
- A base color is vivid but its shade family loses character.
- Yellow, cyan, blue, or other hues behave unexpectedly at equal numeric lightness.
- Building a coherent color scale manually.

## Objective

Preserve perceived color intensity and family character across light and dark steps by adjusting saturation and, where useful, hue—not lightness alone.

## Rules

1. Saturation has less visible impact near HSL’s lightness extremes.
2. Light and dark steps often need increased numeric saturation to remain colorful.
3. Different hues have different perceived brightness at the same HSL lightness.
4. Small hue rotations can help a color feel lighter or darker without washing it toward white or black.
5. Hue rotation should remain restrained enough that the family still reads as one color.
6. Visual and accessibility validation outrank numeric symmetry.

## Procedure

### 1. Inspect the family, not isolated values

Place all steps side by side and apply them to representative surfaces. Identify points where the family appears grey, brown, neon, or disconnected.

### 2. Compensate saturation

As steps approach very light or very dark values, compare higher saturation against the mathematically uniform version. Keep the version that preserves character without becoming fluorescent.

### 3. Use perceived brightness

If lightness adjustments make a color dull, rotate slightly toward a nearby hue perceived as brighter for light steps or darker for dark steps. The source suggests keeping such movement modest—roughly within a few tens of degrees—as a heuristic.

### 4. Combine dimensions

Use lightness, saturation, and hue together. Do not rely on one dimension to do all work.

### 5. Revalidate semantics

A warning yellow that shifts toward orange in dark steps may be useful; a brand blue that shifts visibly purple may violate identity. Product meaning constrains hue movement.

## Failure modes

- Same saturation at every lightness step.
- Pale colors that appear grey and dark colors that look muddy.
- Extreme hue rotation causing separate color families.
- Assuming HSL lightness predicts human brightness.
- Fixing vividness by making every step highly saturated.
- Ignoring contrast because the swatch family looks attractive.

## Verification

- The family remains recognizable across all steps.
- Light and dark tokens perform their actual surface/text roles.
- Adjacent steps are distinct without abrupt hue jumps.
- Required contrast pairs pass current standards.
- Color-blind and grayscale checks retain required non-color structure.
- Hue movement is documented when identity or semantics could be affected.

## Related modules

- [Reason about color](./01-reason-about-color-with-hsl.md)
- [Define shades](./03-define-your-shades-up-front.md)
- [Tinted greys](./05-greys-do-not-have-to-be-grey.md)
