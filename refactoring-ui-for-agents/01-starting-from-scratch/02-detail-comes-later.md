# Detail Comes Later

## Use this module when

- Beginning a new design or substantial layout change.
- The team is debating fonts, icons, colors, shadows, or radii before the content structure works.
- A high-fidelity environment encourages premature polishing.

## Objective

Make structural decisions cheaply, prove hierarchy without decorative assistance, and invest in detail only after the feature composition is stable.

## Rules

1. Early design must make low-level detail difficult to overfit.
2. Grayscale is a diagnostic tool: hierarchy should work before accent color is introduced.
3. Low-fidelity artifacts are disposable; they are not deliverables that justify extended polishing.
4. High-fidelity code may be used early only if the agent deliberately suppresses detail and iterates quickly.
5. A detail decision must not compensate for unclear content order or grouping.

## Procedure

### 1. Reduce fidelity

Represent structure with plain blocks, actual copy, basic controls, and neutral tones. Use the product’s base typography only when coding directly. Avoid new decorative assets, shadows, gradients, and custom icons.

### 2. Validate content order

Confirm that the primary content, primary action, support content, and recovery states appear in the correct sequence.

### 3. Validate grayscale hierarchy

Use order, size, weight, neutral contrast, measure, and spacing. If the main action or content is unclear, fix those properties before using color.

### 4. Validate grouping

Ensure that proximity alone makes local relationships understandable. Do not add borders around every group during this phase.

### 5. Promote only stable decisions

Once the structure works with representative data and relevant viewports, apply product typography, palette, media, depth, and interaction states in that order.

### 6. Discard exploratory artifacts

Do not keep multiple unused prototypes, speculative wrappers, or dormant styles in production. Preserve a decision record when the reasoning matters; remove the scaffolding.

## Diagnostic grayscale test

Temporarily suppress accent colors and imagery where practical. Ask:

- Can the primary action be found immediately?
- Is the reading order apparent?
- Are group boundaries clear?
- Does metadata recede without becoming unreadable?
- Does the page still have a coherent identity from type, rhythm, and content?

If not, the interface has a hierarchy problem, not a color problem.

## Failure modes

- Selecting a distinctive font before knowing which text roles exist.
- Using a bright primary color to rescue a weak action hierarchy.
- Polishing a hero while core interaction states are missing.
- Building exact shadows or iconography for a component that may be removed.
- Treating the prototype as precious and resisting structural changes.
- Shipping exploratory CSS and calling it a design system.

## Verification

- A low-detail or grayscale rendering clearly communicates the user path.
- Decorative treatment can be removed without collapsing comprehension.
- No high-effort asset was created for unapproved functionality.
- Final detail uses existing systems and does not introduce arbitrary local values.
- The implementation was reviewed before and after color/media application.

## Related modules

- [Feature before layout](./01-feature-before-layout.md)
- [Not all elements are equal](../02-hierarchy-is-everything/01-not-all-elements-are-equal.md)
- [Do not design too much](./03-do-not-design-too-much.md)
