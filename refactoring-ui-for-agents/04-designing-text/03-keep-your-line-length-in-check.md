# Keep Your Line Length in Check

## Use this module when

- Paragraphs span broad containers.
- Prose is squeezed to match surrounding cards or grids.
- A mixed-media content region uses one width for every child.
- Reading feels tiring or users lose their place between lines.

## Objective

Constrain paragraph measure for comfortable reading even when the surrounding section must be wider for images, tables, or other media.

## Rules

1. Optimize the layout for reading rather than fitting text into leftover width.
2. A practical starting range for long-form paragraphs is roughly 45–75 characters per line.
3. Measure should be tested in the actual font and language.
4. A content region may contain multiple intentional widths.
5. Wider lines require more line height and stronger evidence.
6. Narrow columns must not create excessive hyphenation or ragged single-word lines.

## Procedure

### 1. Classify the text

Long-form prose, short descriptions, labels, metadata, and tabular text have different measure needs. Apply the character-range heuristic to sustained reading, not every UI string.

### 2. Set a text-specific max measure

Use an existing prose token or a width expressed relative to text metrics when project conventions permit. The source suggests approximately `20–35em` as a starting ballpark, not a universal rule.

### 3. Decouple wider siblings

Let images, charts, code, and tables use broader regions while paragraphs keep their own measure. Align intentionally; not every child needs identical width.

### 4. Test actual language

Count or visually inspect representative lines with typical and long words. Localization may change the ideal measure and wrapping behavior.

### 5. Coordinate line height

If measure must exceed the safe range, increase leading carefully and test tracking between lines. Prefer narrowing the text before making extremely loose leading.

## Failure modes

- Full-width body copy on a large monitor.
- A narrow mobile column with large side padding that leaves only a few words per line.
- Forcing all children to the paragraph measure, shrinking useful media.
- Centering long prose to mask an awkward width.
- Measuring only with placeholder Latin text.
- Using fixed character widths that ignore font and language differences.

## Verification

- Inspect representative paragraphs at narrow, typical, and wide widths.
- Count characters on several lines as a diagnostic, not a single exact target.
- Verify readers can find the next line without effort.
- Check long words, links, inline code, and localization.
- Confirm media can exceed prose measure without creating accidental misalignment.
- Confirm the paragraph does not widen merely because its parent does.

## Related modules

- [Line height](./05-line-height-is-proportional.md)
- [Do not fill the screen](../03-layout-and-spacing/03-you-do-not-have-to-fill-the-whole-screen.md)
- [Alignment](./07-align-with-readability-in-mind.md)
