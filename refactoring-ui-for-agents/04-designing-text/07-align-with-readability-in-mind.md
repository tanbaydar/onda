# Align with Readability in Mind

## Use this module when

- Choosing left, right, center, or justified alignment.
- Designing tables, prices, statistics, hero copy, or multilingual layouts.
- Centered blocks extend beyond a few lines.
- Numbers are difficult to compare.

## Objective

Align text according to reading direction, line tracking, and comparison tasks rather than decorative symmetry.

## Rules

1. Align most text to the start edge of its writing direction.
2. Center alignment is best for short, independent blocks, usually no more than a few lines.
3. Rewrite or recompose overlong centered text instead of accepting unstable ragged edges.
4. Align comparable numbers by their end edge or decimal position.
5. Justified text requires careful hyphenation and language support.
6. Direction-aware properties are preferable for multilingual interfaces.

## Procedure

### 1. Identify the reading task

- Sequential reading → start alignment.
- Short isolated statement → centered may be appropriate.
- Numeric comparison → end or decimal alignment.
- Print-like editorial composition → justified only with appropriate text handling.

### 2. Apply direction-aware layout

Use logical start/end alignment where the product supports both left-to-right and right-to-left languages.

### 3. Limit centered copy

If centered text grows past two or three lines, first shorten it, narrow its role, or switch to start alignment. Do not reduce font size solely to preserve centering.

### 4. Align numeric data

Use tabular numerals if the font supports them. Right-align or decimal-align values; keep units consistent.

### 5. Handle justification carefully

Enable language-correct hyphenation and inspect spacing rivers. Prefer start alignment if browser support or content language makes justified results unreliable.

## Failure modes

- Centering long paragraphs or multi-item instructions.
- Left-aligning decimal data so values cannot be compared quickly.
- Right-aligning general prose in an LTR interface for visual novelty.
- Justification without hyphenation, creating large word gaps.
- Hard-coded `left`/`right` behavior that breaks RTL.
- Mixed alignments within one group without a comparison purpose.

## Verification

- Read centered content with longest realistic copy.
- Compare table values at a glance; decimals or terminal digits should align.
- Test at narrow widths where lines wrap more often.
- Test required languages and writing directions.
- Inspect justified text for rivers, stretched words, and incorrect hyphenation.
- Ensure alignment reinforces grouping and hierarchy.

## Related modules

- [Line length](./03-keep-your-line-length-in-check.md)
- [Labels are a last resort](../02-hierarchy-is-everything/05-labels-are-a-last-resort.md)
- [Baseline alignment](./04-baseline-not-center.md)
