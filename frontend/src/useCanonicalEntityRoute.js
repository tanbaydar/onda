import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { entityIdFromRoute } from "./entityRoutes.js";

export function canonicalReplacement(pathname, entity, pathBuilder) {
  if (!entity) return null;
  const canonical = pathBuilder(entity);
  return pathname === canonical ? null : canonical;
}

export default function useCanonicalEntityRoute(routeKey, entity, pathBuilder) {
  const location = useLocation();
  const navigate = useNavigate();
  const id = entityIdFromRoute(routeKey);

  useEffect(() => {
    const pathname = canonicalReplacement(location.pathname, entity, pathBuilder);
    if (pathname) {
      navigate({ pathname, search: location.search, hash: location.hash }, { replace: true });
    }
  }, [entity, location.hash, location.pathname, location.search, navigate, pathBuilder]);

  return id;
}
