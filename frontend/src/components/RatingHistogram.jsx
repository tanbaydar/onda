import { useState } from "react";

import { histogramBarHeight, ratingTooltip } from "../ratingHistogram.js";

export default function RatingHistogram({ buckets, className = "", staticLabel = null }) {
  const [pinned, setPinned] = useState(null);
  return (
    <div className={`rating-histogram ${className}`.trim()} role={staticLabel ? "img" : undefined} aria-label={staticLabel ?? undefined}>
      <div className="hist-bars" aria-label={staticLabel ? undefined : "Rating distribution"} aria-hidden={staticLabel ? true : undefined}>
        {buckets.map((bucket) => {
          const label = ratingTooltip(bucket);
          const barClassName = `hist-bar ${bucket.relative_value === 0 ? "is-zero" : ""}`.trim();
          const barStyle = { "--bar-height": histogramBarHeight(bucket.relative_value) };
          if (staticLabel) {
            return <span key={bucket.rating} className={barClassName} style={barStyle}><span className="hist-fill" /></span>;
          }
          return (
            <button
              key={bucket.rating}
              className={barClassName}
              type="button"
              aria-label={label}
              aria-pressed={pinned === bucket.rating}
              data-tooltip={label}
              style={barStyle}
              onClick={() => setPinned((value) => value === bucket.rating ? null : bucket.rating)}
            >
              <span className="hist-fill" aria-hidden="true" />
            </button>
          );
        })}
      </div>
      <div className="hist-axis" aria-hidden="true"><span>½</span><span>5</span></div>
    </div>
  );
}
