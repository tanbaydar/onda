# Emulate a Light Source

## Use this module when

- Controls or surfaces should appear raised or inset.
- Borders and shadows imply inconsistent directions.
- Skeuomorphic cues are authorized but look arbitrary.
- Building a depth token system.

## Objective

Make dimensional cues internally consistent by modeling light from a stable direction, usually above the interface.

## Rules

1. Select one primary light direction for the system.
2. Upward-facing edges are generally lighter; occluded lower regions are darker for raised elements.
3. Inset elements reverse the relevant edge and shadow relationships.
4. Choose highlight colors deliberately; translucent white can desaturate colored surfaces.
5. Keep effects restrained. The goal is spatial recognition, not photorealism.
6. Do not add dimensional cues where the product’s flat language prohibits them.

## Procedure

### 1. Define the element profile

Is it flat, slightly raised, highly elevated, pressed, or inset? Do not begin by choosing blur and opacity.

### 2. Model the light interaction

For a slightly raised control under overhead light:

- A subtle lighter top edge may reveal the upward-facing plane.
- A compact darker shadow below suggests the control blocks light.

For an inset well or field:

- A darker inner top edge suggests occlusion.
- A subtle lighter lower inner edge can reveal the upward-facing lip.

### 3. Use product tokens

Map the model to existing border, highlight, and shadow tokens. Do not create a unique recipe per component.

### 4. Define interaction transitions

A pressed element may reduce or remove raised shadow and adopt a more inset treatment. State changes should be immediate and physically coherent.

### 5. Inspect on all surfaces

The same semi-transparent effect composites differently over colored or image backgrounds. Validate every approved surface.

## Failure modes

- Top and bottom shadows both suggesting light from below.
- Raised and inset components using identical shadow recipes.
- Broad soft shadows on elements meant to sit close to the surface.
- White overlays washing saturation from a colored button.
- Photorealistic beveling in an otherwise flat system.
- Different components implying different light sources.

## Verification

- Sketch or state the light direction and object profile.
- Compare resting, hover, pressed, and disabled states.
- Inspect effects on every approved background.
- Confirm blur and offset match the intended proximity.
- Verify the effect is unnecessary for semantic comprehension and does not weaken focus.
- Remove details until the depth cue is just sufficient.

## Related modules

- [Elevation system](./02-use-shadows-to-convey-elevation.md)
- [Two-part shadows](./03-shadows-can-have-two-parts.md)
- [Flat depth](./04-even-flat-designs-can-have-depth.md)
