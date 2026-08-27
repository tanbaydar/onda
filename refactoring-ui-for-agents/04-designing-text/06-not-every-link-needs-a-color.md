# Not Every Link Needs a Color

## Use this module when

- Most content on a surface is clickable.
- Colored links create visual noise in feeds, tables, navigation, or cards.
- Ancillary actions compete with the main path.
- Link treatment is being standardized without context.

## Objective

Make links identifiable and accessible in proportion to their role, using context, weight, contrast, underline, and interaction states rather than coloring every link alike.

## Rules

1. Links embedded in prose must be distinguishable from surrounding text without relying on hover.
2. In link-dense application UI, context may already establish clickability; use subtler treatment.
3. Primary navigation and important actions require clear resting-state discoverability.
4. Ancillary links may rely on restrained resting treatment plus clear focus/hover, only when context supports discovery.
5. Keyboard focus must always be visible.
6. Do not rely on color alone when links appear within otherwise identical text.

## Procedure

### 1. Classify link context

- Inline prose link.
- Navigation item.
- Whole-row or card link.
- Object identity link in a feed/table.
- Tertiary utility action.
- Destructive or recovery link.

### 2. Assign hierarchy

Choose emphasis based on importance. A primary object name may use weight and primary text color; timestamp or utility links may be quieter.

### 3. Preserve affordance

Use underline, weight, color difference, iconography, row behavior, cursor conventions, or component anatomy as appropriate. Embedded prose needs the strongest explicit distinction.

### 4. Define states

Specify resting, visited when relevant, hover, focus, active, and disabled/unavailable behavior. Hover-only discovery is insufficient for essential actions.

### 5. Test mixed content

Ensure link styles do not make every name or label appear equally important and do not cause non-links to look interactive.

## Failure modes

- Bright brand color on every clickable object.
- Removing all inline-link underlines and relying only on color.
- Ancillary links discoverable only by pointer hover.
- Non-link bold text indistinguishable from linked bold text in the same context.
- Focus style removed because it disrupts visual calm.
- Whole-row links containing nested conflicting actions without clear semantics.

## Verification

- Identify essential links without pointer hover.
- Navigate using keyboard only.
- Check color-independent distinction for inline links.
- Compare link-dense surfaces in grayscale.
- Verify visited-state requirements for content where history matters.
- Confirm link treatment follows role rather than one global visual recipe.

## Related modules

- [Semantics are secondary](../02-hierarchy-is-everything/07-semantics-are-secondary.md)
- [Emphasize by de-emphasizing](../02-hierarchy-is-everything/04-emphasize-by-de-emphasizing.md)
- [Do not rely on color alone](../05-working-with-color/07-do-not-rely-on-color-alone.md)
