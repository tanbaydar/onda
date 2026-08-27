# Start with a Feature, Not a Layout

## Use this module when

- Creating a new product, route, page, or substantial feature.
- Redesigning a surface whose current shell dictates content awkwardly.
- Debating navigation, containers, sidebars, or dashboards before core tasks are composed.

## Objective

Derive the page structure from a real user task and its content rather than designing an empty shell and forcing features into it.

## Rules

1. The first design artifact must represent a user capability, not global chrome.
2. List required inputs, outputs, actions, feedback, and states before choosing page structure.
3. Global navigation and shell decisions must be informed by multiple implemented or well-specified features.
4. Do not add interface regions merely because comparable products have them.
5. A surface may be simple. Unused structure is not evidence of professionalism.

## Procedure

### 1. Name the feature as a verb

Use a concrete statement such as “search events,” “compare plans,” “publish a review,” or “invite a collaborator.” Avoid nouns such as “dashboard,” “portal,” or “profile experience”; they describe containers, not jobs.

### 2. Enumerate the minimum interface contract

Record:

- Information the user must provide.
- Information the system must present.
- The main action and any necessary secondary actions.
- Validation and recovery.
- Empty, loading, success, failure, and permission states.
- Content extremes likely to alter the composition.

### 3. Order by task sequence

Lay out the content in the order a user needs it. If the task is compare → select → confirm, the visual sequence should not begin with decorative product context or unrelated navigation.

### 4. Compose the smallest working surface

Use semantic elements and the minimum layout needed for the feature. Keep chrome provisional unless already governed by product authority. Do not reserve space for speculative modules.

### 5. Let repeated feature needs inform the shell

After several features reveal common navigation, context, actions, or measures, consolidate those needs into global structure. The shell is a response to feature evidence.

## Agent questions

- What can the user accomplish after this change that they could not before?
- Which content is essential to that accomplishment?
- What would still work if global navigation were removed from the design review image?
- Is any region present only because “apps usually have one”?
- Does the structure imply features that are not built or approved?

## Failure modes

- Beginning with a header, sidebar, grid, or hero before defining the task.
- Creating empty dashboard zones to make the screen feel complete.
- Filling unused space with metrics, illustrations, or cards unrelated to the primary job.
- Copying a competitor’s application shell without equivalent content needs.
- Choosing full-width versus contained layout before establishing content measure.

## Verification

- Remove the shell visually or mentally; the feature remains coherent.
- Every visible region supports the named user job or required product context.
- The first reading path matches the user's action sequence.
- No control promises functionality outside scope.
- Sparse data does not leave decorative scaffolding with no purpose.
- Dense data expands or scrolls according to content needs rather than breaking a shell-driven composition.

## Related modules

- [Detail comes later](./02-detail-comes-later.md)
- [Do not design too much](./03-do-not-design-too-much.md)
- [You do not have to fill the whole screen](../03-layout-and-spacing/03-you-do-not-have-to-fill-the-whole-screen.md)
