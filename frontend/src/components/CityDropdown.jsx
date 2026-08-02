import { useEffect, useId, useRef, useState } from "react";

export default function CityDropdown({
  cities,
  selectedCity,
  onSelect,
  label = "Browse city",
  nullOptionLabel = null,
  getOptionLabel = (city) => city.name,
}) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const optionRefs = useRef([]);
  const id = useId();
  const options = nullOptionLabel === null
    ? cities
    : [{ id: null, name: nullOptionLabel }, ...cities];
  const selectedIndex = Math.max(0, options.findIndex((city) => city.id === (selectedCity?.id ?? null)));
  const selectedLabel = selectedCity ? getOptionLabel(selectedCity) : nullOptionLabel;

  useEffect(() => {
    if (!open) return undefined;
    optionRefs.current[selectedIndex]?.focus();
    function closeOnOutsideClick(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    }
    document.addEventListener("pointerdown", closeOnOutsideClick);
    return () => document.removeEventListener("pointerdown", closeOnOutsideClick);
  }, [open, selectedIndex]);

  function moveFocus(index) {
    const next = (index + options.length) % options.length;
    optionRefs.current[next]?.focus();
  }

  function handleTriggerKeyDown(event) {
    if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
      event.preventDefault();
      setOpen(true);
    }
  }

  function handleOptionKeyDown(event, index) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveFocus(index + 1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      moveFocus(index - 1);
    } else if (event.key === "Home") {
      event.preventDefault();
      moveFocus(0);
    } else if (event.key === "End") {
      event.preventDefault();
      moveFocus(options.length - 1);
    } else if (event.key === "Escape") {
      event.preventDefault();
      setOpen(false);
      rootRef.current?.querySelector(".city-dropdown-trigger")?.focus();
    }
  }

  return (
    <div className="city-dropdown" ref={rootRef}>
      <span className="city-dropdown-label" id={`${id}-label`}>{label}</span>
      <button className="city-dropdown-trigger" type="button" aria-labelledby={`${id}-label ${id}-value`} aria-haspopup="listbox" aria-expanded={open} onClick={() => setOpen((value) => !value)} onKeyDown={handleTriggerKeyDown}>
        <span id={`${id}-value`}>{selectedLabel}</span><span aria-hidden="true">{open ? "↑" : "↓"}</span>
      </button>
      {open ? (
        <div className="city-dropdown-options" role="listbox" aria-labelledby={`${id}-label`}>
          {options.map((city, index) => {
            const optionLabel = city.id === null ? nullOptionLabel : getOptionLabel(city);
            const selected = city.id === (selectedCity?.id ?? null);
            return (
              <button key={city.id ?? "none"} ref={(element) => { optionRefs.current[index] = element; }} type="button" role="option" aria-selected={selected} onKeyDown={(event) => handleOptionKeyDown(event, index)} onClick={() => { onSelect(city.id); setOpen(false); }}>
                {optionLabel}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
