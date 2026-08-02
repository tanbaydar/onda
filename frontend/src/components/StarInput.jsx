import { useRef, useState } from "react";
import { keyboardStep, valueAtClientX } from "../starInputInteraction.js";
import { RatingStarGlyph } from "./RatingStars.jsx";

export default function StarInput({ value, disabled = false, onChange, onCommit }) {
  const rootRef = useRef(null);
  const dragRef = useRef(false);
  const [dragging, setDragging] = useState(false);
  const [preview, setPreview] = useState(null);
  const numericValue = value === "" ? 0 : Number(value);
  const displayValue = preview ?? numericValue;

  function pointerValue(event) {
    const starRects = Array.from(rootRef.current.children, (star) => star.getBoundingClientRect());
    return valueAtClientX(event.clientX, starRects);
  }

  function stopDragging() {
    dragRef.current = false;
    setDragging(false);
    setPreview(null);
  }

  return (
    <div className="star-input-wrap">
      <div
        ref={rootRef}
        className={`star-input${preview !== null && !dragging ? " is-previewing" : ""}`}
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
            onChange(keyboardStep(numericValue, event.key));
          } else if (event.key === "Enter" && numericValue) {
            event.preventDefault();
            onCommit(numericValue);
          }
        }}
        onPointerDown={(event) => {
          if (disabled) return;
          event.preventDefault();
          event.currentTarget.focus();
          event.currentTarget.setPointerCapture(event.pointerId);
          dragRef.current = true;
          setDragging(true);
          setPreview(pointerValue(event));
        }}
        onPointerMove={(event) => {
          if (disabled) return;
          if (dragRef.current || event.pointerType === "mouse") setPreview(pointerValue(event));
        }}
        onPointerLeave={() => { if (!dragRef.current) setPreview(null); }}
        onPointerUp={(event) => {
          if (!dragRef.current || disabled) return;
          const next = pointerValue(event);
          onChange(next);
          onCommit(next);
          stopDragging();
        }}
        onPointerCancel={stopDragging}
        onLostPointerCapture={() => { if (dragRef.current) stopDragging(); }}
      >
        {[1, 2, 3, 4, 5].map((star) => {
          const fill = Math.min(1, Math.max(0, displayValue - (star - 1)));
          return <span className="star-input-glyph" key={star}><RatingStarGlyph fill={fill} /></span>;
        })}
      </div>
      {displayValue ? <output>{displayValue.toFixed(1)}</output> : null}
    </div>
  );
}
