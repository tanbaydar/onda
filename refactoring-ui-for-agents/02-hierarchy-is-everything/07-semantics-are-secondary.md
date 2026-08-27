# Semantics Are Secondary

## Use this module when

- Styling primary, secondary, tertiary, destructive, or confirmation actions.
- Every action of the same semantic category looks identical.
- Destructive actions are permanently red and dominant.
- A page contains many buttons competing for attention.

## Objective

Style actions according to their importance in the current context, using semantic meaning as an additional signal rather than the sole determinant of prominence.

The title means visual semantics are secondary to hierarchy; semantic HTML and accessible naming remain mandatory.

## Rules

1. Most task states have one primary action.
2. Secondary actions must be clear but less prominent.
3. Tertiary actions should be discoverable without competing.
4. Destructive meaning does not automatically make an action primary.
5. In a confirmation step, the hierarchy may change and the destructive action may become primary.
6. Visual treatment must not be the only indication of consequence.

## Procedure

### 1. Rank actions for the current state

- **Primary:** advances or completes the user's immediate job.
- **Secondary:** valid alternative or supportive action.
- **Tertiary:** infrequent, optional, or reversible utility.
- **Dangerous/destructive:** consequence category applied in addition to rank.

### 2. Apply product variants

Typical mappings:

- Primary: solid or otherwise highest-contrast approved treatment.
- Secondary: outline, quiet fill, or lower-contrast treatment.
- Tertiary: text or link-like treatment.

Use the product system; these are relational roles, not a universal visual recipe.

### 3. Place actions by flow

Order and proximity should reinforce rank. Do not rely on color to fix a confusing action group.

### 4. Handle destructive actions contextually

On an account page, “Delete account” may be a quiet tertiary action. In a confirmation dialog, the destructive confirmation can become the primary action because it is now the explicit task. Pair it with clear consequence copy and a safe cancel path.

### 5. Test alternate states

Saving, disabled, error, and success states should preserve action hierarchy. A disabled primary action must not cause a secondary action to appear accidentally primary unless the task genuinely changes.

## Failure modes

- Three adjacent solid buttons of equal weight.
- Every dangerous action shown as a large red button at rest.
- Secondary actions hidden so thoroughly that users cannot find valid alternatives.
- Color alone indicating destructive consequence.
- Confirmation dialogs whose safe and destructive choices are ambiguous.
- Using button appearance on non-actions or link appearance on primary submissions without product rationale.

## Verification

- Identify the primary action without reading labels.
- Tab through actions; focus order follows the task flow.
- Check grayscale and color-independent meaning.
- Verify destructive actions include explicit consequence language.
- Compare resting page hierarchy with confirmation hierarchy.
- Confirm each action uses an existing variant or a documented reusable role.

## Related modules

- [Emphasize by de-emphasizing](./04-emphasize-by-de-emphasizing.md)
- [Not every link needs color](../04-designing-text/06-not-every-link-needs-a-color.md)
- [Not all elements are equal](./01-not-all-elements-are-equal.md)
