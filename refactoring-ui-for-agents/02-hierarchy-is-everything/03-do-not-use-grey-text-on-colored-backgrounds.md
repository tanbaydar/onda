# Do Not Use Grey Text on Colored Backgrounds

## Use this module when

- Text appears on a colored surface, image, gradient, or tinted panel.
- Secondary text is implemented as grey or low-opacity white over color.
- Text looks washed out, disabled, or inconsistent across backgrounds.

## Objective

Create intentional hierarchy on colored surfaces by choosing foreground colors relative to the surface rather than reusing grey-on-white logic.

## Rules

1. Hierarchy comes from relative contrast with the local background, not from “grey” as an absolute category.
2. Choose foreground colors for the actual surface and validate each pair.
3. Avoid low-opacity foreground text over images or patterns; the background will contaminate the text.
4. Preserve the background hue family when product style calls for tonal text, while adjusting lightness and saturation deliberately.
5. Accessibility requirements outrank aesthetic hierarchy.

## Procedure

### 1. Identify the background class

- Solid light color.
- Solid dark color.
- Gradient.
- Image or pattern.
- Dynamic/user-provided media.

### 2. Select the primary foreground

Use the product’s approved accessible foreground for that surface. Do not assume white is always correct on brand color or black is always correct on a tint.

### 3. Derive secondary foreground intentionally

Choose an opaque color that moves toward the background while remaining readable. Where appropriate, preserve or slightly rotate the hue rather than mixing in neutral grey.

### 4. Test all underlying variations

For gradients and media, test the brightest, darkest, and most detailed regions. If the foreground cannot remain reliable, stabilize the background with an overlay, image treatment, or separate text surface.

### 5. Reserve opacity for controlled contexts

Opacity may be acceptable when the background is uniform and the resulting composite color is intentional and tested. Prefer explicit tokens for recurring pairs.

## Failure modes

- `color: grey` on a saturated panel.
- White text at reduced opacity that appears disabled.
- Translucent text over a photograph, causing local color bleed.
- Reusing a muted-on-white token on a dark surface.
- Adjusting only lightness until primary and secondary text become indistinguishable or inaccessible.

## Verification

- Inspect computed foreground/background pairs, not source colors in isolation.
- Validate required contrast using the project’s current accessibility standard.
- Compare text over every gradient stop or plausible crop.
- Confirm secondary text looks intentionally quieter, not inactive.
- Disable the background image; verify that token semantics still make sense for the surface.
- Test forced-colors or high-contrast modes when required by the product.

## Related modules

- [Accessible color](../05-working-with-color/06-accessible-does-not-have-to-mean-ugly.md)
- [Text over images](../07-working-with-images/02-text-needs-consistent-contrast.md)
- [Reason about color](../05-working-with-color/01-reason-about-color-with-hsl.md)
