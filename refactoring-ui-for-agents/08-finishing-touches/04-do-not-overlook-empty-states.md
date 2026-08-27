# Do Not Overlook Empty States

## Use this module when

- A feature depends on user-created, searched, filtered, or permissioned content.
- Designing first-use, zero-result, cleared, unavailable, or no-activity conditions.
- Tabs, filters, pagination, or toolbars become inert with no data.

## Objective

Make absence understandable and actionable without leaving dead chrome, misleading controls, or a blank visual hole.

## Rules

1. Empty states are core feature states, not post-launch decoration.
2. Explain what is empty in language appropriate to the cause.
3. Offer the next useful action only when one exists and the user has permission.
4. Hide or simplify controls that cannot operate without content.
5. Preserve necessary context so the user understands where they are.
6. Distinguish first-use, no-results, filtered-empty, error, and permission-empty states; they have different remedies.
7. Illustration is optional and must follow product authority.

## Empty-state taxonomy

- **First use:** user has not created or followed anything yet; teach and enable the first action.
- **True zero:** no content exists; explain and provide creation/discovery if possible.
- **No search results:** preserve query and offer correction or scope expansion.
- **Filtered empty:** show active filters and a clear reset path.
- **Permission empty:** explain access without exposing protected information.
- **Completed/cleared:** acknowledge that no action remains, if meaningful.
- **Error masquerading as empty:** never show normal emptiness when loading failed.

## Procedure

### 1. Identify cause

Use data and state logic to distinguish absence from loading or failure.

### 2. Preserve identity

Keep the page/feature title or essential context. Remove tabs, sort, pagination, and filters only when they cannot help the current state.

### 3. Write concise copy

- State what is absent.
- Explain why only if useful.
- Offer one primary next step.
- Add secondary guidance only when necessary.

### 4. Compose hierarchy

The state message and next action become primary. Illustration, if used, supports rather than dominates.

### 5. Test transitions

Verify empty → loading → populated, populated → filtered empty, error → retry, and permission changes without layout confusion.

## Failure modes

- Blank card or table with only “No data.”
- Filters and pagination displayed when nothing can be filtered or paginated.
- First-use state with no action.
- No-results state that discards the user’s query.
- Error state rendered as ordinary emptiness.
- Large decorative illustration pushing the next action below the fold.
- Inventing a CTA for users who lack permission.

## Verification

- Every empty cause maps to the correct copy and action.
- Inert controls are hidden or meaningfully disabled.
- Keyboard focus lands in a logical place after transitions.
- The state remains coherent at narrow and wide widths.
- Error and loading cannot be mistaken for true emptiness.
- The first useful action is visible and authorized.

## Related modules

- [Feature before layout](../01-starting-from-scratch/01-feature-before-layout.md)
- [Semantics are secondary](../02-hierarchy-is-everything/07-semantics-are-secondary.md)
- [Use good photos](../07-working-with-images/01-use-good-photos.md)
