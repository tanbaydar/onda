import { useLayoutEffect, useRef, useState } from "react";

export default function ReviewExcerpt({ children }) {
  const [expanded, setExpanded] = useState(false);
  const [truncated, setTruncated] = useState(false);
  const bodyRef = useRef(null);
  useLayoutEffect(() => {
    if (!expanded && bodyRef.current) setTruncated(bodyRef.current.scrollHeight > bodyRef.current.clientHeight);
  }, [children, expanded]);
  return (
    <div className={`event-review-excerpt${expanded ? " expanded" : ""}`}>
      <p ref={bodyRef}>{children}</p>
      {truncated || expanded ? <button className="event-review-more" type="button" aria-expanded={expanded} onClick={() => setExpanded((value) => !value)}>{expanded ? "less" : "more"}</button> : null}
    </div>
  );
}
