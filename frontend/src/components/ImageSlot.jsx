import { useEffect, useState } from "react";
import { imageSlotInitial } from "../polishPresentation.js";

export default function ImageSlot({ name, src = null, className = "", alt = "", referrerPolicy, loading = "lazy" }) {
  const [failedSource, setFailedSource] = useState(null);

  useEffect(() => setFailedSource(null), [src]);

  if (src && failedSource !== src) return <img className={className || undefined} src={src} alt={alt} loading={loading} referrerPolicy={referrerPolicy} onError={() => setFailedSource(src)} />;
  return <span className={`image-slot${className ? ` ${className}` : ""}`} aria-hidden="true"><span>{imageSlotInitial(name)}</span></span>;
}
