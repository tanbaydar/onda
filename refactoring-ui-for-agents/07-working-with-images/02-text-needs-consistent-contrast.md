# Text Needs Consistent Contrast

## Use this module when

- Text overlays a hero, card image, video, gradient, or user-uploaded background.
- No single text color works across the image.
- Readability changes with responsive crop.
- Agents are adding text shadow without stabilizing the media.

## Objective

Reduce background variation behind text so the foreground remains readable across all images, crops, states, and viewport sizes.

## Rules

1. When both light and dark regions sit behind text, the image is the unstable variable.
2. Stabilize the image or place text on a controlled surface before endlessly changing text color.
3. Overlays, image contrast reduction, colorization, and subtle text shadow solve different aspects of the problem.
4. Text shadow is a local supplement, not a substitute for adequate overall contrast.
5. Dynamic media requires testing against worst-case content.
6. Current accessibility requirements apply to the composite rendered result.

## Procedure

### 1. Test the crop matrix

Render bright, dark, high-detail, and low-detail images at each responsive crop. Identify the region occupied by text.

### 2. Select a stabilization strategy

- **Dark overlay + light text:** suppresses bright regions but darkens the whole image.
- **Light overlay + dark text:** lifts dark regions and reduces image dominance.
- **Reduced image contrast:** compresses bright/dark range; compensate brightness as needed.
- **Colorization:** reduce contrast, desaturate, then tint/blend to align imagery with palette.
- **Controlled text surface:** place copy on a solid/tinted region when imagery must retain fidelity.
- **Soft no-offset text shadow:** local reinforcement after background stabilization.

### 3. Preserve image purpose

If the image conveys product detail or evidence, avoid treatments that obscure it. Recompose text outside the image when necessary.

### 4. Tokenize recurring treatment

Define approved overlay and text combinations. Do not tune opacity separately per image unless the content system explicitly supports art direction.

### 5. Test states

Loading, transition, missing, video frames, and error fallbacks must maintain text contrast.

## Failure modes

- White text placed directly over arbitrary photography.
- Switching between white and black text based on an unreliable average brightness.
- Heavy offset text shadows that look decorative.
- Overlay opacity so strong the image becomes irrelevant.
- Contrast checked only on the desktop crop.
- Text opacity combined with image variation.

## Verification

- Test worst-case images and every responsive crop.
- Measure composite foreground/background contrast using current project standards.
- Confirm text remains readable during loading and transitions.
- Verify image content still performs its role.
- Confirm the treatment comes from a reusable authorized system.
- Check that assistive modes preserve both text and image meaning.

## Related modules

- [Colored-background text](../02-hierarchy-is-everything/03-do-not-use-grey-text-on-colored-backgrounds.md)
- [Accessible color](../05-working-with-color/06-accessible-does-not-have-to-mean-ugly.md)
- [Use good photos](./01-use-good-photos.md)
