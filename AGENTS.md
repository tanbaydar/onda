# Agent Conduct Contract

These standing rules apply to every agent working in this repository.

## Frozen behavior rule

Shipped backend behavior, API contracts, and specified product rules may change only under an explicit operator ruling that names the change. A phrase in a task prompt that conflicts with shipped behavior is a conflict to surface, never authority to amend. Stop the affected work, state the conflict and the available options, and wait for operator direction.

## Scope rule

Touch only what the task names. Adjacent problems discovered during the task must be reported, not fixed.

## Self-fix rule

Self-fixes are limited to bugs introduced by the current task itself. Do not use a current-task correction as authority to repair pre-existing or adjacent behavior.

## Reporting rule

Every completion report must clearly separate these three sections:

1. **WHAT WAS ORDERED**
2. **WHAT I DID BEYOND IT** — this should be empty
3. **WHAT I FOUND BUT DID NOT TOUCH**

Every order gets a report, even if the answer is "already shipped in X."

## Backend ruling provenance

Never push a backend-behavior change unless an explicit operator ruling authorizes it and the commit message records that authority using: `per operator ruling: ...`.

## Design handoffs

Design handoffs: the .md in frontend/design-handoffs/ is sole authority. No spec HTML is kept in the repo; visual disputes are escalated to the operator.

## Push policy

Approved orders push by default. Hold a push only when the order explicitly says so or when it would publish unrelated work; in the latter case, ask the operator first.

Approved orders push by default; hold a push only when the order says so or unrelated work would publish — then ask.
