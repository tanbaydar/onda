import { useEffect, useState } from "react";

import { profileInitials } from "../profilePresentation.js";

export default function ProfileAvatar({ profile, small = false, className = "" }) {
  const [failedSource, setFailedSource] = useState(null);
  const classes = `profile-avatar${small ? " profile-avatar-small" : ""}${className ? ` ${className}` : ""}`;

  useEffect(() => setFailedSource(null), [profile.avatar]);

  if (profile.avatar && failedSource !== profile.avatar) return <img className={classes} src={profile.avatar} alt={`${profile.display_name}'s avatar`} onError={() => setFailedSource(profile.avatar)} />;
  return <span className={classes} aria-label={`${profile.display_name}'s initials avatar`}>{profileInitials(profile.display_name)}</span>;
}
