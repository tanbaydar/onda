import { useLayoutEffect, useRef, useState } from "react";

export default function ReviewExcerpt({ children, prefix = null }) {
  const [expanded, setExpanded] = useState(false);
  const [truncated, setTruncated] = useState(false);
  const bodyRef = useRef(null);
  useLayoutEffect(() => {
    if (!expanded && bodyRef.current) setTruncated(bodyRef.current.scrollHeight > bodyRef.current.clientHeight);
  }, [children, expanded]);
  return (
    <div className={`event-review-excerpt${expanded ? " expanded" : ""}`}>
      <p ref={bodyRef}>{prefix}{prefix ? " " : null}{children}</p>
      {truncated || expanded ? <button className="event-review-more mobile-target" type="button" aria-expanded={expanded} onClick={() => setExpanded((value) => !value)}>{expanded ? "Show less" : "Read more"}</button> : null}
    </div>
  );
}
