export default function BeenControl({ marked = false, disabled = false, onMark, onRemove }) {
  const label = marked ? "Been" : "Mark Been";
  return (
    <button className={`been-control${marked ? " is-been" : ""}`} type="button" disabled={disabled} aria-label={marked ? "Remove from Been" : label} onClick={marked ? onRemove : onMark}>
      <img src={marked ? "/assets/been-hand-filled.svg" : "/assets/been-hand.svg"} alt="" aria-hidden="true" />
      <small>{label}</small>
    </button>
  );
}
