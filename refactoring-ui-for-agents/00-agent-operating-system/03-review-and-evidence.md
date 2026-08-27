# Review and Evidence

## Use this module when

Use for design review, implementation verification, visual regression investigation, or the final quality pass.

## Objective

Produce findings that are specific, evidence-based, routed to principles, and bounded by authority.

## Rules

1. Review foundation layers before finishing layers.
2. Report observable conditions and user consequences, not taste reactions.
3. Tie every finding to product authority or a named general principle.
4. Keep recommended corrections within the requested scope.
5. Rendered evidence outranks code-shape assumptions.
6. Severity follows user impact and authority, not visual conspicuousness.

## Procedure

### Review order

Review in this order because later layers can conceal earlier defects:

1. Scope and product truth.
2. Content and interaction completeness.
3. Hierarchy and reading order.
4. Grouping, spacing, measure, and responsive composition.
5. Typography.
6. Color and accessibility.
7. Depth, borders, and layers.
8. Imagery and uncontrolled content.
9. Empty, loading, error, and extreme states.
10. Finishing treatment.

## Evidence types

Acceptable evidence includes:

- Rendered screenshots at named viewport dimensions.
- Side-by-side before/after comparisons with identical data.
- Token or computed-style inventories.
- Contrast and accessibility checks required by the project.
- Interaction recordings or state screenshots.
- Dense and sparse fixture comparisons.
- Automated visual, semantic, and keyboard tests where available.

Code presence alone is weak evidence. “Uses token X” does not prove that X creates the correct hierarchy in context.

## Finding format

Each finding should state:

1. **Observed condition:** what is visibly or behaviorally true.
2. **Consequence:** what becomes difficult to understand, scan, compare, or operate.
3. **Violated rule:** link to the relevant module or product authority.
4. **Scope:** exact surface, state, and viewport.
5. **Recommended direction:** the smallest class of correction, not an unsolicited redesign.
6. **Authority status:** required, allowed, open, or conflicting.

Example:

> At 390 px, the gap from the field label to its input equals the gap between field groups. Users cannot reliably perceive label ownership. This violates the grouping rule in `avoid-ambiguous-spacing`. Increase inter-group spacing using the next existing spacing token; do not add card borders. The correction is allowed by the current spacing scale.

## Severity model

- **Critical:** blocks comprehension or operation; violates explicit authority or accessibility requirements.
- **High:** materially misstates hierarchy, breaks responsive use, or fails a common data state.
- **Medium:** creates recurring inconsistency, avoidable ambiguity, or significant visual noise.
- **Low:** localized polish issue after foundations are correct.

Do not inflate severity because a defect is visually obvious. Severity follows user impact and authority.

## Whole-system checks

Before approving a local change, compare it with at least:

- One sibling component.
- One dense state.
- One sparse or empty state.
- The narrowest supported width.
- A typical desktop width.
- Every interaction state changed by the task.

If a proposed correction would alter unrelated surfaces through a shared primitive, report the blast radius. Do not expand scope silently.

## Completion gate

A design change is complete only when:

- The named outcome is visible in the rendered interface.
- Higher-authority requirements remain satisfied.
- No new arbitrary values or variants were introduced without rationale.
- Responsive and state checks pass.
- Accessibility signals are not weakened.
- Remaining issues are separated from the work performed.

## Failure modes

- Listing isolated pixels without identifying the shared system defect.
- Calling a design “unprofessional” without observable evidence.
- Treating a reference screenshot as higher authority than product rules.
- Recommending a full redesign for a scoped component defect.
- Approving source-code token use without rendering the outcome.
- Omitting empty, dense, responsive, focus, or error states from review.

## Verification

- Every finding uses the required finding format.
- Every severity rating is supported by user impact or authority.
- All in-scope viewports and states have evidence.
- Recommendations name the smallest correction class.
- Adjacent issues are reported separately and not silently fixed.
- The completion gate is satisfied before approval.

## Related modules

- [Preflight and authority](./01-preflight-and-authority.md)
- [Implementation loop](./02-implementation-loop.md)
- [Quick audit](../QUICK_AUDIT.md)
