# Use Fewer Borders

## Use this module when

- Cards, sections, rows, controls, and panels are all outlined.
- The interface resembles a spreadsheet of boxes.
- Borders are used to compensate for weak spacing or surface hierarchy.
- A design feels busy despite a restrained palette.

## Objective

Use the least intrusive separation method that accurately communicates grouping and interaction.

## Rules

1. Do not reach for a border before testing spacing and background separation.
2. Use borders when the boundary itself carries functional meaning: fields, focus, selection, table structure, or required containment.
3. Use shadows only when elevation is real and authorized.
4. Adjacent surface colors can separate regions without outlines.
5. Extra spacing can separate unrelated groups with no added visual element.
6. Repeating dividers may be appropriate when they improve row tracking, but full boxes are rarely required for every item.
7. Removing borders must not reduce perceivable control boundaries below current accessibility requirements.

## Separation decision tree

1. **Are the elements unrelated groups?** Increase space.
2. **Are they adjacent regions with different roles?** Consider approved surface colors.
3. **Is one physically above the other?** Consider elevation/shadow if authorized.
4. **Is repeated row tracking needed?** Consider one subtle divider between siblings.
5. **Is the boundary itself interactive or semantic?** Use an approved border.
6. **Does focus/selection require a clear outline?** Preserve the functional indicator.

## Procedure

### 1. Inventory borders

Classify each as structural, interactive, state, focus, decorative, or compensating.

### 2. Remove compensating/decorative borders in a test rendering

Assess grouping. If it collapses, repair proximity and surface organization first.

### 3. Choose one separator per relationship

Avoid combining border, shadow, alternate background, and large gap unless each has a distinct job.

### 4. Preserve controls

Inputs, buttons, menus, and focus indicators may require perceivable boundaries. Follow product accessibility authority.

### 5. Check dense views

Tables and long lists may legitimately use dividers. Prefer consistent sibling separators over boxed rows.

## Failure modes

- Border around every card plus shadow and alternate background.
- Nested boxes creating double borders.
- Removing input boundaries for visual minimalism.
- Hairlines too faint to perform required control separation.
- Large gaps plus borders separating the same groups.
- Borders inserted because spacing tokens are inconsistent.

## Verification

- Every remaining border has a named structural or interaction job.
- Grouping remains clear with decorative borders removed.
- Control and focus boundaries satisfy current requirements.
- Dense lists are trackable without boxed repetition.
- No double separators appear at nested edges.
- The whole page has lower visual noise without loss of comprehension.

## Related modules

- [Avoid ambiguous spacing](../03-layout-and-spacing/06-avoid-ambiguous-spacing.md)
- [Flat depth](../06-creating-depth/04-even-flat-designs-can-have-depth.md)
- [Balance weight and contrast](../02-hierarchy-is-everything/06-balance-weight-and-contrast.md)
