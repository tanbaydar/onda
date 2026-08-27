# Start with Too Much White Space

## Use this module when

- A surface feels cramped, noisy, or assembled from default gaps.
- The agent is tuning margins upward one small step at a time.
- Whitespace is criticized broadly without distinguishing useful space from waste.
- A dense interface is required and spacing must be deliberate.

## Objective

Find the correct breathing room by starting generous and removing space according to task density, grouping, and viewport constraints.

## Rules

1. Begin structural spacing with a generous scale candidate, then reduce it.
2. Do not add minimal space only until a layout stops looking broken.
3. Whitespace must perform a job: group, separate, focus, establish rhythm, or preserve readable measure.
4. Dense layouts are valid when the user benefits from simultaneous information visibility.
5. Density must be explicit and internally systematic, not the default result of missing spacing decisions.

## Procedure

### 1. Classify each gap

- **Intra-element:** icon to label, title to metadata.
- **Intra-group:** between related fields or rows.
- **Inter-group:** between distinct sections or tasks.
- **Container inset:** content to surface edge.
- **Viewport breathing room:** content region to shell or screen edge.

### 2. Start high on the approved scale

Choose a generous existing token for inter-group and viewport gaps. Keep intra-element spacing appropriately compact. Render the whole surface, not an isolated component.

### 3. Remove in scale steps

Reduce only where the interface appears disconnected, inefficient, or impractical. Never fine-tune with arbitrary values when the spacing scale offers adjacent choices.

### 4. Evaluate task density

For monitoring, comparison, scheduling, or data-heavy workflows, estimate how much information must be visible at once. Compact row internals before collapsing distinctions between groups.

### 5. Protect responsive rhythm

Large desktop gaps may reduce on mobile, but group relationships must remain. Do not remove structural spacing merely to fit content above the fold.

## Functional vs. unutilized whitespace

Functional whitespace:

- Separates unrelated regions.
- Gives primary content a clear field.
- Keeps prose at readable measure.
- Shows parent/child grouping.
- Creates a repeatable vertical rhythm.

Unutilized whitespace:

- Exists because a container is arbitrarily tall or wide.
- Pushes required content away without increasing clarity.
- Appears inside empty cards or grid columns created for symmetry.
- Results from fixed heights that do not match content.
- Forces excessive scrolling while relationships remain unclear.

## Failure modes

- Adding 4px repeatedly until a component is merely tolerable.
- Applying generous padding uniformly, including within dense data rows.
- Calling all blank space “luxury.”
- Cramming everything above the fold.
- Using fixed-height panels that create dead zones with sparse data.
- Reducing every gap equally on mobile.

## Verification

- Every major gap can be assigned a functional role.
- Inter-group space is visibly greater than intra-group space.
- Sparse states do not produce unexplained dead zones.
- Dense states remain scannable without losing necessary information.
- Adjacent scale comparisons were rendered.
- The layout works without fixed heights unless the task or media ratio requires them.

## Related modules

- [Spacing system](./02-establish-a-spacing-and-sizing-system.md)
- [Avoid ambiguous spacing](./06-avoid-ambiguous-spacing.md)
- [Do not fill the screen](./03-you-do-not-have-to-fill-the-whole-screen.md)
