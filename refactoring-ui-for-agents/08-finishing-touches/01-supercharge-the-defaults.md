# Supercharge the Defaults

## Use this module when

- Foundations are correct but generic browser/UI defaults feel under-resolved.
- Lists, quotations, links, checkboxes, or radio controls need product character.
- Adding a new decorative element is being considered.

## Objective

Increase polish by enhancing elements already required by the content instead of adding unrelated decoration.

## Rules

1. Prefer meaningful enhancement of existing content over new ornamental objects.
2. The enhancement must preserve semantic HTML and interaction behavior.
3. Use product tokens and iconography; do not create an isolated visual language.
4. Custom controls must preserve native semantics, focus, target size, keyboard operation, disabled state, and high-contrast behavior.
5. Enhancements remain subordinate to the content’s hierarchy.
6. Do not replace familiar cues with obscure custom visuals.

## Candidate transformations

- Replace generic bullet markers with a small meaningful icon when every list item shares that semantic.
- Promote a quotation mark into a restrained visual anchor for testimonials or editorial quotes.
- Apply an approved custom underline or weight treatment to important links.
- Style selected checkbox/radio states with the product’s assigned action or selection color.
- Improve a native default’s spacing, typography, and focus treatment without hiding its function.

## Procedure

### 1. Identify an existing required element

Choose a list marker, quotation, link, input, divider, or state indicator already present in the content.

### 2. Name the enhancement job

Does it improve scan, reinforce meaning, clarify selection, or carry product personality? If it only fills space, reject it.

### 3. Select an authorized visual channel

Use the existing icon family, palette role, shape grammar, type role, or border treatment.

### 4. Preserve interaction and fallback

Keep semantic elements and accessible names. Test without CSS, with keyboard, forced colors, and reduced motion when relevant.

### 5. Compare with the default

The custom version must materially improve comprehension or coherent personality. If it adds noise, keep the simpler default.

## Failure modes

- Decorative icons unrelated to list meaning.
- Custom checkboxes with lost keyboard or focus behavior.
- Oversized quotation marks competing with the quote.
- Special link treatment used everywhere.
- New colors or icon styles introduced for one component.
- Styling native controls without testing platform and accessibility modes.

## Verification

- Semantics and keyboard behavior remain intact.
- The enhancement uses existing system tokens/assets.
- Content remains primary.
- The state is understandable without color alone.
- The custom treatment works at all in-scope sizes and themes.
- Removing the enhancement does not reveal a hidden foundation defect.

## Related modules

- [Do not rely on color alone](../05-working-with-color/07-do-not-rely-on-color-alone.md)
- [Intended size](../07-working-with-images/03-everything-has-an-intended-size.md)
- [Choose a personality](../01-starting-from-scratch/04-choose-a-personality.md)
