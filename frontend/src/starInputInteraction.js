export function valueAtClientX(clientX, starRects) {
  if (!starRects.length) return 0.5;
  for (let index = 0; index < starRects.length; index += 1) {
    const rect = starRects[index];
    const next = starRects[index + 1];
    const effectiveRight = next ? (rect.right + next.left) / 2 : rect.right;
    if (clientX <= effectiveRight) return index + (clientX < (rect.left + rect.right) / 2 ? 0.5 : 1);
  }
  return 5;
}

export function keyboardStep(value, key) {
  const numericValue = Number(value) || 0.5;
  return Math.min(5, Math.max(0.5, numericValue + (key === "ArrowRight" ? 0.5 : -0.5)));
}
