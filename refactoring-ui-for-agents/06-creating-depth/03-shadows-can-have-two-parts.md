# Shadows Can Have Two Parts

## Use this module when

- A single shadow is either too vague or too harsh.
- Building refined low-to-medium elevation tokens.
- Shadow edges need definition without darkening a broad area.
- Higher elevation shadows look unrealistically dense near the object.

## Objective

Control direct-light cast shadow and tight ambient-occlusion shadow as separate components.

## Rules

1. The broad component is softer, lighter, more offset, and represents cast shadow from direct light.
2. The tight component is darker, sharper, and closer to the object, representing limited ambient light near contact.
3. As elevation increases, the tight contact component should weaken or disappear.
4. Both components must follow the system’s light direction.
5. Two shadows are justified by distinct jobs, not by random layering.

## Procedure

### 1. Start from semantic elevation

Choose the z-level first. Do not begin with a copied shadow recipe.

### 2. Add the cast component

Set broad offset and blur appropriate to the apparent height. Keep opacity restrained enough that the shadow does not become a visible halo.

### 3. Add the contact component

Use a smaller blur and offset near the lower edge. Make it distinct at low elevation and progressively quieter as the object lifts.

### 4. Compare against one-part version

The two-part version should improve edge definition and realism without appearing heavier. If it does not, retain the simpler system.

### 5. Encode in elevation tokens

Do not expose independent arbitrary shadow layers to every component. Components request elevation roles.

## Failure modes

- Two equally broad shadows that simply darken the surface.
- Strong contact shadow at high elevation.
- Offsets pointing in different directions.
- Copying fashionable shadow values without a z-axis model.
- Multiple shadow colors inconsistent with surface temperature.
- Using two parts where a border or single shadow is clearer.

## Verification

- Temporarily toggle each part; each performs a distinct visible job.
- Compare low, middle, and high elevation levels together.
- Contact shadow decreases with height.
- Cast shadow expands and softens consistently.
- No dirty halo or clipped edge appears.
- Shadow tokens remain limited and reusable.

## Related modules

- [Emulate a light source](./01-emulate-a-light-source.md)
- [Elevation system](./02-use-shadows-to-convey-elevation.md)
- [Tinted greys](../05-working-with-color/05-greys-do-not-have-to-be-grey.md)
