import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";


export default function AccountMenu({ user, onLogout }) {
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
      <button className="account-menu-trigger" type="button" aria-haspopup="menu" aria-expanded={open} ref={triggerRef} onClick={() => setOpen((current) => !current)}>
        @{user.username}
      </button>
      {open ? (
        <div className="account-menu-panel" role="menu">
          <Link role="menuitem" to="/settings/profile" onClick={() => setOpen(false)}>Edit profile</Link>
          <button role="menuitem" type="button" onClick={onLogout}>Log out</button>
        </div>
      ) : null}
    </div>
  );
}
