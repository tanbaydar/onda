export function histogramBarHeight(relativeValue) {
  return relativeValue === 0 ? "var(--sp-2)" : `${relativeValue * 100}%`;
}

export function ratingTooltip(bucket) {
  return `${bucket.count} · ${bucket.rating.toFixed(1)}★`;
}

export function profileRatingBuckets(distribution) {
  if (distribution.state === "available") return distribution.buckets;
  return Array.from({ length: 10 }, (_, index) => ({
    rating: (index + 1) / 2,
    count: 0,
    relative_value: 0,
  }));
}
