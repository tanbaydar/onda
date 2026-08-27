# Labels Are a Last Resort

## Use this module when

- Presenting profile details, metadata, specifications, metrics, or database records.
- The interface repeats `Label: value` rows.
- Every field receives equal emphasis because labels dominate the layout.
- Designing a table, card, detail page, or dashboard.

## Objective

Present data through recognizable format, context, natural language, and hierarchy before adding explicit labels.

This rule does not apply to form labels, which remain necessary for accessible input identification.

## Rules

1. Remove a display label when the value’s format and context identify it reliably.
2. Prefer natural combined phrases when a bare value is ambiguous.
3. When labels are necessary, usually treat them as supporting content.
4. Emphasize labels when users are primarily scanning for category names, such as technical specifications.
5. Never trade clarity or accessibility for visual minimalism.

## Procedure

For each data item, ask in order:

1. **Is the format self-identifying?** Email addresses, phone numbers, prices, dates, and URLs often are.
2. **Does placement provide enough context?** A role below a person’s name may need no “Role” label.
3. **Can label and value become natural language?** Prefer “12 left in stock” to `In stock: 12` when it improves clarity.
4. **Are several similar values being compared?** Labels may be necessary.
5. **Will users scan for the label rather than the value?** Emphasize the label modestly.
6. **Would assistive technology lose necessary context?** Preserve semantic relationships even if the visible label changes.

## Layout patterns

- **Identity stack:** primary name/value first; contextual details beneath without labels.
- **Natural metric:** value plus unit or noun, such as “3 bedrooms.”
- **Supporting label:** small or quieter label above a prominent value.
- **Specification row:** stronger label and readable, slightly quieter value aligned for scan.
- **Table header:** explicit labels when columns require comparison, sorting, or interpretation.

## Failure modes

- Mechanical lists where every row has the same visual weight.
- Removing labels from genuinely ambiguous values.
- Hiding meaningful context only visually but not semantically connected.
- Treating labels as large headings while the data recedes too far.
- Using placeholders as form labels.
- Combining label and value into unnatural or localized-unfriendly copy.

## Verification

- Hide the labels temporarily; identify which values remain clear.
- Test with unfamiliar but representative data, not only obvious samples.
- Ask whether the user scans for a value or a category name.
- Check localization and pluralization for combined phrases.
- Verify accessible names and relationships for forms, descriptions, tables, and definition lists.
- Confirm the resulting hierarchy gives important data more prominence than supporting words.

## Related modules

- [Hierarchy](./01-not-all-elements-are-equal.md)
- [Alignment](../04-designing-text/07-align-with-readability-in-mind.md)
- [Think outside the box](../08-finishing-touches/06-think-outside-the-box.md)
