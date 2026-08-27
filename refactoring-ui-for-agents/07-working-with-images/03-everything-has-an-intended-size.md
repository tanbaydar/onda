# Everything Has an Intended Size

## Use this module when

- Scaling icons, logos, screenshots, raster images, or illustrations.
- A vector icon looks chunky when enlarged or noisy when reduced.
- Product screenshots are unreadable in marketing or onboarding layouts.
- One source asset is reused at every size.

## Objective

Use or create assets whose detail, stroke weight, crop, and composition are designed for their rendered size.

## Rules

1. Raster assets should not be enlarged beyond useful source resolution.
2. Vector fidelity does not guarantee visual suitability at another size.
3. Small icons enlarged dramatically lack the detail and proportion expected at display scale.
4. Large detailed icons reduced to tiny sizes become muddy; create simplified small-size variants.
5. Full-interface screenshots should not be shrunk until functional text becomes illegible.
6. Crop or simplify when the available display size cannot support all source detail.

## Procedure

### 1. Record rendered sizes

List CSS dimensions, device-pixel density needs, and responsive variants for each asset role.

### 2. Inspect source intent

Determine the size for which the icon or illustration was drawn. Examine stroke width, corner radius, internal whitespace, and detail density.

### 3. Choose a scale strategy

- Use a size-specific asset.
- Redraw or simplify for the target size.
- Place a small icon inside a larger colored/neutral container rather than enlarging it.
- Crop a screenshot to the relevant feature.
- Capture a smaller responsive layout so UI text remains legible.
- Replace a tiny full screenshot with a simplified schematic when detail is not meant to be read.

### 4. Provide responsive sources

Use suitable raster densities and formats. Art-direct crops when composition changes materially.

### 5. Validate at actual display size

Do not judge a 16px icon zoomed to 800%. Inspect normal rendering on target displays.

## Failure modes

- Enlarging a 16px system icon into a feature illustration.
- Shrinking a detailed logo into a favicon.
- Full desktop screenshot displayed so small that text is only a few pixels high.
- Assuming SVG means infinitely appropriate.
- Browser downscaling expected to simplify detail intelligently.
- One raster source stretched across all density classes.

## Verification

- Inspect assets at 100% CSS size on representative displays.
- Confirm raster resolution is sufficient but not wastefully excessive.
- Check small icons for crispness and recognizable silhouette.
- Check large icons/illustrations for appropriate detail.
- Verify screenshot text is readable or intentionally abstracted.
- Confirm favicon/app-icon and responsive image variants exist where required.

## Related modules

- [Balance weight and contrast](../02-hierarchy-is-everything/06-balance-weight-and-contrast.md)
- [Use good photos](./01-use-good-photos.md)
- [Spacing and sizing system](../03-layout-and-spacing/02-establish-a-spacing-and-sizing-system.md)
