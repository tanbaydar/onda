# Decorate Your Backgrounds

## Use this module when

- Foundations are complete but a large surface needs differentiation or atmosphere.
- Separating major page sections through surface treatment.
- Considering gradients, patterns, shapes, or illustrations.
- Product authority permits decorative backgrounds.

## Objective

Add controlled visual interest behind content without harming readability, hierarchy, performance, or product character.

## Rules

1. Background treatment must remain behind the content in both contrast and z-order.
2. Use decoration sparingly, usually on selected sections rather than the entire product.
3. For restrained gradients, nearby hues often feel more coherent than distant hues; the source suggests roughly within 30 degrees as a heuristic.
4. Patterns and illustrations require low enough contrast not to compete with text or controls.
5. Decorative assets must not convey required information.
6. Respect product anti-goals; a general technique is not permission to introduce gradients or illustration.
7. Define responsive crop/repetition and performance behavior.

## Procedure

### 1. Name the background job

- Distinguish a section.
- Establish product atmosphere.
- Support a hero or empty state.
- Create continuity across a long page.
- Reinforce category or identity where authorized.

### 2. Try the least complex method

Evaluate in order:

1. Existing alternate surface color.
2. Restrained nearby-hue gradient.
3. Low-contrast repeating pattern.
4. Edge pattern or localized shape.
5. Purpose-built illustration.

Stop at the first method that solves the named job.

### 3. Protect content zones

Keep high-detail or high-contrast areas away from text and controls. Use masks, gradients, or placement constraints when needed.

### 4. Define responsive behavior

Specify crop, repeat, anchor point, density, and whether decoration disappears at narrow widths.

### 5. Test accessibility and performance

Check composite contrast, forced colors, motion if animated, image loading, and cumulative layout behavior.

## Failure modes

- Decorating every section differently.
- High-contrast patterns behind body text.
- Distant-hue gradients that create unintended emphasis.
- Large assets with no responsive or performance plan.
- Background illustration carrying essential instructions.
- Adding decoration to compensate for empty content or weak hierarchy.

## Verification

- Disable the decoration; structure and meaning remain complete.
- Text/control contrast passes in every decorated region.
- Decoration stays subordinate at reduced thumbnails.
- Narrow and wide crops are intentional.
- Asset loading does not shift content.
- Product authority explicitly allows the treatment.

## Related modules

- [Choose a personality](../01-starting-from-scratch/04-choose-a-personality.md)
- [Text over images](../07-working-with-images/02-text-needs-consistent-contrast.md)
- [Flat depth](../06-creating-depth/04-even-flat-designs-can-have-depth.md)
