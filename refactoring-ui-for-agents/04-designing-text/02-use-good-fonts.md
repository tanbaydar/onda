# Use Good Fonts

## Use this module when

- Selecting or replacing a UI, display, or prose typeface.
- A font looks distinctive but performs poorly in controls or body text.
- Too many families or weights are loaded.
- Product personality is being defined.

## Objective

Select typefaces that remain legible at intended sizes, provide the necessary styles, render reliably, and support the product’s character without making typography itself the usability problem.

## Rules

1. For functional UI, a neutral, highly legible sans serif is the safest baseline.
2. System fonts are valid when reliability and familiarity outweigh distinctiveness.
3. A family with a broad, well-made weight/style range is stronger evidence of suitability than one isolated style, but style count is a heuristic, not a guarantee.
4. Body/UI fonts need clear forms, adequate x-height, and spacing intended for small sizes.
5. Condensed or display-oriented fonts should not be forced into long prose or small controls.
6. Limit family roles and define where expressive faces may appear.
7. Verify actual glyph coverage, licensing, loading, fallback, and performance in the project.

## Procedure

### 1. Define text roles

List UI, prose, display, numeric, code, and multilingual requirements. A product may use one family for all roles or a small coordinated set.

### 2. Create a safe shortlist

Prioritize proven families, system stacks, or typefaces used successfully in comparable high-quality contexts. Avoid novelty-first searching across thousands of options.

### 3. Inspect technical fitness

Check:

- Required weights and italics.
- Numeral styles and punctuation.
- Glyph coverage and language support.
- Legibility at smallest intended size.
- Variable-font axes if used.
- File size, loading strategy, and fallback metrics.
- Licensing and repository policy.

### 4. Render product content

Use real navigation labels, long names, form text, body copy, numerals, and error messages. Do not evaluate only a specimen sentence.

### 5. Assign strict roles

Document which family owns functional UI, long-form text, and display identity. If one family covers everything, define weight and scale constraints instead.

### 6. Test failure and fallback

Inspect loading swap, missing font, slow connection, and platform rendering if relevant. Layout must not collapse when fallback metrics differ.

## Failure modes

- Choosing a font because a single hero headline looks attractive.
- Using a short-x-height or condensed face for small UI text.
- Loading many families for isolated decorative moments.
- Assuming popularity proves project fit.
- Using synthetic bold or italics when real styles are required.
- Ignoring non-Latin content, diacritics, numerals, or localization.
- Failing to define fallback and loading behavior.

## Verification

- Every family has a named role and usage boundary.
- Small UI text remains legible at target devices.
- Long prose is comfortable at intended line length and line height.
- Required weights are real, visually distinct, and not excessive.
- Long labels, numerals, punctuation, and target languages render correctly.
- Loading and fallback do not cause unacceptable layout shift.

## Related modules

- [Choose a personality](../01-starting-from-scratch/04-choose-a-personality.md)
- [Type scale](./01-establish-a-type-scale.md)
- [Letter spacing](./08-use-letter-spacing-effectively.md)
