# Working with Images

This chapter governs photo quality, text contrast over media, scale-specific assets, screenshots/icons, and uncontrolled user uploads.

## Read order

1. [Use good photos](./01-use-good-photos.md)
2. [Text needs consistent contrast](./02-text-needs-consistent-contrast.md)
3. [Everything has an intended size](./03-everything-has-an-intended-size.md)
4. [Beware user-uploaded content](./04-beware-user-uploaded-content.md)

## Chapter doctrine

- Image quality can set the ceiling for the perceived quality of the whole interface.
- Design with production-representative imagery; placeholders hide composition and contrast problems.
- Text over images needs a stabilized background, not endless foreground-color switching.
- Vector assets can still be wrong at a different size because detail and stroke weight are scale-specific.
- Screenshots must remain legible at their rendered size or be cropped/simplified.
- User uploads require fixed slots, controlled crops, fallbacks, and background-separation treatment.

## Required state set

For every in-scope image role, inspect:

- Correct image.
- Very light image.
- Very dark image.
- High-detail image.
- Unusual aspect ratio.
- Transparent image if accepted.
- Missing source.
- Loading state.
- Failed load.
- Low-resolution source.
