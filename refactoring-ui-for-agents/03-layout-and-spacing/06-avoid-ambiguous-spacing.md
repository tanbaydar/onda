# Avoid Ambiguous Spacing

## Use this module when

- Users may misread which label belongs to which input.
- Sections, list items, metadata, or horizontal controls blend together.
- Borders are being added because proximity does not communicate groups.
- Whitespace feels abundant but relationships remain unclear.

## Objective

Use proximity to communicate ownership: space around a group must be clearly greater than space within it.

## Rules

1. Related elements sit closer together than unrelated elements.
2. Inter-group spacing must be perceptibly larger than intra-group spacing.
3. The rule applies vertically and horizontally.
4. Borders and background fills may reinforce groups but should not repair poorly chosen spacing by default.
5. Repeating items need internal cohesion and external separation.
6. Spacing relationships must survive responsive reflow.

## Procedure

### 1. Draw the grouping tree

Identify parent/child and sibling relationships: page → section → group → item → label/value. Every gap should correspond to one edge in this tree.

### 2. Assign spacing tiers

Use smaller tokens inside items, medium tokens between sibling items, and larger tokens between groups or sections. Exact tokens come from the product system.

### 3. Test without separators

Temporarily remove borders and fills. If grouping collapses, adjust proximity first. Restore only separators that communicate an additional structural need.

### 4. Check common ambiguity patterns

- Label-to-control gap equals control-to-next-label gap.
- Heading has equal space above and below.
- List-item gap equals wrapped line height.
- Icon is equidistant from its label and neighboring control.
- Action row sits closer to the next section than the content it controls.

### 5. Re-evaluate after wrapping

Long labels, multiline content, and mobile stacking can invert intended relationships. Use row/column gaps and scoped margins that follow structure rather than source-order accidents.

## Failure modes

- Uniform vertical rhythm applied to every relationship.
- Large internal card padding but minimal gap between cards.
- Equal spacing around section headings.
- Adding boxes around groups instead of fixing proximity.
- Margin collapse or selector dependence causing state-specific grouping errors.
- Reordered mobile content retaining desktop-only gaps.

## Verification

- A viewer can outline groups without reading the text.
- Labels cannot plausibly be assigned to the wrong control.
- Wrapped list items remain distinct from neighboring items.
- Section headings attach more strongly to following content than previous content.
- Border removal does not destroy basic grouping.
- Sparse and dense data preserve the same relationship hierarchy.

## Related modules

- [Start with too much whitespace](./01-start-with-too-much-white-space.md)
- [Use fewer borders](../08-finishing-touches/05-use-fewer-borders.md)
- [Not all elements are equal](../02-hierarchy-is-everything/01-not-all-elements-are-equal.md)
