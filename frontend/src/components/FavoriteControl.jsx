import { useState } from "react";

import { fetchWithCsrf } from "../api.js";
import { classifyFavoriteError } from "../favoriteError.js";


export default function FavoriteControl({ path, state, onChanged, compact = false }) {
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  async function change() {
    setSaving(true);
    setError(null);
    try {
      await fetchWithCsrf(path, { method: state.is_favorite ? "DELETE" : "PUT" });
      onChanged();
    } catch (requestError) {
      const outcome = classifyFavoriteError(requestError);
      if (outcome.refetch) {
        onChanged();
      }
      setError(outcome.message);
    } finally {
      setSaving(false);
    }
  }

  const contents = <><button className={compact ? "quiet-action" : undefined} type="button" disabled={saving} onClick={change}>{state.is_favorite ? "Remove favorite" : "Add favorite"}</button>{error ? <p role="alert">{error}</p> : null}</>;
  return compact ? <div className="owner-favorite">{contents}</div> : <section><h2>Favorite</h2>{contents}</section>;
}
