import { useEffect, useState } from "react";

import { fetchWithCsrf } from "../api.js";
import { classifyFavoriteError } from "../favoriteError.js";
import { FAVORITE_CONTROL_INITIAL, favoriteRequestRejected, favoriteRequestSettled, favoriteRequestStarted } from "../favoriteControlState.js";


export default function FavoriteControl({ path, state, onChanged, compact = false, row = false }) {
  const [request, setRequest] = useState(FAVORITE_CONTROL_INITIAL);
  const [hovered, setHovered] = useState(false);
  const [filled, setFilled] = useState(false);
  const [favorite, setFavorite] = useState(state);

  useEffect(() => {
    setFavorite(state);
  }, [state.added_at, state.is_favorite]);

  async function change() {
    setRequest(favoriteRequestStarted());
    try {
      const adding = !favorite.is_favorite;
      const response = await fetchWithCsrf(path, { method: adding ? "PUT" : "DELETE" });
      const nextFavorite = adding
        ? response.favorite
        : { is_favorite: false, added_at: null };
      setFavorite(nextFavorite);
      setRequest(favoriteRequestSettled());
      if (adding) { setFilled(true); window.setTimeout(() => setFilled(false), 120); }
      onChanged(nextFavorite);
    } catch (requestError) {
      const outcome = classifyFavoriteError(requestError);
      if (outcome.refetch) {
        onChanged(null);
      }
      setRequest(favoriteRequestRejected(outcome.message));
    }
  }

  const label = favorite.is_favorite ? (hovered ? "Remove" : "Favorited") : "Favorite";
  const contents = <><button className={`favorite-heart${row ? " favorite-heart-row" : ""}${favorite.is_favorite ? " is-favorite" : ""}${filled ? " just-filled" : ""}`} type="button" disabled={request.pending} aria-busy={request.pending} aria-label={row ? "Remove favorite" : label} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)} onClick={change}><span aria-hidden="true">{favorite.is_favorite ? "♥" : "♡"}</span>{row ? null : <small>{label}</small>}</button>{request.message ? <p className="favorite-notice" role="alert">{request.message}</p> : null}</>;
  if (row) return <div className="profile-favorite-control">{contents}</div>;
  return compact ? <div className="owner-favorite">{contents}</div> : <section><h2>Favorite</h2>{contents}</section>;
}
