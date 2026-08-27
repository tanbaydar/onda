# Separate Visual Hierarchy from Document Hierarchy

## Use this module when

- Heading elements look too large merely because they are `h1`, `h2`, or `h3`.
- A section title competes with the content it introduces.
- Developers consider changing semantic markup to obtain a visual style.
- Visually hidden headings or labels may improve navigation for assistive technology.

## Objective

Choose HTML semantics for document meaning and accessibility while styling each element for its actual visual role in the interface.

## Rules

1. Semantic level and visual size are independent systems.
2. Preserve a logical heading outline even when a heading is visually quiet.
3. Section titles in application interfaces often behave as supporting labels, not display headlines.
4. Use CSS classes or component roles for appearance; do not choose HTML elements for browser default styling.
5. A visually hidden heading is valid when the content is self-identifying visually but still benefits from semantic navigation.

## Procedure

### 1. Establish the semantic outline

Determine page title, section hierarchy, landmarks, labels, and relationships based on content meaning. Do not skip levels to achieve smaller defaults.

### 2. Assign visual roles independently

Map semantic elements to product type roles such as page identity, section label, card title, supporting label, or visually hidden context.

### 3. Prioritize content over labels

If a heading merely names a group whose contents should dominate, use a restrained approved style. Let position and spacing establish the section.

### 4. Preserve assistive context

When hiding a heading visually, ensure it remains in the accessibility tree and does not duplicate or confuse visible labels.

### 5. Test source and rendered order

Responsive CSS must not create a visual sequence that materially conflicts with focus or reading order.

## Failure modes

- Every `h1` is a huge display heading regardless of context.
- Using `div` or `span` because a semantic heading “looks wrong.”
- Skipping heading levels to obtain smaller text.
- Styling every section title more prominently than its content.
- Visually reordering content without correcting keyboard or screen-reader sequence.
- Hiding headings that are necessary for sighted comprehension.

## Verification

- Inspect the document outline and landmarks.
- Disable CSS; the semantic reading order remains understandable.
- Inspect the styled surface; headings receive emphasis appropriate to their role.
- Navigate by headings with assistive tooling when required by scope.
- Confirm visually hidden content uses a robust utility and remains available to assistive technology.
- Confirm responsive reordering does not separate semantics from visible task order.

## Related modules

- [Labels are a last resort](./05-labels-are-a-last-resort.md)
- [Type scale](../04-designing-text/01-establish-a-type-scale.md)
- [Feature before layout](../01-starting-from-scratch/01-feature-before-layout.md)
