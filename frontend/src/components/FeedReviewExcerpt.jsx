import { useLayoutEffect, useRef, useState } from "react";


export default function FeedReviewExcerpt({ children, lineLimit = 4 }) {
  const body = String(children ?? "");
  const rootRef = useRef(null);
  const [rendered, setRendered] = useState({ text: body, truncated: false });

  useLayoutEffect(() => {
    const root = rootRef.current;
    if (!root) return undefined;
    let active = true;

    function measure() {
      if (!active || !root.isConnected) return;
      const styles = getComputedStyle(root);
      const probe = document.createElement("span");
      Object.assign(probe.style, {
        position: "fixed",
        visibility: "hidden",
        pointerEvents: "none",
        display: "block",
        width: `${root.clientWidth}px`,
        fontFamily: styles.fontFamily,
        fontSize: styles.fontSize,
        fontStyle: styles.fontStyle,
        fontWeight: styles.fontWeight,
        letterSpacing: styles.letterSpacing,
        lineHeight: styles.lineHeight,
        whiteSpace: "normal",
      });
      document.body.append(probe);
      const maxHeight = Math.ceil(Number.parseFloat(styles.lineHeight) * lineLimit);
      probe.textContent = body;
      if (probe.scrollHeight <= maxHeight) {
        setRendered({ text: body, truncated: false });
        probe.remove();
        return;
      }

      let low = 0;
      let high = body.length;
      while (low < high) {
        const middle = Math.ceil((low + high) / 2);
        probe.textContent = `${body.slice(0, middle).trimEnd()}… Read more`;
        if (probe.scrollHeight <= maxHeight) low = middle;
        else high = middle - 1;
      }
      setRendered({ text: body.slice(0, low).trimEnd(), truncated: true });
      probe.remove();
    }

    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(root);
    document.fonts?.ready.then(measure);
    return () => {
      active = false;
      observer.disconnect();
    };
  }, [body, lineLimit]);

  return (
    <span className="home-feed-review" ref={rootRef}>
      {rendered.text}{rendered.truncated ? <>… <small>Read more</small></> : null}
    </span>
  );
}
