# Size Is Not Everything

## Use this module when

- Primary content is oversized.
- Secondary content has become uncomfortably small.
- Many hierarchy levels are encoded as many font sizes.
- A layout feels dramatic but not controlled.

## Objective

Create hierarchy using a coordinated mix of weight, contrast, position, and spacing so text size remains readable and restrained.

## Rules

1. Do not make font size carry every hierarchy distinction.
2. Use a small number of readable text colors for primary, secondary, and tertiary roles.
3. Use a small number of weights; normal and emphasized are usually sufficient for interface text.
4. Avoid very light weights for small UI text; reduce emphasis with contrast or modest size changes instead.
5. Large text should be earned by content role, not used as a generic professionalism signal.

## Procedure

### 1. Start with a type role

Choose the role from the product type scale: body, UI, metadata, section label, title, display, or numeral. Do not begin with an arbitrary pixel value.

### 2. Adjust weight

Use a heavier approved weight for important names, values, or actions. Ensure the chosen font renders that weight distinctly and legibly.

### 3. Adjust neutral contrast

Move supporting content to an approved secondary or muted color. Do not reduce contrast below product accessibility requirements.

### 4. Use size only for structural jumps

Reserve larger steps for meaningful changes: body to section title, title to display identity, or UI label to key metric. Avoid one-pixel or two-pixel tier proliferation.

### 5. Rebalance spacing

Give primary content room and attach supporting content through proximity. Often the apparent need for a bigger heading is actually a grouping problem.

## Practical hierarchy palette

For a typical interface, begin with:

- One dark neutral for primary content.
- One quieter neutral for secondary content.
- One still-readable muted neutral for tertiary/supporting content.
- One regular text weight.
- One emphasized text weight.
- A constrained type scale with role-based steps.

This is a starting structure, not permission to override a product palette.

## Failure modes

- 48px headings beside 11px supporting text on routine application pages.
- Font sizes at nearly every pixel step.
- Weight 300 used to make small metadata “elegant.”
- Secondary text made unreadable rather than visually quiet.
- Bold, large, dark, and colored treatment stacked on the same element without need.
- Huge numerals or titles filling unused space without improving comprehension.

## Verification

- Temporarily normalize sizes within a text group; hierarchy should still be partly visible through weight, contrast, position, and spacing.
- Confirm all small text remains readable at supported devices and zoom levels.
- Inventory font sizes and weights; every one maps to a role.
- Compare the primary element one scale step smaller; keep the smaller value if hierarchy remains clear.
- Compare the secondary element at body size but quieter contrast; prefer readability over unnecessary miniaturization.

## Related modules

- [Type scale](../04-designing-text/01-establish-a-type-scale.md)
- [Balance weight and contrast](./06-balance-weight-and-contrast.md)
- [Not all elements are equal](./01-not-all-elements-are-equal.md)
