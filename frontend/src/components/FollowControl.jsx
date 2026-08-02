import { followControlLabel } from "../followControl.js";

export default function FollowControl({ relationship, onChange }) {
  if (!relationship) return null;
  return <button className="profile-follow-control" type="button" onClick={onChange}>{followControlLabel(relationship)}</button>;
}
