# Quick UI Audit for Agents

Use this for triage, review, or the final pass of a design implementation. It is a routing checklist, not a substitute for the relevant topic modules.

## 1. Establish authority

- [ ] Identify the explicit task scope.
- [ ] Locate product specifications, design handoffs, tokens, primitives, and accessibility requirements.
- [ ] Separate authoritative intent from shipped implementation evidence.
- [ ] Record unresolved conflicts instead of inventing a compromise.

## 2. State the feature and hierarchy

- [ ] Describe the user's job on this surface in one sentence.
- [ ] Name the single primary element or action.
- [ ] Classify remaining elements as secondary, tertiary, or supporting.
- [ ] Verify that the visual order matches this importance order.
- [ ] Remove equal emphasis from elements that do not deserve it.

Read: [Hierarchy](./02-hierarchy-is-everything/README.md).

## 3. Audit systems, not isolated pixels

- [ ] List every font family, font size, weight, line height, color, radius, border, shadow, and recurring spacing value used in the changed surface.
- [ ] Map each value to an existing token or documented exception.
- [ ] Flag near-duplicate values that serve the same role.
- [ ] Confirm that new tokens represent reusable roles rather than one component's appearance.

Read: [Limit choices](./01-starting-from-scratch/05-limit-your-choices.md), [spacing system](./03-layout-and-spacing/02-establish-a-spacing-and-sizing-system.md), and [type scale](./04-designing-text/01-establish-a-type-scale.md).

## 4. Audit spacing and layout

- [ ] Space within a group is smaller than space between groups.
- [ ] Content width follows readability and task needs, not viewport availability.
- [ ] Fixed-size content does not become fluid merely to satisfy a grid.
- [ ] Mobile is recomposed rather than uniformly scaled.
- [ ] Dense and sparse states preserve understandable grouping.
- [ ] Whitespace has a job: grouping, focus, rhythm, or readable measure.

Read: [Layout and spacing](./03-layout-and-spacing/README.md).

## 5. Audit typography

- [ ] The number of families and sizes is intentionally constrained.
- [ ] Importance is not encoded by size alone.
- [ ] Paragraph measure is readable.
- [ ] Line height matches text size and line length.
- [ ] Mixed sizes sharing a row align by baseline where appropriate.
- [ ] Alignment follows reading and comparison tasks.
- [ ] Links are prominent only in proportion to their importance.

Read: [Designing text](./04-designing-text/README.md).

## 6. Audit color

- [ ] Every color has a named role.
- [ ] The palette uses defined shades rather than one-off variations.
- [ ] Primary, secondary, semantic, and neutral roles do not conflict.
- [ ] Text and controls meet the product's current accessibility requirements.
- [ ] Color is never the only signal.
- [ ] Colored surfaces use intentional foreground colors, not faded grey or accidental opacity.

Read: [Working with color](./05-working-with-color/README.md).

## 7. Audit depth and separation

- [ ] Depth corresponds to actual layer, focus, or interaction state.
- [ ] Shadow direction is consistent with one light model.
- [ ] Elevation options come from a small system.
- [ ] Borders are not the default separator for every relationship.
- [ ] Background, spacing, shadow, or overlap is used only when it better expresses the relationship.

Read: [Creating depth](./06-creating-depth/README.md) and [fewer borders](./08-finishing-touches/05-use-fewer-borders.md).

## 8. Audit imagery

- [ ] Assets are suitable for their display size and role.
- [ ] Screenshots remain legible at rendered size.
- [ ] Icons were designed for approximately the size at which they render.
- [ ] Text over imagery remains readable for every plausible crop.
- [ ] User uploads are constrained by stable slots and intentional cropping.
- [ ] Loading, failure, missing-media, and extreme-aspect-ratio states are designed.

Read: [Working with images](./07-working-with-images/README.md).

## 9. Audit real states

- [ ] Empty state explains the condition and provides the next useful action when one exists.
- [ ] Controls that cannot work in an empty state are hidden or disabled with a reason.
- [ ] Loading, error, success, disabled, selected, hover, focus, and pressed states preserve hierarchy.
- [ ] Very short, very long, missing, and high-volume content do not break the design.
- [ ] Narrow mobile, typical mobile, tablet, and wide desktop layouts were visually checked when relevant.

## 10. Polish only after foundations pass

- [ ] Decorative work solves a named problem.
- [ ] Accent treatment does not create a second primary focus.
- [ ] Background decoration cannot interfere with content.
- [ ] Custom control treatments preserve semantics and accessibility.
- [ ] No added flourish compensates for broken hierarchy, spacing, typography, or media.

Read: [Finishing touches](./08-finishing-touches/README.md).

## Completion evidence

An agent should be able to report:

1. The hierarchy it implemented.
2. The systems and tokens it reused.
3. Any new reusable decision and why it was necessary.
4. The states and viewport sizes it inspected.
5. Before/after evidence for a refactor or rendered evidence for new work.
6. Remaining ambiguity that requires product authority.
