# Think Outside the Box

## Use this module when

- A familiar component pattern wastes space or flattens hierarchy.
- Dropdowns, tables, radio groups, filters, or cards feel mechanically generic.
- Constraints have produced a competent but inflexible interface.
- The task explicitly authorizes exploration.

## Objective

Recompose familiar controls around their actual content and task while preserving semantics, accessibility, and product-system coherence.

## Rules

1. Component conventions are starting points, not visual laws.
2. Break visual conventions only when the alternative improves task performance, hierarchy, or comprehension.
3. Preserve familiar interaction semantics and accessibility unless explicit product research authorizes a new model.
4. Combine related data when it improves scanning and sorting is not compromised.
5. Use richer option presentations when choices need supporting context.
6. Exploration is constrained by product personality and existing systems.

## Procedure

### 1. State the conventional limitation

Examples:

- Dropdown list cannot show enough decision context.
- Table has too many narrow columns and equal emphasis.
- Radio labels require description and comparison.
- Card grid hides natural reading order.

### 2. Preserve the user contract

Document expected keyboard behavior, selection model, focus, sorting/filtering, responsive behavior, and assistive semantics.

### 3. Explore structural alternatives

- Group menu items into labeled sections or columns.
- Add supporting text/icons to options.
- Combine related unsortable table fields into one richer cell.
- Use images or status markers where data benefits.
- Present important radio options as selectable panels while retaining radio semantics.

### 4. Compare against the conventional version

Measure scan time, comprehension, space, error risk, and interaction cost. Novelty alone is not a benefit.

### 5. Re-enter the design system

Use existing type, spacing, color, shape, and state primitives. A new anatomy should still belong to the product.

## Failure modes

- Redesigning a standard control only to look unique.
- Selectable cards with lost radio semantics or keyboard behavior.
- Combining sortable table columns and removing a needed comparison operation.
- Menus so rich they become miniature dashboards.
- Unconventional layout with no mobile or dense-content plan.
- Adding imagery/color that competes with choice labels.

## Verification

- The alternative solves a named limitation.
- All original interaction and accessibility requirements remain satisfied.
- Representative users or task-based review can still identify how to operate it.
- Sorting, filtering, selection, and focus behavior are complete.
- Dense, sparse, long-copy, and mobile cases work.
- The result uses existing design-system vocabulary.

## Related modules

- [Labels are a last resort](../02-hierarchy-is-everything/05-labels-are-a-last-resort.md)
- [Semantics are secondary](../02-hierarchy-is-everything/07-semantics-are-secondary.md)
- [Do not design too much](../01-starting-from-scratch/03-do-not-design-too-much.md)
