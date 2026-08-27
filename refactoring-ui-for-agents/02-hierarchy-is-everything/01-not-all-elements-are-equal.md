# Not All Elements Are Equal

## Use this module when

- Everything on a surface appears equally loud.
- A page contains many cards, labels, actions, or metadata blocks with similar treatment.
- Users cannot tell where to begin or what matters.
- A redesign request is described only as “make it more professional.”

## Objective

Make the relative importance of information visible so the interface can be scanned without reading every element.

## Rules

1. Every surface must have an explicit importance order.
2. Only one element or tightly related group should occupy the highest visual tier for a given task state.
3. Supporting information must remain readable while receding.
4. Order, position, spacing, measure, weight, contrast, size, and imagery all affect hierarchy.
5. Do not give equal component chrome to unequal content.

## Procedure

### 1. Inventory visible elements

List content, actions, labels, navigation, imagery, system feedback, and decoration. Do not group them by DOM structure; group them by user purpose.

### 2. Assign tiers

- **Primary:** the main content or action required for the current user job.
- **Secondary:** content needed to interpret or complete the job.
- **Tertiary:** useful metadata, less common actions, or supplemental context.
- **Supporting:** structural labels, timestamps, system chrome, or optional detail.

If more than one unrelated item is primary, restate the user job or split the surface into task states.

### 3. Select channels deliberately

Use the fewest channels necessary:

- Position and order for first-read priority.
- Space for grouping and prominence.
- Weight and neutral contrast for emphasis.
- Size for major tier differences, not every distinction.
- Imagery only where content warrants it.
- Color only for its assigned semantic or action role.

### 4. De-emphasize lower tiers

Reduce competing contrast, weight, size, chrome, or visual area. Preserve legibility and interaction discoverability.

### 5. Check state-specific hierarchy

The primary element may change after selection, error, completion, or permission change. Re-evaluate each material state rather than assuming one hierarchy fits all.

## Failure modes

- Every section uses the same card, heading size, and padding.
- Primary and tertiary actions share identical button treatment.
- Metadata is only slightly smaller but equally dark and bold.
- A large image dominates even though it is not central to the task.
- Multiple accent colors create several apparent entry points.
- The interface relies on users reading every label to understand priority.

## Verification

- Ask a reviewer to identify the primary element after a brief glance.
- Inspect a grayscale screenshot and a reduced thumbnail.
- Count unrelated high-contrast elements; justify each.
- Confirm supporting text remains readable but does not compete.
- Compare empty, typical, and dense states.
- Verify keyboard focus can temporarily become prominent without permanently flattening the hierarchy.

## Related modules

- [Size is not everything](./02-size-is-not-everything.md)
- [Emphasize by de-emphasizing](./04-emphasize-by-de-emphasizing.md)
- [Ambiguous spacing](../03-layout-and-spacing/06-avoid-ambiguous-spacing.md)
