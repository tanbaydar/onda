import { useState } from "react";

import { fetchWithCsrf } from "../api.js";
import { classifyFavoriteError } from "../favoriteError.js";
import { FAVORITE_CONTROL_INITIAL, favoriteRequestRejected, favoriteRequestSettled, favoriteRequestStarted } from "../favoriteControlState.js";


export default function FavoriteControl({ path, state, onChanged, compact = false, row = false }) {
  const [request, setRequest] = useState(FAVORITE_CONTROL_INITIAL);
  const [hovered, setHovered] = useState(false);
  const [filled, setFilled] = useState(false);

  async function change() {
    setRequest(favoriteRequestStarted());
    try {
      const adding = !state.is_favorite;
      await fetchWithCsrf(path, { method: adding ? "PUT" : "DELETE" });
      setRequest(favoriteRequestSettled());
      if (adding) { setFilled(true); window.setTimeout(() => setFilled(false), 120); }
      onChanged();
    } catch (requestError) {
      const outcome = classifyFavoriteError(requestError);
      if (outcome.refetch) {
        onChanged();
      }
      setRequest(favoriteRequestRejected(outcome.message));
    }
  }

  const label = state.is_favorite ? (hovered ? "Remove" : "Favorited") : "Favorite";
  const contents = <><button className={`favorite-heart${row ? " favorite-heart-row" : ""}${state.is_favorite ? " is-favorite" : ""}${filled ? " just-filled" : ""}`} type="button" disabled={request.pending} aria-label={row ? "Remove favorite" : label} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)} onClick={change}><span aria-hidden="true">{state.is_favorite ? "♥" : "♡"}</span>{row ? null : <small>{label}</small>}</button>{request.message ? <p className="favorite-notice" role="alert">{request.message}</p> : null}</>;
  return compact ? <div className="owner-favorite">{contents}</div> : <section><h2>Favorite</h2>{contents}</section>;
}
