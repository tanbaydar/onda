import { useId } from "react";

import {
  histogramBarHeight,
  ratingDistributionDescription,
} from "../ratingHistogram.js";

export default function RatingHistogram({ buckets, className = "", staticLabel = null }) {
  const descriptionId = useId();
  const description = [staticLabel, ratingDistributionDescription(buckets)].filter(Boolean).join(" ");

  return (
    <div className={`rating-histogram ${className}`.trim()}>
      <div role="img" aria-label="Rating distribution chart" aria-describedby={descriptionId}>
        <div className="hist-bars" aria-hidden="true">
          {buckets.map((bucket) => (
            <span
              key={bucket.rating}
              className={`hist-bar ${bucket.relative_value === 0 ? "is-zero" : ""}`.trim()}
              style={{ "--bar-height": histogramBarHeight(bucket.relative_value) }}
            >
              <span className="hist-fill" />
            </span>
          ))}
        </div>
        <div className="hist-axis" aria-hidden="true"><span>½</span><span>5</span></div>
      </div>
      <p className="sr-only" id={descriptionId}>{description}</p>
    </div>
  );
}
