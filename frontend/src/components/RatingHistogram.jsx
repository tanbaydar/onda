import { useState } from "react";

import { histogramBarHeight, ratingTooltip } from "../ratingHistogram.js";

export default function RatingHistogram({ buckets }) {
  const [pinned, setPinned] = useState(null);
  return (
    <div className="rating-histogram">
      <div className="hist-bars" aria-label="Rating distribution">
        {buckets.map((bucket) => {
          const label = ratingTooltip(bucket);
          return (
            <button
              key={bucket.rating}
              className="hist-bar"
              type="button"
              aria-label={label}
              aria-pressed={pinned === bucket.rating}
              data-tooltip={label}
              style={{ "--bar-height": histogramBarHeight(bucket.relative_value) }}
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
