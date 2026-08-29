export function histogramBarHeight(relativeValue) {
  return relativeValue === 0 ? "var(--sp-2)" : `${relativeValue * 100}%`;
}

export function ratingTooltip(bucket) {
  return `${bucket.count} · ${bucket.rating.toFixed(1)}★`;
}

export function ratingBucketLabel(bucket) {
  const unit = bucket.count === 1 ? "rating" : "ratings";
  return `${bucket.rating.toFixed(1)} stars: ${bucket.count} ${unit}`;
}

export function ratingDistributionDescription(buckets) {
  return `${buckets.map(ratingBucketLabel).join(". ")}.`;
}

export function profileRatingBuckets(distribution) {
  if (distribution?.state === "available" && Array.isArray(distribution.buckets)) return distribution.buckets;
  return Array.from({ length: 10 }, (_, index) => ({
    rating: (index + 1) / 2,
    count: 0,
    relative_value: 0,
  }));
}

export function profileRatingCount(distribution) {
  return profileRatingBuckets(distribution).reduce(
    (total, bucket) => total + (Number.isFinite(bucket.count) && bucket.count > 0 ? bucket.count : 0),
    0,
  );
}
