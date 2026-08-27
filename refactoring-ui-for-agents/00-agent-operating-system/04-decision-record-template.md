# Design Decision Record Template

Use this template for a non-trivial visual decision, a new system value, an exception, or a conflict resolution. Keep it with the project’s normal design authority; do not create records for routine reuse of an existing token.

```md
# [Decision title]

- Date:
- Status: proposed | approved | rejected | superseded
- Scope:
- Decider or authority:

## User outcome

The user needs to ...

## Constraints

- Product behavior that must remain unchanged:
- Existing design authority:
- Accessibility requirements:
- Content and responsive extremes:

## Hierarchy

- Primary:
- Secondary:
- Tertiary/supporting:
- Deliberately de-emphasized:

## Options compared

1. Option A
2. Option B
3. Option C

## Decision

State the selected option and the observable reason it best satisfies the hierarchy and constraints.

## System impact

- Existing tokens/primitives reused:
- New reusable role, if any:
- Explicit exception, if any:
- Affected sibling surfaces:

## Verification

- Viewports:
- Data states:
- Interaction states:
- Accessibility checks:
- Visual evidence:

## Rejected alternatives

Record why each alternative failed. Avoid taste-only explanations.
```
