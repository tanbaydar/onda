# Study Unexpected Decisions

## Use this module when

- Researching references for a design task.
- An interface feels polished but the reason is not obvious.
- Building an internal design pattern library.
- An agent is tempted to copy familiar surface styling.

## Objective

Identify choices a default implementation would not have made, explain their function, and convert them into bounded reusable hypotheses.

## Rules

1. Look for decisions, not visual adjectives.
2. Prioritize surprising relationships: position, contrast, composition, type treatment, interaction placement, or state behavior.
3. Explain the user/hierarchy problem solved before extracting a pattern.
4. Record the conditions that make the decision successful.
5. References inspire hypotheses; they do not outrank product authority.
6. Avoid copying direct competitors so closely that identity and task context disappear.

## Procedure

### 1. Capture the reference context

Record product category, user task, viewport, state, content density, and relevant interaction. A screenshot without context can be misleading.

### 2. Describe the default expectation

Examples:

- Action would normally sit outside the input.
- Date picker would normally share the page surface.
- Headline would normally use one color.
- Table would normally dedicate one field per column.

### 3. Describe the unexpected decision

Use observable language: “the action is embedded inside the input’s trailing edge,” not “the form feels smart.”

### 4. Infer the mechanism

Determine whether the choice improves proximity, reduces travel, creates focus, compresses layout, expresses hierarchy, or reinforces personality. Mark inference as inference.

### 5. Define transfer conditions

List required content, interaction, density, and accessibility conditions. An embedded button may work only with short labels and clear form semantics.

### 6. Test against current authority

Map the idea to product tokens and components. Reject it if it conflicts with stronger rules or introduces unapproved behavior.

### 7. Record the principle

Write a general statement narrow enough to be useful, such as:

> When a single compact action directly operates on one short input and target-size requirements fit, trailing integration can reduce spatial separation without obscuring semantics.

## Failure modes

- Recording “clean,” “modern,” or “premium” as the lesson.
- Copying colors and radii without understanding the hierarchy.
- Ignoring state and responsive context.
- Treating inferred intent as confirmed fact.
- Importing a competitor’s identity.
- Collecting screenshots without retrieving them during real tasks.

## Verification

- The observation names a concrete unexpected decision.
- The solved problem and mechanism are explicit.
- Transfer conditions and failure conditions are documented.
- The idea maps to or deliberately challenges an existing principle.
- Product authority was checked before implementation.
- A testable comparison can be built if the idea is applied.

## Related modules

- [Think outside the box](../08-finishing-touches/06-think-outside-the-box.md)
- [Choose a personality](../01-starting-from-scratch/04-choose-a-personality.md)
- [Review and evidence](../00-agent-operating-system/03-review-and-evidence.md)
