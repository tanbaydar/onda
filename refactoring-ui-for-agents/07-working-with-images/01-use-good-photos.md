# Use Good Photos

## Use this module when

- Photography is a major part of the product or page hierarchy.
- Designing a hero, catalog, profile, editorial, property, food, travel, or social surface.
- Placeholder images are being used during implementation.
- The interface looks unprofessional despite sound layout and typography.

## Objective

Use imagery whose composition, lighting, resolution, subject, and consistency support the intended display role.

## Rules

1. Low-quality imagery cannot be repaired by polished chrome.
2. Use professional photography when the product requires specific subjects or controlled brand expression.
3. Use high-quality licensed stock when the need is generic and appropriate.
4. Design with production-representative images early enough to reveal real crop and contrast constraints.
5. Define quality, ratio, and content requirements for image sources.
6. Do not assume casual future replacements will match carefully chosen placeholders.

## Procedure

### 1. Define the image job

Is the image identity, evidence, atmosphere, instruction, product detail, background, or decoration? The job determines required resolution, crop tolerance, alternative text, and prominence.

### 2. Define capture/source requirements

Record:

- Subject and framing.
- Lighting and background.
- Orientation/aspect ratio.
- Minimum useful resolution and density.
- Color/temperature consistency.
- Rights and attribution.
- Whether text may appear over it.

### 3. Assemble a representative set

Include best case, typical case, difficult crop, bright/dark extremes, and missing imagery. For user-generated systems, include genuinely uncontrolled samples.

### 4. Design the crop system

Choose fixed aspect ratios or intrinsic presentation according to content. Use focal-point or art-direction data where product infrastructure supports it.

### 5. Define fallbacks

Missing imagery must not create collapsed layout, broken icons, or misleading decoration. Use product-authorized placeholders, initials, neutral surfaces, or designed absence.

## Failure modes

- Designing around a perfect stock image, then shipping uncontrolled photos.
- Low-resolution images stretched into prominent slots.
- Mixed photographic styles producing inconsistent product identity.
- Placeholder gradients that hide real crop and contrast issues.
- Cropping faces or key content because focal points are unknown.
- Decorative photos receiving meaningful alt text or informative photos receiving none.

## Verification

- Inspect a representative image corpus in every slot size.
- Check high-density displays and responsive sources.
- Verify crops preserve key subjects.
- Test missing/loading/error behavior.
- Confirm image role determines correct alternative text treatment.
- Confirm asset licensing and repository policy are satisfied.

## Related modules

- [Text contrast](./02-text-needs-consistent-contrast.md)
- [Intended size](./03-everything-has-an-intended-size.md)
- [User uploads](./04-beware-user-uploaded-content.md)
