# Use Letter-spacing Effectively

## Use this module when

- Styling large headings with a text-oriented font.
- Using uppercase labels, overlines, or compact navigation.
- Typography feels loose or hard to scan despite correct size and weight.
- Agents are adding tracking globally.

## Objective

Preserve the type designer’s spacing by default and make restrained role-specific adjustments where scale or case creates a known need.

## Rules

1. Default to the font’s native spacing.
2. Large headlines set in fonts designed for text may benefit from slightly tighter tracking.
3. All-caps text often benefits from added tracking because capital shapes are less varied.
4. Do not turn display fonts into body fonts by loosening tracking.
5. Tracking changes must be tested in the actual font, weight, size, language, and rendering environment.
6. Define tracking by type role, not by individual string.

## Procedure

### 1. Confirm the problem is spacing

Rule out incorrect font choice, size, weight, line height, measure, and hierarchy before adjusting tracking.

### 2. Preserve body defaults

Leave paragraph and routine UI text at native spacing unless the product type system explicitly says otherwise.

### 3. Tighten display text cautiously

For large headings in a broad text family, compare default tracking with a small negative approved step. Watch for collisions in round, diagonal, and punctuation pairs.

### 4. Open uppercase labels cautiously

Compare default with a small positive step. Track enough to improve recognition without making the label appear as separated characters.

### 5. Test scripts and responsive sizes

Tracking conventions do not transfer uniformly across writing systems. A display role that changes size may need a different tracked token or no adjustment.

## Failure modes

- Global negative letter spacing.
- Large positive tracking on lowercase body copy.
- Tight tracking that closes counters or causes collisions.
- Uppercase microcopy with default tight spacing and poor legibility.
- Adjusting individual words until every heading has a unique value.
- Applying Latin assumptions to scripts with different typographic behavior.

## Verification

- Compare default and adjusted settings side by side.
- Inspect representative problematic pairs, punctuation, numerals, and long words.
- Test at the smallest and largest sizes assigned to the role.
- Check target languages.
- Verify wrapping changes do not create worse composition.
- Confirm tracking is tokenized or role-scoped and not string-specific.

## Related modules

- [Use good fonts](./02-use-good-fonts.md)
- [Type scale](./01-establish-a-type-scale.md)
- [Line height](./05-line-height-is-proportional.md)
