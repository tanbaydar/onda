export const FOLLOW_CONTROL_LABELS = [
  "Follow",
  "Unfollow",
  "Request to follow",
  "Requested",
];

export function followControlLabel(relationship) {
  if (relationship.outgoing_status === "pending") return "Requested";
  if (relationship.outgoing_status === "approved") return "Unfollow";
  return relationship.follow_action === "request" ? "Request to follow" : "Follow";
}
