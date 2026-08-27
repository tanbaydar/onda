import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import DiscoverEventRow from "./DiscoverEventRow.jsx";
import { entityResultPath } from "../entityRoutes.js";
import ImageSlot from "./ImageSlot.jsx";
import ProfileAvatar from "./ProfileAvatar.jsx";
import ArtistAvatar from "./ArtistAvatar.jsx";

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
  return (
    <li>
      <Link className="search-result-row" to={resultPath(type, item)} onFocus={onFocus}>
        {type === "events" ? <ImageSlot name={item.title} src={item.cover_image_url} referrerPolicy="no-referrer" /> : null}
        {type === "artists" ? <ArtistAvatar artist={item} small /> : null}
        {type === "people" ? <ProfileAvatar profile={item} small className="search-avatar" /> : null}
        <span className="search-result-copy">
          <strong>{type === "people" ? item.display_name : item.title ?? item.name}</strong>
          <small>{type === "artists" ? "Artist" : type === "venues" ? item.city.name : type === "people" ? `@${item.username}` : `${item.venue.name} · ${item.event_date}`}</small>
        </span>
      </Link>
    </li>
  );
}

export default function SearchResults({ data, scope = "all", activeIndex, onActiveIndex, onViewAll, onResultOpen = () => {}, compact = false }) {
  const rootRef = useRef(null);
  useEffect(() => {
    if (activeIndex >= 0) rootRef.current?.querySelectorAll(".discover-event-row,.search-result-row")[activeIndex]?.focus();
  }, [activeIndex]);
  let rowIndex = -1;
  if (scope !== "all") {
    return <ul ref={rootRef} className={`search-results ${scope === "events" && !compact ? "discover-event-ledger" : ""}`} onClickCapture={onResultOpen}>{data.results.map((item) => { rowIndex += 1; const index = rowIndex; return scope === "events" ? <DiscoverEventRow key={item.id} event={item} compact variant={compact ? "overlay" : "standard"} onFocus={() => onActiveIndex(index)} /> : <ResultRow key={item.id} type={scope} item={item} onFocus={() => onActiveIndex(index)} />; })}</ul>;
  }
  return (
    <div className="search-groups" ref={rootRef}>
      {GROUPS.map(([type, label]) => {
        const group = data.groups[type];
        if (!group?.results.length) return null;
        return <section key={type}><h2 className="section-heading">{label}</h2><ul className={`search-results ${type === "events" && !compact ? "discover-event-ledger" : ""}`} onClickCapture={onResultOpen}>{group.results.map((item) => { rowIndex += 1; const index = rowIndex; return type === "events" ? <DiscoverEventRow key={item.id} event={item} compact variant={compact ? "overlay" : "standard"} onFocus={() => onActiveIndex(index)} /> : <ResultRow key={item.id} type={type} item={item} onFocus={() => onActiveIndex(index)} />; })}</ul>{group.total > 5 ? <button className="quiet-action" type="button" onClick={() => onViewAll(type)}>View all ({group.total})</button> : null}</section>;
      })}
    </div>
  );
}
