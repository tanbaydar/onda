import { useEffect, useRef } from "react";

export default function ConfirmDialog({ open, title, consequence, confirmLabel, onCancel, onConfirm }) {
  const ref = useRef(null);
  const closingReason = useRef(null);
  useEffect(() => {
    const dialog = ref.current;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) {
      closingReason.current = "external";
      dialog.close();
    }
  }, [open]);
  return (
    <dialog
      ref={ref}
      onCancel={(event) => {
        event.preventDefault();
        closingReason.current = "cancel";
        event.currentTarget.close();
      }}
      onClose={() => {
        const reason = closingReason.current;
        closingReason.current = null;
        if (reason === "confirm") onConfirm();
        if (reason === "cancel") onCancel();
      }}
    >
      <h2>{title}</h2>
      <p>{consequence}</p>
      <form method="dialog" onSubmit={(event) => { closingReason.current = event.nativeEvent.submitter?.value === "confirm" ? "confirm" : "cancel"; }}>
        <button type="submit" value="cancel">Cancel</button>
        <button className="destructive" type="submit" value="confirm">{confirmLabel}</button>
      </form>
    </dialog>
  );
}
