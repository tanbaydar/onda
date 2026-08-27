# Preflight and Authority

## Use this module when

Always. This is the first step before visual design, implementation, refactoring, or review.

## Objective

Build a bounded evidence set that tells the agent what may change, what must remain true, and which decisions already exist.

## Rules

1. Higher-authority product decisions override this general memory.
2. Shipped implementation is evidence, not automatic design authority.
3. Missing information is not permission to invent a product-changing answer.
4. Scope boundaries must be explicit before shared primitives are changed.
5. Every proposed visual change must connect to a user outcome or a named system defect.
6. Assumptions must be reversible, disclosed, and consistent with the existing system.

## Required inputs

Collect, in descending authority:

1. The user's named outcome, scope, and exclusions.
2. Repository agent instructions and change policies.
3. Product specifications, design handoffs, design contracts, and approved references.
4. Design tokens, primitives, component variants, and content rules.
5. Representative routes and states in the shipped implementation.
6. Realistic sparse, typical, dense, error, and empty data.

Missing inputs are not permission to invent. If a missing decision materially changes the product direction or creates a conflict, ask for a ruling. If it only affects a reversible implementation detail and the existing system supplies a clear convention, use that convention and report the assumption.

## Procedure

### 1. Restate the job

Write one sentence in this format:

> The user needs to [perform/understand outcome] on [surface] while [important constraint].

If this sentence describes appearance but no user outcome, the task is underdefined. For a visual-only refactor, describe the comprehension outcome: faster scanning, clearer grouping, reduced competition, readable measure, or system consistency.

### 2. Define the change boundary

List:

- Named routes, components, assets, or documents.
- Behavior that must remain unchanged.
- Responsive sizes and states in scope.
- Adjacent issues explicitly out of scope.

### 3. Build an authority table

For each relevant decision, record its source:

| Decision | Authority | Current implementation | Status |
|---|---|---|---|
| Example: primary action treatment | approved component contract | local custom style | conflict |

Use only four statuses: `required`, `allowed`, `open`, `conflict`.

### 4. Inventory the visual language

Inspect the smallest representative set that reveals:

- Font families, sizes, weights, line heights, and tracking.
- Neutral, brand, semantic, and interaction colors.
- Spacing and sizing steps.
- Container and text measures.
- Radius, border, shadow, and layer conventions.
- Image ratios and fallback behavior.
- Control anatomy and states.

Do not assume that repetition makes a value correct. Repetition proves implementation prevalence, not design authority.

### 5. Identify the violated principle

Name the primary problem class and route to its module. Limit the initial diagnosis to one primary and at most two contributing classes. A list of twenty isolated symptoms usually means the foundational issue has not been identified.

### 6. Write the design intent

Before editing, state:

- The primary content or action.
- What will be deliberately de-emphasized.
- Which existing systems will carry the change.
- What evidence will demonstrate success.

## Failure modes

- Starting from a screenshot and copying its surface treatment without understanding its information hierarchy.
- Treating adjectives as requirements.
- Inventing new tokens before inventorying existing ones.
- Refactoring unrelated components for “consistency.”
- Assuming desktop is authoritative and mobile is a shrink operation.
- Ignoring states because the happy path looks correct.

## Verification

Preflight is complete only when the agent can answer:

- What exactly is allowed to change?
- Which source decides each relevant visual rule?
- What is the one primary user outcome?
- Which modules must be read?
- Which states and viewports will be rendered?
- What would count as an unauthorized design invention?

## Related modules

- [Implementation loop](./02-implementation-loop.md)
- [Review and evidence](./03-review-and-evidence.md)
- [Feature before layout](../01-starting-from-scratch/01-feature-before-layout.md)
