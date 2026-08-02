export function imageSlotInitial(name) {
  return String(name ?? "").trim().charAt(0).toUpperCase();
}

export function recentRatingVisible(summary) {
  return summary?.state === "available" && summary.count >= 3;
}
