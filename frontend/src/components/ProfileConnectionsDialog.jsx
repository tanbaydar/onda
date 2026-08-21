import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson } from "../api.js";
import { profilePath } from "../profileRoutes.js";
import ProfileAvatar from "./ProfileAvatar.jsx";


function ConnectionList({ kind, onNavigate, username }) {
  const sentinelRef = useRef(null);
  const loadingMoreRef = useRef(false);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, loadingMore: false, error: null, data: null });

  useEffect(() => {
    const controller = new AbortController();
    loadingMoreRef.current = false;
    setState({ loading: true, loadingMore: false, error: null, data: null });
    fetchJson(`/api/users/${encodeURIComponent(username)}/${kind}/?page=1`, { signal: controller.signal, cache: "no-store" })
      .then((data) => setState({ loading: false, loadingMore: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") setState({ loading: false, loadingMore: false, error, data: null });
      });
    return () => controller.abort();
  }, [kind, retry, username]);

  async function loadMore() {
    const nextPage = state.data?.pagination.next_page;
    if (!nextPage || loadingMoreRef.current) return;
    loadingMoreRef.current = true;
    setState((current) => ({ ...current, loadingMore: true, error: null }));
    try {
      const page = await fetchJson(`/api/users/${encodeURIComponent(username)}/${kind}/?page=${nextPage}`, { cache: "no-store" });
      setState((current) => current.data ? {
        loading: false,
        loadingMore: false,
        error: null,
        data: { ...page, results: [...current.data.results, ...page.results] },
      } : current);
    } catch (error) {
      setState((current) => ({ ...current, loadingMore: false, error }));
    } finally {
      loadingMoreRef.current = false;
    }
  }

  useEffect(() => {
    const target = sentinelRef.current;
    if (!target || !state.data?.pagination.next_page || state.loadingMore || state.error) return undefined;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) loadMore();
    }, { root: target.closest(".profile-connection-panel"), rootMargin: "160px 0px" });
    observer.observe(target);
    return () => observer.disconnect();
  }, [state.data?.pagination.next_page, state.error, state.loadingMore]);

  if (state.loading) return <p className="profile-connection-status" role="status">Loading {kind}…</p>;
  if (state.error && !state.data) return <div className="profile-connection-status" role="alert"><p>The {kind} list could not be loaded.</p><button className="quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>;
  if (state.data.results.length === 0) return <p className="profile-connection-status">No {kind} yet.</p>;
  return (
    <>
      <ul className="profile-connection-list">
        {state.data.results.map((person) => (
          <li key={person.id}>
            <Link to={profilePath(person.username)} onClick={onNavigate}>
              <ProfileAvatar profile={person} small />
              <span><strong>{person.display_name}</strong><small>@{person.username}</small></span>
            </Link>
          </li>
        ))}
      </ul>
      {state.error ? <div className="profile-connection-more-error" role="alert"><span>More people could not be loaded.</span><button className="quiet-control" type="button" onClick={loadMore}>Retry</button></div> : null}
      {state.data.pagination.next_page ? <div className="profile-connection-sentinel" ref={sentinelRef} role="status" aria-live="polite">{state.loadingMore ? "Loading more people…" : ""}</div> : null}
    </>
  );
}


export default function ProfileConnectionsDialog({ counts, initialKind, onClose, open, profile }) {
  const dialogRef = useRef(null);
  const [kind, setKind] = useState(initialKind ?? "followers");

  useEffect(() => {
    if (open) setKind(initialKind);
  }, [initialKind, open]);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      className="profile-connections-dialog"
      ref={dialogRef}
      onCancel={(event) => { event.preventDefault(); event.currentTarget.close(); }}
      onClose={onClose}
      onMouseDown={(event) => { if (event.target === event.currentTarget) event.currentTarget.close(); }}
    >
      <div className="profile-connections-shell">
        <header><h2>@{profile.username}</h2><button type="button" aria-label="Close connections" onClick={() => dialogRef.current.close()}>×</button></header>
        <nav aria-label="Profile connections" role="tablist">
          <button type="button" role="tab" aria-selected={kind === "followers"} onClick={() => setKind("followers")}>Followers <span>{counts.followers}</span></button>
          <button type="button" role="tab" aria-selected={kind === "following"} onClick={() => setKind("following")}>Following <span>{counts.following}</span></button>
        </nav>
        <section className="profile-connection-panel" role="tabpanel" aria-label={kind}>
          {open ? <ConnectionList key={`${profile.username}:${kind}`} kind={kind} username={profile.username} onNavigate={() => dialogRef.current.close()} /> : null}
        </section>
      </div>
    </dialog>
  );
}
