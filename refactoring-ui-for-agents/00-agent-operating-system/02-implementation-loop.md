# Implementation Loop

## Use this module when

Whenever an agent changes design code, design tokens, component structure, assets, or content presentation.

## Objective

Move from low-cost structural decisions to high-fidelity detail without letting decoration conceal a weak interface.

## Rules

1. Resolve content structure before surface detail.
2. Make hierarchy work in grayscale before assigning semantic or accent color.
3. Reuse systems before adding values or variants.
4. Render and inspect every meaningful phase.
5. Return to the earliest failing phase when later work exposes a foundation defect.
6. Do not advance to finishing treatment while required states or responsive compositions fail.

## Procedure

### Phase 1: Content and feature skeleton

Represent the real content and actions with minimal visual styling.

- Include only functionality that exists or is explicitly in scope.
- Use realistic labels and representative data lengths.
- Establish semantic order and keyboard order.
- Include empty, loading, error, selected, and disabled states in the structure when relevant.

Gate: the feature must be understandable without color, shadow, imagery, or ornamental styling.

### Phase 2: Hierarchy in grayscale

Assign each visible element a role: primary, secondary, tertiary, or supporting.

Use spacing, order, measure, font size, font weight, and neutral contrast to make those roles apparent. Do not introduce accent color to rescue a hierarchy that fails in grayscale.

Gate: a viewer can identify the main content or action within a brief glance and can follow the intended reading order.

### Phase 3: Systems and geometry

Map values to existing scales and primitives:

- Type roles and scale.
- Spacing and sizing scale.
- Content measures and responsive behavior.
- Component anatomy and reusable variants.
- Radius, border, and elevation systems.

When no existing value works, compare adjacent scale candidates in context before proposing a new system value. A new value needs a role and at least one plausible reuse case.

Gate: no arbitrary one-off value is hiding a structural problem.

### Phase 4: Color and media

Apply color according to named semantic roles. Add real or production-representative imagery at its intended ratio and size.

- Validate foreground/background combinations.
- Add a non-color signal for status and categories when needed.
- Test hostile media: very light, very dark, low contrast, missing, failed, and unusual aspect ratios.

Gate: color supports existing meaning; media does not control or destabilize layout.

### Phase 5: Interaction and depth

Add hover, focus, active, pressed, drag, menu, dialog, and layered states.

- Depth must correspond to actual z-order or interaction.
- Focus must remain visible.
- Changes in state must not depend only on color.
- Motion is added only when permitted and must communicate state or continuity.

Gate: every interactive treatment describes a real state and survives keyboard and reduced-motion conditions required by the product.

### Phase 6: Finish

Only after all earlier gates pass, consider restrained finishing treatments: accent borders, custom list markers, background treatment, or unconventional composition.

Every flourish must answer:

1. What problem does this solve?
2. Which element should receive the added emphasis?
3. Does the product's visual language authorize it?
4. Can it be removed without reducing comprehension? If yes, is the aesthetic value worth the extra system complexity?

## Compare adjacent candidates

For any uncertain scalar choice:

1. Choose the nearest existing token.
2. Render that token, the previous step, and the next step.
3. Compare all three in the same realistic context.
4. Reject candidates that create excessive emphasis, poor readability, or ambiguous grouping.
5. Keep the smallest change that clearly satisfies the role.

Do not fine-tune in one-pixel increments unless optical alignment demands a documented exception.

## Failure modes

- Styling the shell before the feature content exists.
- Introducing color before hierarchy works.
- Adding cards, borders, or shadows to solve spacing ambiguity.
- Building only one viewport and deriving the rest through proportional scaling.
- Testing with polished placeholder data instead of real extremes.
- Adding new primitives while bypassing equivalent existing ones.
- Calling a surface complete after code review without rendering it.

## Verification

At each phase, capture or inspect the rendered result. If a later phase reveals a foundation defect, return to the earliest failing phase instead of adding compensating polish.

## Related modules

- [Preflight and authority](./01-preflight-and-authority.md)
- [Review and evidence](./03-review-and-evidence.md)
- [Detail comes later](../01-starting-from-scratch/02-detail-comes-later.md)
- [Limit your choices](../01-starting-from-scratch/05-limit-your-choices.md)
