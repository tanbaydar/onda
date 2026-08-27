import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";


export default function AccountMenu({ user, onLogout, logoutState = { pending: false, error: null } }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const triggerRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    function closeOutside(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    }
    function closeOnEscape(event) {
      if (event.key === "Escape") {
        setOpen(false);
        triggerRef.current?.focus();
      }
    }
    document.addEventListener("pointerdown", closeOutside);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOutside);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [open]);

  return (
    <div className="account-menu" ref={rootRef}>
      <button className="account-menu-trigger menu-action" type="button" aria-haspopup="menu" aria-expanded={open} ref={triggerRef} onClick={() => setOpen((current) => !current)}>
        @{user.username}
      </button>
      {open ? (
        <div className="account-menu-panel">
          <div role="menu">
            <Link className="menu-action" role="menuitem" to="/settings/profile" onClick={() => setOpen(false)}>Edit profile</Link>
            <button className="menu-action" role="menuitem" type="button" disabled={logoutState.pending} onClick={onLogout}>{logoutState.pending ? "Logging out…" : "Log out"}</button>
          </div>
          {logoutState.error ? <div className="menu-feedback" role="alert"><p>Log out could not be completed.</p><button className="recovery-action" type="button" onClick={onLogout}>Retry</button></div> : null}
        </div>
      ) : null}
    </div>
  );
}
