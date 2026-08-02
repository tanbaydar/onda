import { useEffect, useRef, useState } from "react";

import { PROFILE_REVIEW_SORTS } from "../profilePresentation.js";

export default function ProfileSortMenu({ value, onChange }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const optionRefs = useRef([]);
  const selectedIndex = Math.max(0, PROFILE_REVIEW_SORTS.findIndex((option) => option.value === value));
  const selected = PROFILE_REVIEW_SORTS[selectedIndex];

  useEffect(() => {
    if (!open) return undefined;
    optionRefs.current[selectedIndex]?.focus();
    function close(event) { if (!rootRef.current?.contains(event.target)) setOpen(false); }
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, [open, selectedIndex]);

  function move(index) {
    optionRefs.current[(index + PROFILE_REVIEW_SORTS.length) % PROFILE_REVIEW_SORTS.length]?.focus();
  }

  return (
    <div className="profile-sort-menu" ref={rootRef}>
      <button className="profile-sort-trigger" type="button" aria-label="Sort reviews" aria-haspopup="listbox" aria-expanded={open} onClick={() => setOpen((current) => !current)} onKeyDown={(event) => { if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) { event.preventDefault(); setOpen(true); } }}>{selected.label} {open ? "▴" : "▾"}</button>
      {open ? <div className="profile-sort-options" role="listbox" aria-label="Sort reviews">{PROFILE_REVIEW_SORTS.map((option, index) => <button key={option.value} ref={(element) => { optionRefs.current[index] = element; }} type="button" role="option" aria-selected={option.value === value} onKeyDown={(event) => { if (event.key === "ArrowDown") { event.preventDefault(); move(index + 1); } else if (event.key === "ArrowUp") { event.preventDefault(); move(index - 1); } else if (event.key === "Home") { event.preventDefault(); move(0); } else if (event.key === "End") { event.preventDefault(); move(PROFILE_REVIEW_SORTS.length - 1); } else if (event.key === "Escape") { event.preventDefault(); setOpen(false); rootRef.current?.querySelector(".profile-sort-trigger")?.focus(); } }} onClick={() => { onChange(option.value); setOpen(false); }}>{option.label}</button>)}</div> : null}
    </div>
  );
}
