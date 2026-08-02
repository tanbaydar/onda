import { useState } from "react";

import { fetchWithCsrf } from "../api.js";
import { classifyFavoriteError } from "../favoriteError.js";
import { FAVORITE_CONTROL_INITIAL, favoriteRequestRejected, favoriteRequestSettled, favoriteRequestStarted } from "../favoriteControlState.js";


export default function FavoriteControl({ path, state, onChanged, compact = false }) {
  const [request, setRequest] = useState(FAVORITE_CONTROL_INITIAL);

  async function change() {
    setRequest(favoriteRequestStarted());
    try {
      await fetchWithCsrf(path, { method: state.is_favorite ? "DELETE" : "PUT" });
      setRequest(favoriteRequestSettled());
      onChanged();
    } catch (requestError) {
      const outcome = classifyFavoriteError(requestError);
      if (outcome.refetch) {
        onChanged();
      }
      setRequest(favoriteRequestRejected(outcome.message));
    }
  }

  const contents = <><button className={compact ? "quiet-action" : undefined} type="button" disabled={request.pending} onClick={change}>{state.is_favorite ? "Remove favorite" : "Add favorite"}</button>{request.message ? <p className="favorite-notice" role="alert">{request.message}</p> : null}</>;
  return compact ? <div className="owner-favorite">{contents}</div> : <section><h2>Favorite</h2>{contents}</section>;
}
