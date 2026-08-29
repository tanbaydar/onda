export default function BeenControl({ disabled = false, onRemove }) {
  return (
    <button className="been-control" type="button" disabled={disabled} aria-label="Remove from Been" onClick={onRemove}>
      <span aria-hidden="true">✓</span>
      <small>Been</small>
    </button>
  );
}
