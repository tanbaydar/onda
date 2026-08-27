import { useEffect, useRef, useState } from "react";

import { PROFILE_REVIEW_SORTS } from "../profilePresentation.js";

export default function SortMenu({ value, onChange, options = PROFILE_REVIEW_SORTS }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const optionRefs = useRef([]);
  const selectedIndex = Math.max(0, options.findIndex((option) => option.value === value));
  const selected = options[selectedIndex];

  useEffect(() => {
    if (!open) return undefined;
    optionRefs.current[selectedIndex]?.focus();
    function close(event) { if (!rootRef.current?.contains(event.target)) setOpen(false); }
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, [open, selectedIndex]);

  function move(index) {
    optionRefs.current[(index + options.length) % options.length]?.focus();
  }

  return (
    <div className="sort-menu" ref={rootRef}>
      <button className="sort-menu-trigger menu-action" type="button" aria-label="Sort reviews" aria-haspopup="listbox" aria-expanded={open} onClick={() => setOpen((current) => !current)} onKeyDown={(event) => { if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) { event.preventDefault(); setOpen(true); } }}>{selected.label} {open ? "▴" : "▾"}</button>
      {open ? <div className="sort-menu-options" role="listbox" aria-label="Sort reviews">{options.map((option, index) => <button className="menu-action" key={option.value} ref={(element) => { optionRefs.current[index] = element; }} type="button" role="option" aria-selected={option.value === value} onKeyDown={(event) => { if (event.key === "ArrowDown") { event.preventDefault(); move(index + 1); } else if (event.key === "ArrowUp") { event.preventDefault(); move(index - 1); } else if (event.key === "Home") { event.preventDefault(); move(0); } else if (event.key === "End") { event.preventDefault(); move(options.length - 1); } else if (event.key === "Escape") { event.preventDefault(); setOpen(false); rootRef.current?.querySelector(".sort-menu-trigger")?.focus(); } }} onClick={() => { onChange(option.value); setOpen(false); }}>{option.label}</button>)}</div> : null}
    </div>
  );
}
