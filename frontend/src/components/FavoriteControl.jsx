import { useState } from "react";

import { fetchWithCsrf } from "../api.js";


export default function FavoriteControl({ path, state, onChanged, onAuthenticationRequired }) {
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  async function change() {
    setSaving(true);
    setError(null);
    try {
      await fetchWithCsrf(path, { method: state.is_favorite ? "DELETE" : "PUT" });
      onChanged();
    } catch (requestError) {
      if (requestError.status === 401 || requestError.status === 403) {
        setError("Sign in required.");
        onAuthenticationRequired?.();
      } else if (requestError.status === 404 || requestError.status === 409) {
        onChanged();
        if (requestError.status === 409) {
          const messages = Object.values(requestError.data?.errors ?? {}).flat();
          setError(messages.join(" ") || "The favorite limit has been reached.");
        }
      } else {
        setError("The favorite could not be changed.");
      }
    } finally {
      setSaving(false);
    }
  }

  return <section><h2>Favorite</h2><button type="button" disabled={saving} onClick={change}>{state.is_favorite ? "Remove favorite" : "Add favorite"}</button>{error ? <p>{error}</p> : null}</section>;
}
