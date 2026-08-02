import { profileInitials } from "../profilePresentation.js";

export default function ProfileAvatar({ profile, small = false }) {
  const className = `profile-avatar${small ? " profile-avatar-small" : ""}`;
  if (profile.avatar) return <img className={className} src={profile.avatar} alt={`${profile.display_name}'s avatar`} />;
  return <span className={className} aria-label={`${profile.display_name}'s initials avatar`}>{profileInitials(profile.display_name)}</span>;
}
