# Define Your Shades Up Front

## Use this module when

- New components generate lighter/darker colors on demand.
- The palette contains many nearly identical variations.
- Building a neutral, primary, semantic, or data color scale.
- Agents repeatedly use alpha, `lighten`, or `darken` functions.

## Objective

Create a finite, intentional shade family whose steps cover real roles and prevent component-level color drift.

## Rules

1. Define explicit shade values; do not generate production variants opportunistically.
2. Start with a useful base, then select the lightest and darkest role endpoints.
3. Fill gaps through visual comparison, not blind mathematical interpolation.
4. A family typically needs enough steps to avoid compromise but not enough to create indecision.
5. Adjust the system after real use, but resist adding shades casually.
6. Shade numbers indicate order, not guaranteed perceptual distance or semantic role.

## Procedure

### 1. Choose the base

For primary/accent families, start with a color that works in its central product role, often a standard control, mark, or data series. For neutrals, the middle is less important than functional endpoints.

### 2. Choose endpoints in context

- Dark endpoint: test as text or a high-contrast state where the family owns that role.
- Light endpoint: test as a tinted background or subtle selected/alert surface.

Do not choose endpoints solely in a palette tool.

### 3. Fill major midpoints

Select colors that feel like clear compromises between endpoint and base. Then fill remaining gaps. Around nine steps can be a useful working structure, but real role needs decide the count.

### 4. Assign semantic aliases

Map scale steps to roles such as `action`, `action-hover`, `action-subtle`, `danger-text`, or `danger-surface`. Do not rely on numeric names alone in product code when semantics matter.

### 5. Test interaction pairs

Validate resting, hover, pressed, focus, selected, disabled, foreground, background, and border combinations. Adjacent steps must remain distinguishable.

### 6. Tune with restraint

Real usage may reveal that a shade is too dull, close, bright, or dark. Change the shared shade when its role is wrong; add a shade only when a genuinely distinct reusable role exists.

## Failure modes

- CSS functions producing a new variation per component.
- Linear numeric interpolation treated as finished design.
- Building ten steps that are indistinguishable at one end.
- Adding `brand-550` for one button.
- Choosing endpoints without testing text and surface roles.
- Changing a shared shade to fix one surface while breaking its other roles.

## Verification

- Display the family as swatches and in actual components.
- Test dark text, subtle background, border, and base action roles where relevant.
- Compare adjacent steps for perceptible distinction.
- Compute required contrast for every semantic pair.
- Search for local color literals after migration within task scope.
- Document exceptions and do not expand to unrelated surfaces.

## Related modules

- [Reason about color](./01-reason-about-color-with-hsl.md)
- [Saturation across lightness](./04-do-not-let-lightness-kill-saturation.md)
- [Limit choices](../01-starting-from-scratch/05-limit-your-choices.md)
