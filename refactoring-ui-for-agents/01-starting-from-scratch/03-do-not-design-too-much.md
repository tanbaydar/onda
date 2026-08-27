# Do Not Design Too Much

## Use this module when

- Planning a feature with many possible states or future capabilities.
- Producing comprehensive mockups before implementation begins.
- A task risks expanding into speculative product design.
- Static designs are hiding implementation constraints.

## Objective

Ship the smallest useful, honest version of a feature, then learn from the working interface in short design–implementation cycles.

## Rules

1. Design the next useful slice, not the imagined final product.
2. Do not imply functionality that is not approved and implementable in the current slice.
3. Build early enough that real constraints can correct the design.
4. Edge states required for the chosen slice are not optional; speculative future states are.
5. “Nice to have” functionality must not block a useful core feature.

## Procedure

### 1. Define the shipping slice

State the smallest outcome that creates value. Separate requirements into:

- **Required now:** necessary to complete the core job safely.
- **Required state coverage:** empty, error, loading, permission, and data extremes of that job.
- **Deferred enhancement:** useful but not necessary.
- **Unapproved idea:** do not represent in the UI.

### 2. Design the simple path

Compose the core interaction using real semantics and product constraints. Avoid controls, tabs, upload areas, filters, or settings that only support future capability.

### 3. Implement and exercise it

Use the working feature to discover content overflow, latency, validation, responsive, and state problems that static design could not reveal.

### 4. Correct the current slice

Iterate until the implemented feature handles its required states and the hierarchy remains coherent.

### 5. Begin the next cycle

Only then select the next approved capability. Revisit the shell and system as repeated needs emerge.

## Scope distinction

“Do not design too much” does not mean ignoring likely production conditions. An agent must still design:

- No data and first-use states.
- Long names and localization pressure.
- Validation and recoverable failures.
- Loading and slow operations.
- Permissions and unavailable actions.
- Narrow and wide layouts in scope.
- High-volume content when plausible.

These are realities of the feature, not speculative additions.

## Failure modes

- Designing attachment controls when upload support is unapproved.
- Creating settings for capabilities that do not exist.
- Blocking a useful simple feature because an ambitious version is incomplete.
- Producing every conceivable screen before testing one working flow.
- Using static happy-path content to avoid error and empty states.
- Adding dormant components or commented-out styles “for later.”

## Verification

- Every control corresponds to shipped or explicitly assigned behavior.
- The user can complete the core job end to end.
- Required states are designed and implemented.
- Deferred features are absent rather than visually disabled promises.
- The next iteration can be added without invalidating the current user value.
- Implementation feedback informed at least one review of the design.

## Related modules

- [Feature before layout](./01-feature-before-layout.md)
- [Empty states](../08-finishing-touches/04-do-not-overlook-empty-states.md)
- [Implementation loop](../00-agent-operating-system/02-implementation-loop.md)
