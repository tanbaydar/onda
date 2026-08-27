# Rebuild Interfaces Deliberately

## Use this module when

- Training visual implementation skill.
- Reverse-engineering why a reference feels polished.
- Calibrating typography, spacing, and depth judgment.
- Creating a study artifact outside production scope.

## Objective

Reconstruct a reference from visual observation, compare differences, and extract durable design insights without copying implementation code.

## Rules

1. Rebuild as a study, not as an unauthorized production redesign.
2. Do not inspect developer tools or source implementation during the initial reconstruction.
3. Use a legally and ethically appropriate reference and assets.
4. Match content and viewport closely enough for meaningful comparison.
5. Diagnose differences by category before tuning values.
6. Extract principles; do not preserve a pile of copied literals.

## Procedure

### 1. Define the study frame

Choose one surface and one viewport. Record visible content, state, and interactions. Limit the exercise so comparison remains precise.

### 2. Reconstruct structure

Build semantic content order, container behavior, and component relationships without high-fidelity detail.

### 3. Reconstruct hierarchy

Estimate type roles, contrast tiers, spacing groups, measures, and imagery. Use your own constrained scales rather than one-pixel guessing.

### 4. Reconstruct detail

Add typography, color, borders, shadows, icons, and media treatments only after the composition matches.

### 5. Compare visually

Use side-by-side and overlay/difference methods when available. Categorize mismatches:

- Geometry and measure.
- Spacing and grouping.
- Type metrics and line height.
- Weight and contrast.
- Color temperature and shade.
- Shadow/elevation.
- Media crop and asset scale.

### 6. Correct by principle

Change the system-level cause first. If every heading is too loose, adjust the heading role; do not tune each heading individually.

### 7. Extract lessons

Record unexpected decisions, why your first attempt differed, and the reusable rule. Discard or clearly label copied study code so it cannot become accidental production authority.

## Failure modes

- Inspecting exact CSS immediately and learning only values.
- Rebuilding a whole application rather than a bounded surface.
- Using different content, making spacing comparison invalid.
- Pixel-tuning before hierarchy matches.
- Copying proprietary assets or code into production.
- Treating a reference pattern as universally correct.

## Verification

- The reconstruction uses comparable content and dimensions.
- Differences were classified before correction.
- At least one system-level insight was extracted.
- Study code and assets are isolated from production unless separately authorized.
- The resulting principle includes transfer and failure conditions.
- No product-specific authority was silently changed.

## Related modules

- [Study unexpected decisions](./01-study-unexpected-decisions.md)
- [Implementation loop](../00-agent-operating-system/02-implementation-loop.md)
- [Limit choices](../01-starting-from-scratch/05-limit-your-choices.md)
