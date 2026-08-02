export function RatingStarGlyph({ fill }) {
  return (
    <span className="rating-star-glyph" aria-hidden="true">
      <span className="rating-star-outline">☆</span>
      <span className="rating-star-fill" style={{ "--star-fill": `${fill * 100}%` }}>★</span>
    </span>
  );
}

export default function RatingStars({ value, className = "" }) {
  const numericValue = Number(value);
  return (
    <span className={`rating-stars${className ? ` ${className}` : ""}`} aria-label={`${numericValue} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((star) => <RatingStarGlyph key={star} fill={Math.min(1, Math.max(0, numericValue - (star - 1)))} />)}
    </span>
  );
}
