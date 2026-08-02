import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { EventItem } from "./EventList.jsx";
import { formatEventDateTime } from "../formatEventDateTime.js";
import { entityResultPath } from "../entityRoutes.js";
import ImageSlot from "./ImageSlot.jsx";

const GROUPS = [
  ["events", "Events"],
  ["artists", "Artists"],
  ["venues", "Venues"],
  ["people", "People"],
];

export function resultPath(type, item) {
  return entityResultPath(type, item);
}

function ResultRow({ type, item, onFocus }) {
  const navigate = useNavigate();
  return (
    <li>
      <button className="search-result-row" type="button" onFocus={onFocus} onClick={() => navigate(resultPath(type, item))}>
        {type === "events" ? <ImageSlot name={item.title} src={item.cover_image_url} referrerPolicy="no-referrer" /> : null}
        {type === "people" && item.avatar ? <img className="search-avatar" src={item.avatar} alt="" /> : null}
        <span className="search-result-copy">
          <strong>{type === "people" ? item.display_name : item.title ?? item.name}</strong>
          <small>{type === "artists" ? "Artist" : type === "venues" ? item.city.name : type === "people" ? `@${item.username}` : `${item.venue.name} · ${item.event_date}`}</small>
        </span>
      </button>
    </li>
  );
}

function CompactEventResultRow({ item, onFocus }) {
  const navigate = useNavigate();
  return (
    <li>
      <button className="compact-event-result-row" type="button" onFocus={onFocus} onClick={() => navigate(resultPath("events", item))}>
        <ImageSlot className="compact-event-thumb" name={item.title} src={item.cover_image_url} referrerPolicy="no-referrer" />
        <span className="search-result-copy">
          <strong>{item.title}</strong>
          <small>{formatEventDateTime(item.event_date, item.start_time)} · {item.venue.name}</small>
        </span>
      </button>
    </li>
  );
}

export default function SearchResults({ data, scope = "all", activeIndex, onActiveIndex, onViewAll, onResultOpen = () => {}, compact = false }) {
  const rootRef = useRef(null);
  useEffect(() => {
    if (activeIndex >= 0) rootRef.current?.querySelectorAll(".event-row h3 a,.search-result-row,.compact-event-result-row")[activeIndex]?.focus();
  }, [activeIndex]);
  let rowIndex = -1;
  if (scope !== "all") {
    return <ul ref={rootRef} className={`search-results ${scope === "events" && !compact ? "ledger" : ""}`} onClickCapture={onResultOpen}>{data.results.map((item) => { rowIndex += 1; const index = rowIndex; return scope === "events" ? (compact ? <CompactEventResultRow key={item.id} item={item} onFocus={() => onActiveIndex(index)} /> : <EventItem key={item.id} event={item} />) : <ResultRow key={item.id} type={scope} item={item} onFocus={() => onActiveIndex(index)} />; })}</ul>;
  }
  return (
    <div className="search-groups" ref={rootRef}>
      {GROUPS.map(([type, label]) => {
        const group = data.groups[type];
        if (!group?.results.length) return null;
        return <section key={type}><h2>{label}</h2><ul className={`search-results ${type === "events" && !compact ? "ledger" : ""}`} onClickCapture={onResultOpen}>{group.results.map((item) => { rowIndex += 1; const index = rowIndex; return type === "events" ? (compact ? <CompactEventResultRow key={item.id} item={item} onFocus={() => onActiveIndex(index)} /> : <EventItem key={item.id} event={item} />) : <ResultRow key={item.id} type={type} item={item} onFocus={() => onActiveIndex(index)} />; })}</ul>{group.total > 5 ? <button className="quiet-action" type="button" onClick={() => onViewAll(type)}>View all ({group.total})</button> : null}</section>;
      })}
    </div>
  );
}
