import { Link } from "react-router-dom";

export default function SystemStatePage({ title, children, actionTo = "/discover", actionLabel = "Return to Discover", busy = false }) {
  return (
    <main className="system-state-page" aria-busy={busy}>
      <div className="system-state-slot">
        <h1 className="functional-title">{title}</h1>
        <div className="system-state-copy">{children}</div>
        {actionTo ? <Link className="system-state-action mobile-target" to={actionTo}>{actionLabel}</Link> : null}
      </div>
    </main>
  );
}
