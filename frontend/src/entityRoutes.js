const MAX_SLUG_LENGTH = 60;

const ASCII_FOLD = new Map([
  ["æ", "ae"], ["ǽ", "ae"], ["œ", "oe"], ["ß", "ss"],
  ["ø", "o"], ["ł", "l"], ["đ", "d"], ["ð", "d"], ["þ", "th"],
]);

export function entitySlug(value) {
  const folded = String(value ?? "")
    .normalize("NFKD")
    .toLowerCase()
    .replace(/[æǽœßøłđðþ]/g, (character) => ASCII_FOLD.get(character))
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return folded.slice(0, MAX_SLUG_LENGTH).replace(/-+$/g, "");
}

export function entityIdFromRoute(value) {
  const match = String(value ?? "").match(/(?:^|-)([0-9]+)$/);
  if (!match) return null;
  const id = Number(match[1]);
  return Number.isSafeInteger(id) && id > 0 ? id : null;
}

function entityPath(prefix, entity, labelKey) {
  const id = Number(entity?.id);
  if (!Number.isSafeInteger(id) || id < 1) throw new TypeError("A positive entity ID is required.");
  const slug = entitySlug(entity[labelKey]);
  return `/${prefix}/${slug ? `${slug}-` : ""}${id}`;
}

export const eventPath = (event) => entityPath("e", event, "title");
export const venuePath = (venue) => entityPath("v", venue, "name");
export const artistPath = (artist) => entityPath("a", artist, "name");

export function entityResultPath(type, item) {
  if (type === "events") return eventPath(item);
  if (type === "venues") return venuePath(item);
  if (type === "artists") return artistPath(item);
  return `/u/${item.username}`;
}
