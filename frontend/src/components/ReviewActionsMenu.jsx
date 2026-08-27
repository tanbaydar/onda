import { useEffect, useRef, useState } from "react";

export default function ReviewActionsMenu({ disabled = false, hasReview = false, onEditReview, onRemoveReview, onRemoveFromBeen }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const triggerRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    function closeOnOutsidePointer(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    }
    function closeOnEscape(event) {
      if (event.key === "Escape") {
        setOpen(false);
        triggerRef.current?.focus();
      }
    }
    document.addEventListener("pointerdown", closeOnOutsidePointer);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutsidePointer);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [open]);

  function choose(action) {
    setOpen(false);
    action();
  }

  return (
    <div className="review-actions-menu" ref={rootRef}>
      <button className="quiet-action review-actions-trigger menu-action" type="button" aria-haspopup="menu" aria-expanded={open} disabled={disabled} ref={triggerRef} onClick={() => setOpen((current) => !current)}>
        Edit <span aria-hidden="true">{open ? "▴" : "▾"}</span>
      </button>
      {open ? (
        <div className="review-actions-options" role="menu" aria-label="Review actions">
          <button className="menu-action" type="button" role="menuitem" onClick={() => choose(onEditReview)}>Edit review</button>
          {hasReview ? <button className="menu-action" type="button" role="menuitem" onClick={() => choose(onRemoveReview)}>Remove review</button> : null}
          <button className="menu-action review-actions-remove-entry" type="button" role="menuitem" onClick={() => choose(onRemoveFromBeen)}>Remove from Been</button>
        </div>
      ) : null}
    </div>
  );
}
