import { useRef, useState } from "react";

function valueAtPointer(event, root) {
  const rect = root.getBoundingClientRect();
  const raw = ((event.clientX - rect.left) / rect.width) * 5;
  return Math.min(5, Math.max(0.5, Math.ceil(raw * 2) / 2));
}

export default function StarInput({ value, disabled = false, onChange, onCommit }) {
  const rootRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const numericValue = value === "" ? 0 : Number(value);

  function updateFromPointer(event) {
    const next = valueAtPointer(event, rootRef.current);
    onChange(next);
    return next;
  }

  return (
    <div className="star-input-wrap">
      <div
        ref={rootRef}
        className="star-input"
        role="slider"
        tabIndex={disabled ? -1 : 0}
        aria-label="Your rating"
        aria-valuemin="0.5"
        aria-valuemax="5"
        aria-valuenow={numericValue || 0.5}
        aria-valuetext={numericValue ? `${numericValue.toFixed(1)} stars` : "No rating selected"}
        aria-disabled={disabled}
        onKeyDown={(event) => {
          if (disabled) return;
          if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
            event.preventDefault();
            onChange(Math.min(5, Math.max(0.5, (numericValue || 0.5) + (event.key === "ArrowRight" ? 0.5 : -0.5))));
          } else if (event.key === "Enter" && numericValue) {
            event.preventDefault();
            onCommit(numericValue);
          }
        }}
        onPointerDown={(event) => {
          if (disabled) return;
          event.currentTarget.setPointerCapture(event.pointerId);
          setDragging(true);
          updateFromPointer(event);
        }}
        onPointerMove={(event) => { if (dragging && !disabled) updateFromPointer(event); }}
        onPointerUp={(event) => {
          if (!dragging || disabled) return;
          const next = updateFromPointer(event);
          setDragging(false);
          onCommit(next);
        }}
        onPointerCancel={() => setDragging(false)}
      >
        {[1, 2, 3, 4, 5].map((star) => {
          const fill = Math.min(1, Math.max(0, numericValue - (star - 1)));
          return <span className="star-input-glyph" key={star}><span aria-hidden="true">☆</span><span className="star-input-fill" aria-hidden="true" style={{ width: `${fill * 100}%` }}>★</span></span>;
        })}
      </div>
      {numericValue ? <output>{numericValue.toFixed(1)}</output> : null}
    </div>
  );
}
