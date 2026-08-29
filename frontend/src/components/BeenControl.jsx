export default function BeenControl({ disabled = false, onRemove }) {
  return (
    <button className="been-control" type="button" disabled={disabled} aria-label="Remove from Been" onClick={onRemove}>
      <img src="/assets/been-hand.svg" alt="" aria-hidden="true" />
      <small>Been</small>
    </button>
  );
}
