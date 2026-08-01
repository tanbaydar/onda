import { useState } from "react";

export default function ExpandableText({ children, feed = false, destination = null }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <>
      <p className={`review-body ${expanded ? "" : "is-clamped"} ${feed ? "feed-review" : ""}`}>{children}</p>
      {feed && destination ? <p><a className="quiet-action" href={destination}>Read on event page</a></p> : null}
      {!feed ? <button className="quiet-action" type="button" aria-expanded={expanded} onClick={() => setExpanded((value) => !value)}>{expanded ? "Show less" : "Read more"}</button> : null}
    </>
  );
}
