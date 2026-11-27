#!/usr/bin/env python3
"""Check that each animation starts at its word.

Run:    python3 docs/video/check_sync.py
Needs:  Manim Community. The check draws no frames, and it takes some seconds.

The scene waits for a cue before it starts an animation. If the animations
before a cue are too long, the scene reaches the cue late, and the picture
is behind the voice. This check runs the scene and lists each late cue.
The exit status is 1 if a cue is more than LIMIT seconds late, or if the
picture and the voice track have different lengths.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import tempconfig  # noqa: E402

import kit  # noqa: E402

LIMIT = 0.12          # seconds. A person does not see a smaller delay.
late: list[tuple[float, float]] = []
wait_until = kit.CueScene.until


def until(self, time: float) -> None:
    if self.clock - time > 1 / 60:
        late.append((time, self.clock - time))
    wait_until(self, time)


def main() -> int:
    kit.CueScene.until = until
    import scene

    options = {"dry_run": True, "frame_rate": 60, "disable_caching": True, "verbosity": "ERROR", "progress_bar": "none"}
    with tempconfig(options):
        film = scene.OndaExplainer()
        film.render()
    length, voice = film.renderer.time, film.total
    worst = 0.0
    for time, delay in late:
        name, _ = min(film.cues.items(), key=lambda item: abs(item[1] - time))
        mark = "LATE" if delay > LIMIT else "ok"
        print(f"{mark:4s}  {delay:5.2f} s late at {time:7.2f} s, near the cue '{name}'")
        worst = max(worst, delay)
    print(f"{len(film.cues)} cues. Worst delay {worst:.2f} s. Picture {length:.2f} s, voice track {voice:.2f} s.")
    return 1 if worst > LIMIT or abs(length - voice) > 0.05 else 0


if __name__ == "__main__":
    sys.exit(main())
