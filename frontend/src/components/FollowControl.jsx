import { followControlLabel } from "../followControl.js";

export default function FollowControl({ relationship, onChange, pending = false }) {
  if (!relationship) return null;
  return <button className="profile-follow-control" type="button" disabled={pending} aria-busy={pending} onClick={onChange}>{followControlLabel(relationship)}</button>;
}
