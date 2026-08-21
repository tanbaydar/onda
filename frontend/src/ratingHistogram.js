export function histogramBarHeight(relativeValue) {
  return relativeValue === 0 ? "var(--sp-2)" : `${relativeValue * 100}%`;
}

export function ratingTooltip(bucket) {
  return `${bucket.count} · ${bucket.rating.toFixed(1)}★`;
}

export function profileRatingBuckets(distribution) {
  if (distribution?.state === "available" && Array.isArray(distribution.buckets)) return distribution.buckets;
  return [];
}

export function profileRatingCount(distribution) {
  return profileRatingBuckets(distribution).reduce(
    (total, bucket) => total + (Number.isFinite(bucket.count) && bucket.count > 0 ? bucket.count : 0),
    0,
  );
}

export function profileRatingHistogramVisible(distribution) {
  return profileRatingCount(distribution) >= 5;
}
