# Beware User-uploaded Content

## Use this module when

- Users upload avatars, product images, event art, covers, attachments, or gallery media.
- Intrinsic ratios destabilize layout.
- Image backgrounds blend into the interface background.
- Media quality and composition cannot be curated.

## Objective

Protect layout and identity from uncontrolled media through stable slots, intentional crops, fallbacks, and subtle edge separation.

## Rules

1. Do not let intrinsic aspect ratio determine repeated-list geometry.
2. Center-crop or contain media in fixed, role-specific slots.
3. Choose crop mode from content meaning: `cover` for photographic identity where cropping is acceptable; `contain` where the whole artifact matters.
4. Provide missing, loading, failed, transparent, and low-quality states.
5. Prevent same-color background bleed with a subtle inner separation treatment when needed.
6. Borders may clash with image colors; a subtle inset shadow or translucent inner ring can be less intrusive if authorized.
7. Preserve user control or focal-point information when the product supports it.

## Procedure

### 1. Define each media role

For avatar, thumbnail, hero, gallery, attachment, or logo, specify ratio, dimensions, crop behavior, focal point, radius/shape, and fallback.

### 2. Stabilize the container

Reserve aspect ratio and dimensions before load. Prevent cumulative layout shift and row-height variation.

### 3. Apply crop policy

Use centered cover only as a baseline. Faces, text-heavy posters, or products may require focal data, object-position rules, or contain behavior.

### 4. Protect edges

Test white-on-white, black-on-black, transparent PNGs, and images matching the surface. Add an approved inset separator only if shape is lost.

### 5. Handle hostile inputs

Test portrait, landscape, extreme panorama, tiny image, corrupted image, animated media if accepted, and unsupported format.

### 6. Preserve semantics and safety

Use appropriate alt-text policy, moderation/security constraints, and upload feedback defined by the product. Visual rules do not authorize changes to upload behavior.

## Failure modes

- Masonry-like row instability where consistent scanning is required.
- `object-fit: cover` cropping critical text or faces indiscriminately.
- Broken-image icons exposed in production.
- Borders around every image regardless of need.
- Transparent assets disappearing against the surface.
- Layout shift while dimensions are unknown.
- Placeholder treatment more prominent than real media.

## Verification

- Run a matrix of aspect ratios, resolutions, and background colors.
- Inspect missing/loading/error states.
- Confirm stable layout before and after load.
- Check subject preservation and focal points.
- Verify edge separation is subtle and only present where needed.
- Test the same asset across every slot size that reuses it.

## Related modules

- [Intended size](./03-everything-has-an-intended-size.md)
- [Overlap elements](../06-creating-depth/05-overlap-elements-to-create-layers.md)
- [Use good photos](./01-use-good-photos.md)
