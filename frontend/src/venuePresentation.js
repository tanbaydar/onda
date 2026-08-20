function clean(value) {
  return typeof value === "string" ? value.trim() : "";
}

function countryName(countryCode, locale) {
  const code = clean(countryCode).toUpperCase();
  if (!code) return "";

  try {
    return new Intl.DisplayNames([locale], { type: "region" }).of(code) || code;
  } catch {
    return code;
  }
}

export function formatVenueLocation(city, locale = "en") {
  if (!city) return "";

  const cityName = clean(city.name);
  const region = clean(city.region_name) || clean(city.region_code);
  const distinctRegion = region.toLocaleLowerCase(locale) === cityName.toLocaleLowerCase(locale) ? "" : region;
  const locality = [cityName, distinctRegion].filter(Boolean).join(", ");
  const country = countryName(city.country_code, locale);
  const countryAlreadyNamed = [cityName, distinctRegion]
    .filter(Boolean)
    .some((part) => part.toLocaleLowerCase(locale) === country.toLocaleLowerCase(locale));

  return [locality, countryAlreadyNamed ? "" : country].filter(Boolean).join(" · ");
}
