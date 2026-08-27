# Refactoring UI for Agents

This directory is a portable, product-agnostic design memory for AI agents that design, implement, refactor, or review user interfaces. It operationalizes the ideas in *Refactoring UI* by Adam Wathan and Steve Schoger as task routing, decision rules, implementation procedures, failure detection, and verification.

It is not a visual brand, a component library, or a substitute for a product's own design authority. It tells an agent how to reason about interface quality without improvising arbitrary values or treating design as decoration.

## Authority and scope

Use this memory under the following precedence order:

1. Explicit user instructions and operator rulings.
2. Repository-level agent instructions and shipped product constraints.
3. Approved product specifications, design handoffs, tokens, and component contracts.
4. This general design memory.
5. Existing implementation patterns, unless a higher authority explicitly ratifies them.

If this memory conflicts with a higher authority, stop applying the conflicting rule. Record the conflict and request a ruling when the task cannot continue safely. Do not silently reinterpret product requirements to fit a general principle.

This memory governs visual decision-making. It does not authorize changes to product behavior, content, information architecture, APIs, or accessibility requirements outside the assigned task.

## Mandatory agent reading protocol

For any task that changes or evaluates visual UI:

1. Read [the operating protocol](./00-agent-operating-system/README.md).
2. Identify the task type in the router below.
3. Read every module marked **Required** for that task and any conditional module triggered by the implementation.
4. Inspect the product's existing authority: specifications, tokens, primitives, components, responsive rules, and representative real data.
5. Write a short design intent before editing code.
6. Implement using existing systems before inventing new values.
7. Verify the result at realistic content densities and relevant viewport sizes.
8. Report decisions, exceptions, and evidence. Do not report taste as proof.

Do not load all modules by default. This directory is intentionally modular so that an agent retrieves the smallest complete set of knowledge needed for a task.

## Task router

| Task | Required modules | Conditional modules |
|---|---|---|
| New feature or surface | [Feature before layout](./01-starting-from-scratch/01-feature-before-layout.md), [Defer detail](./01-starting-from-scratch/02-detail-comes-later.md), [Work in cycles](./01-starting-from-scratch/03-do-not-design-too-much.md), [Limit choices](./01-starting-from-scratch/05-limit-your-choices.md), [Hierarchy](./02-hierarchy-is-everything/01-not-all-elements-are-equal.md), [Ambiguous spacing](./03-layout-and-spacing/06-avoid-ambiguous-spacing.md) | Typography, color, depth, imagery, and finishing modules actually used by the surface |
| Existing UI looks amateur, noisy, or inconsistent | [Hierarchy](./02-hierarchy-is-everything/README.md), [Spacing system](./03-layout-and-spacing/02-establish-a-spacing-and-sizing-system.md), [Type scale](./04-designing-text/01-establish-a-type-scale.md), [Fewer borders](./08-finishing-touches/05-use-fewer-borders.md), [Quick audit](./QUICK_AUDIT.md) | Color palette, imagery, depth, empty state |
| Design-system or token work | [Limit choices](./01-starting-from-scratch/05-limit-your-choices.md), [Spacing system](./03-layout-and-spacing/02-establish-a-spacing-and-sizing-system.md), [Type scale](./04-designing-text/01-establish-a-type-scale.md), [Color palette](./05-working-with-color/02-you-need-more-colors-than-you-think.md), [Shade construction](./05-working-with-color/03-define-your-shades-up-front.md), [Elevation system](./06-creating-depth/02-use-shadows-to-convey-elevation.md) | Personality, font selection, color temperature, two-part shadows |
| Typography or content layout | [Designing text](./04-designing-text/README.md), [Hierarchy](./02-hierarchy-is-everything/README.md) | Labels, links, document hierarchy |
| Spacing, responsive layout, or density | [Layout and spacing](./03-layout-and-spacing/README.md) | Line length, line height, intended image size |
| Color or theming | [Working with color](./05-working-with-color/README.md), especially [do not rely on color alone](./05-working-with-color/07-do-not-rely-on-color-alone.md) | Colored backgrounds, depth through color, text over images |
| Buttons, actions, navigation, or control hierarchy | [Emphasize by de-emphasizing](./02-hierarchy-is-everything/04-emphasize-by-de-emphasizing.md), [Semantics are secondary](./02-hierarchy-is-everything/07-semantics-are-secondary.md), [Not every link needs color](./04-designing-text/06-not-every-link-needs-a-color.md) | Weight/contrast balance, supercharged defaults |
| Tables, dashboards, metadata, or data display | [Labels are a last resort](./02-hierarchy-is-everything/05-labels-are-a-last-resort.md), [Alignment](./04-designing-text/07-align-with-readability-in-mind.md), [Think outside the box](./08-finishing-touches/06-think-outside-the-box.md) | Color-alone, density, grids |
| Cards, overlays, dropdowns, or layers | [Creating depth](./06-creating-depth/README.md), [Fewer borders](./08-finishing-touches/05-use-fewer-borders.md) | Background decoration, overlap, weight/contrast |
| Photos, icons, screenshots, avatars, or uploads | [Working with images](./07-working-with-images/README.md) | Text contrast, overlap, background bleed, color |
| Empty, loading, first-use, or no-results state | [Empty states](./08-finishing-touches/04-do-not-overlook-empty-states.md), [Hierarchy](./02-hierarchy-is-everything/01-not-all-elements-are-equal.md) | Feature-first design, imagery, action hierarchy |
| Visual polish pass | [Finishing touches](./08-finishing-touches/README.md), [Quick audit](./QUICK_AUDIT.md) | Any foundation module implicated by a defect; fix foundations before decoration |
| Design review only | [Review protocol](./00-agent-operating-system/03-review-and-evidence.md), [Quick audit](./QUICK_AUDIT.md) | Modules corresponding to each reported finding |

## Trigger map

Read these modules whenever the trigger appears, even if the task router did not list them:

| Trigger | Module |
|---|---|
| More than a few one-off font sizes | [Establish a type scale](./04-designing-text/01-establish-a-type-scale.md) |
| Repeated arbitrary gaps, widths, or heights | [Establish a spacing and sizing system](./03-layout-and-spacing/02-establish-a-spacing-and-sizing-system.md) |
| Everything appears equally important | [Not all elements are equal](./02-hierarchy-is-everything/01-not-all-elements-are-equal.md) |
| Primary content is huge or secondary text is tiny | [Size is not everything](./02-hierarchy-is-everything/02-size-is-not-everything.md) |
| Grey or translucent text on color or imagery | [Colored-background text](./02-hierarchy-is-everything/03-do-not-use-grey-text-on-colored-backgrounds.md) and [image contrast](./07-working-with-images/02-text-needs-consistent-contrast.md) |
| Active state still does not stand out | [Emphasize by de-emphasizing](./02-hierarchy-is-everything/04-emphasize-by-de-emphasizing.md) |
| Dense `Label: value` displays | [Labels are a last resort](./02-hierarchy-is-everything/05-labels-are-a-last-resort.md) |
| Semantic heading level dictates appearance | [Visual vs. document hierarchy](./02-hierarchy-is-everything/06-separate-visual-hierarchy-from-document-hierarchy.md) |
| Icons overpower adjacent text | [Balance weight and contrast](./02-hierarchy-is-everything/06-balance-weight-and-contrast.md) |
| Desktop layout stretches merely because space exists | [Do not fill the whole screen](./03-layout-and-spacing/03-you-do-not-have-to-fill-the-whole-screen.md) |
| Grid percentages distort content | [Grids are overrated](./03-layout-and-spacing/04-grids-are-overrated.md) |
| Mobile looks like a uniformly scaled desktop | [Relative sizing does not scale](./03-layout-and-spacing/05-relative-sizing-does-not-scale.md) |
| Users may misread which items belong together | [Avoid ambiguous spacing](./03-layout-and-spacing/06-avoid-ambiguous-spacing.md) |
| Paragraphs feel tiring or difficult to track | [Line length](./04-designing-text/03-keep-your-line-length-in-check.md) and [line height](./04-designing-text/05-line-height-is-proportional.md) |
| Mixed text sizes look vertically misaligned | [Baseline, not center](./04-designing-text/04-baseline-not-center.md) |
| Too many blue links compete for attention | [Not every link needs color](./04-designing-text/06-not-every-link-needs-a-color.md) |
| Color values proliferate | [Define shades up front](./05-working-with-color/03-define-your-shades-up-front.md) |
| Status depends only on red/green or category hue | [Do not rely on color alone](./05-working-with-color/07-do-not-rely-on-color-alone.md) |
| Shadows are arbitrary decoration | [Use shadows to convey elevation](./06-creating-depth/02-use-shadows-to-convey-elevation.md) |
| User-uploaded media breaks layout | [Beware user-uploaded content](./07-working-with-images/04-beware-user-uploaded-content.md) |
| Empty screen shows inert controls or a dead-end message | [Do not overlook empty states](./08-finishing-touches/04-do-not-overlook-empty-states.md) |
| Boxes and borders surround everything | [Use fewer borders](./08-finishing-touches/05-use-fewer-borders.md) |

## Module contract

Every topic module uses the same sections:

- **Use this module when**: retrieval conditions.
- **Objective**: the design outcome, expressed independently of style.
- **Rules**: constraints an agent can apply while implementing.
- **Procedure**: ordered decisions; no taste-based skipping.
- **Failure modes**: visible evidence that the principle was violated.
- **Verification**: observations, comparisons, and tests required before completion.
- **Related modules**: the smallest useful neighboring context.

The examples are intentionally generic. Product-specific tokens and components must replace illustrative values.

## Core doctrine

Professional interface quality is usually the result of coherent decisions, not additional decoration:

- Make importance visible through hierarchy.
- Restrict low-level choices into reusable systems.
- Use space to communicate grouping and rhythm.
- Give content the width and scale it needs, not the width the viewport offers.
- Treat typography as interface structure.
- Assign color semantic jobs and never make color the only signal.
- Use depth only to communicate spatial relationships.
- Design media for its actual display conditions.
- Fix foundations before adding finishing treatments.
- Verify with real states, real density, and direct visual comparison.

## Source relationship

This is an original, paraphrased operationalization of *Refactoring UI*. It is optimized for agent retrieval and implementation rather than human chapter-by-chapter reading. See [SOURCE_MAP.md](./SOURCE_MAP.md) for complete topic coverage and source-page mapping.
