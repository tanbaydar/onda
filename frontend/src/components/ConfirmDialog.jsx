import { useEffect, useRef } from "react";

export default function ConfirmDialog({ open, title, consequence, confirmLabel, onCancel, onConfirm }) {
  const ref = useRef(null);
  useEffect(() => {
    const dialog = ref.current;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);
  return (
    <dialog ref={ref} onCancel={(event) => { event.preventDefault(); onCancel(); }} onClose={onCancel}>
      <h2>{title}</h2>
      <p>{consequence}</p>
      <form method="dialog" onSubmit={(event) => { if (event.nativeEvent.submitter?.value === "confirm") onConfirm(); }}>
        <button type="submit" value="cancel">Cancel</button>
        <button className="destructive" type="submit" value="confirm">{confirmLabel}</button>
      </form>
    </dialog>
  );
}
