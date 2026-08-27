# You Need More Colors Than You Think

## Use this module when

- A palette contains only a few brand swatches but the application needs complete states.
- Components invent local greys or semantic colors.
- Building a product palette or auditing color roles.
- “Use fewer colors” is being interpreted as “define too few usable shades.”

## Objective

Provide enough controlled color options to cover real interface roles without creating uncontrolled visual variety.

## Rules

1. Visual restraint comes from semantic usage limits, not from an underspecified palette.
2. Neutral shades usually carry most of the interface and need sufficient range.
3. Primary colors need light and dark variants for surfaces, controls, text, and interaction states where authorized.
4. Semantic accent families may need multiple shades even when used rarely.
5. Complex data visualization may require additional distinct families, but only when the data model needs them.
6. Avoid true black as the default interface ink unless product authority specifically chooses it.

## Palette categories

### Neutrals

Needed for primary text, secondary text, muted text, page backgrounds, raised or inset surfaces, fields, dividers, disabled states, and media fallbacks. A practical system often needs more than three or four steps because these roles require distinct but coherent relationships.

### Primary or brand family

One or two core hue families may cover primary actions, selection, navigation, focus, or identity—depending on the product’s allocation rules. Each role still needs appropriate light, base, and dark options.

### Semantic accents

Error, warning, positive, informational, new, or categorical signals require named ownership. Multiple semantic meanings must not share a color when that would create ambiguity, and color must not stand alone.

### Data/category colors

Charts, calendars, tags, or multi-series data may need additional hue families plus contrast/shape/label strategies. Do not import this complexity into ordinary UI chrome.

## Procedure

### 1. Inventory roles before swatches

List every required foreground, background, border, interaction, status, and data role.

### 2. Allocate hue families

Assign one job per family where possible. Record forbidden uses to prevent semantic drift.

### 3. Determine shade needs

For each family, identify light surface, subtle border, base control/mark, hover/pressed, and dark text needs. Not every family needs every role.

### 4. Build a constrained scale

Use [Define shades up front](./03-define-your-shades-up-front.md). Provide enough distinction without near-duplicate steps.

### 5. Validate whole-page color mass

A large token inventory does not mean every page should display it. Render representative surfaces and confirm color remains scarce according to the product’s hierarchy.

## Failure modes

- Five decorative swatches expected to cover all UI roles.
- Dozens of one-off greys because the neutral scale is too shallow.
- One “success green” reused for selection, links, charts, and positive status without rationale.
- Showing every palette family on a normal screen.
- Treating additional defined shades as permission for decorative color.
- Using pure black everywhere, producing harsh contrast and reducing hierarchy options.

## Verification

- Every required UI role maps to an approved token.
- No component needs ad hoc color for an ordinary state.
- Shade steps are distinct and sufficient for text/surface/border needs.
- Semantic families retain one clear meaning.
- Representative pages use only the small subset appropriate to their content.
- Color-independent cues exist for statuses and categories.

## Related modules

- [Define shades up front](./03-define-your-shades-up-front.md)
- [Do not rely on color alone](./07-do-not-rely-on-color-alone.md)
- [Choose a personality](../01-starting-from-scratch/04-choose-a-personality.md)
