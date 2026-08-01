import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";

function CityDropdown({ cities, selectedCity, onSelect }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const optionRefs = useRef([]);
  const selectedIndex = cities.findIndex((city) => city.id === selectedCity.id);

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
    const next = (index + cities.length) % cities.length;
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
      moveFocus(cities.length - 1);
    } else if (event.key === "Escape") {
      event.preventDefault();
      setOpen(false);
      rootRef.current?.querySelector(".city-dropdown-trigger")?.focus();
    }
  }

  return (
    <div className="city-dropdown" ref={rootRef}>
      <span className="city-dropdown-label" id="city-dropdown-label">Browse city</span>
      <button className="city-dropdown-trigger" type="button" aria-labelledby="city-dropdown-label city-dropdown-value" aria-haspopup="listbox" aria-expanded={open} onClick={() => setOpen((value) => !value)} onKeyDown={handleTriggerKeyDown}>
        <span id="city-dropdown-value">{selectedCity.name}</span><span aria-hidden="true">{open ? "↑" : "↓"}</span>
      </button>
      {open ? (
        <div className="city-dropdown-options" role="listbox" aria-labelledby="city-dropdown-label">
          {cities.map((city, index) => (
            <button key={city.id} ref={(element) => { optionRefs.current[index] = element; }} type="button" role="option" aria-selected={city.id === selectedCity.id} onKeyDown={(event) => handleOptionKeyDown(event, index)} onClick={() => { onSelect(city.id); setOpen(false); }}>
              {city.name}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export default function DiscoverPage() {
  const [view, setView] = useState("upcoming");
  const [searchParams, setSearchParams] = useSearchParams();
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: null,
    cities: null,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, cities: null });
    fetchJson("/api/cities/", { signal: controller.signal })
      .then((data) => {
        setState({ loading: false, error: null, cities: data.results });
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, cities: null });
        }
      });
    return () => controller.abort();
  }, [retry]);

  const requestedCityId = searchParams.get("city_id");
  const selectedCity =
    state.cities?.find((city) => String(city.id) === requestedCityId) ??
    state.cities?.[0] ??
    null;

  useEffect(() => {
    if (selectedCity && String(selectedCity.id) !== requestedCityId) {
      setSearchParams({ city_id: String(selectedCity.id) }, { replace: true });
    }
  }, [requestedCityId, selectedCity, setSearchParams]);

  return (
    <main className="discover-page">
      <h1>Discover</h1>
      {state.loading ? <p>Loading cities.</p> : null}
      {state.error ? (
        <>
          <p>Cities could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {state.cities && state.cities.length === 0 ? (
        <p>No cities are available.</p>
      ) : null}
      {selectedCity ? (
        <>
          <CityDropdown cities={state.cities} selectedCity={selectedCity} onSelect={(cityId) => setSearchParams({ city_id: String(cityId) })} />
          <h2 className="discover-city">{selectedCity.name}</h2>
          <nav className="section-tabs" aria-label="Event timeframe">
            <button type="button" className={view === "upcoming" ? "active" : ""} aria-pressed={view === "upcoming"} onClick={() => setView("upcoming")}>Upcoming</button>
            <button type="button" className={view === "recent" ? "active" : ""} aria-pressed={view === "recent"} onClick={() => setView("recent")}>Recent</button>
          </nav>
          <EventList
            key={selectedCity.id}
            heading={`Upcoming events in ${selectedCity.name}`}
            scopeName="city_id"
            scopeId={selectedCity.id}
            when="upcoming"
            emptyMessage={`No upcoming events in ${selectedCity.name}.`}
            showCity={false}
            hidden={view !== "upcoming"}
            quietHeading
          />
          <EventList
            key={`recent-${selectedCity.id}`}
            heading={`Recent events in ${selectedCity.name}`}
            scopeName="city_id"
            scopeId={selectedCity.id}
            when="past"
            pageSize={10}
            emptyMessage={`No recent events in ${selectedCity.name}.`}
            showCity={false}
            hidden={view !== "recent"}
            quietHeading
          />
        </>
      ) : null}
    </main>
  );
}
