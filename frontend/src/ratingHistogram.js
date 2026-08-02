export function histogramBarHeight(relativeValue) {
  return relativeValue === 0 ? "var(--sp-2)" : `${relativeValue * 100}%`;
}

export function ratingTooltip(bucket) {
  return `${bucket.count} · ${bucket.rating.toFixed(1)}★`;
}

export function shouldRenderRatingHistogram(buckets) {
  return buckets.reduce((total, bucket) => total + (Number(bucket.count) || 0), 0) >= 5;
}
