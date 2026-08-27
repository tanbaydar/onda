# Greys Do Not Have to Be Grey

## Use this module when

- A neutral palette feels sterile, disconnected, too cool, or too warm.
- Establishing product color temperature.
- Neutral shades appear inconsistent across light and dark steps.
- Pure zero-saturation greys make the interface feel generic.

## Objective

Use subtly tinted neutrals to establish a coherent temperature while preserving their neutral function and hierarchy.

## Rules

1. A color can function as neutral while carrying low saturation.
2. Blue-tinted neutrals tend to feel cooler; yellow/orange-tinted neutrals tend to feel warmer.
3. Keep temperature consistent across the family.
4. Light and dark extremes may need more numeric saturation to preserve the same perceived tint.
5. Neutral tint must not compete with semantic or brand colors.
6. White and near-black endpoints may remain less saturated when product direction requires it.

## Procedure

### 1. Define intended temperature

Tie the choice to product personality and adjacent imagery. State “cool neutral,” “warm neutral,” or “near-achromatic” rather than tweaking randomly.

### 2. Select endpoints by role

Choose the darkest readable ink and lightest subtle surface. Test them with body text, borders, panels, and imagery.

### 3. Add a restrained hue bias

Apply a consistent hue family with low enough saturation that users still perceive the colors as neutral.

### 4. Build the scale

Fill intermediate steps and compensate saturation near extremes as necessary. Avoid sudden warm/cool shifts.

### 5. Test semantic separation

Ensure neutral error text does not appear red, neutral success surfaces do not appear green, and disabled states do not become brand-tinted accidentally.

## Failure modes

- Every neutral is exact RGB equality without considering product character.
- Alternating blue and yellow biases across steps.
- Tints so strong that neutrals become semantic colors.
- Warm neutrals clashing with a deliberately cool product palette or vice versa.
- Applying tint through translucent overlays that behave differently on surfaces.
- Ignoring image and illustration temperature.

## Verification

- View the entire neutral family together and in representative pages.
- Compare against pure greys to confirm the tint is intentional but restrained.
- Test primary, secondary, and muted text roles for readable separation.
- Test surfaces, borders, disabled states, and image fallbacks.
- Confirm semantic colors remain unambiguous.
- Check light and dark extremes for washed-out temperature.

## Related modules

- [Choose a personality](../01-starting-from-scratch/04-choose-a-personality.md)
- [Define shades](./03-define-your-shades-up-front.md)
- [Saturation across lightness](./04-do-not-let-lightness-kill-saturation.md)
