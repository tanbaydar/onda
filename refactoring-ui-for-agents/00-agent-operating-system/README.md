# Agent Operating System

Read this chapter before any design implementation or design review.

## Purpose

Human designers can use tacit judgment to fill gaps. Agents should not hide gap-filling behind words such as “clean,” “modern,” “premium,” or “polished.” This operating system converts a visual task into explicit evidence, constrained decisions, and a verification loop.

## Required sequence

1. [Preflight and authority](./01-preflight-and-authority.md)
2. [Implementation loop](./02-implementation-loop.md)
3. [Review and evidence](./03-review-and-evidence.md)
4. Use the [decision record template](./04-decision-record-template.md) for non-trivial visual choices.

## Global rules

### Diagnose before styling

Classify the problem before changing code:

- **Hierarchy:** importance is unclear or everything competes.
- **System:** too many arbitrary values or inconsistent primitives.
- **Grouping:** spacing, borders, or layout fail to show relationships.
- **Measure:** content is too wide, narrow, dense, or sparse for its task.
- **Typography:** type roles, scale, alignment, or readability are unstable.
- **Color:** roles, shades, contrast, or redundant signals are unstable.
- **Depth:** z-order or separation treatments do not express real structure.
- **Media:** imagery is low quality, incorrectly scaled, or uncontrolled.
- **State:** empty, loading, error, extreme data, or responsive variants were ignored.
- **Finish:** foundations are sound, but a restrained enhancement is justified.

Do not apply a finish-layer solution to a foundation-layer defect.

### Preserve user and product truth

- Never invent product functionality to make a layout attractive.
- Never remove required content merely because it is difficult to compose.
- Never convert a semantic or accessibility problem into a visual trick.
- Never copy a reference interface without mapping it to the current product's tasks and content.
- Never treat existing CSS as authoritative when higher-level design decisions exist.

### Prefer systems over local fixes

When a value or pattern will recur, express it as a named role, token, primitive, or documented component variant. When it is genuinely singular, document why it is exceptional. Do not create a global abstraction to conceal one arbitrary decision.

### Make comparisons, not isolated guesses

When choosing among allowed values, render adjacent candidates in context. Compare one step smaller and one step larger, or one hierarchy level quieter and louder. Select the candidate that satisfies the role with the least excess emphasis.

### Render the actual result

Static reasoning is insufficient. Inspect the implementation with real fonts, real content, actual browser layout, and representative viewport sizes. Source code conformance is not proof of visual quality.
