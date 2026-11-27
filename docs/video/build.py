#!/usr/bin/env python3
"""Join the picture, the voice track and the subtitles into the final video.

Run:    python3 docs/video/build.py PICTURE.mp4 [OUTPUT.mp4]
Needs:  ffmpeg with libx264 and libass, and the General Sans typeface.

PICTURE.mp4 is the render of scene.py (no sound). voice.py makes the other inputs:
narration.m4a and timings.json. The script writes build/subtitles.ass, then
it writes the final file. The default output is docs/assets/video/onda-how-it-works.mp4.

The subtitles are part of the picture, because the GitHub player has no subtitle control.
The same lines are in the .srt and .vtt files for other players.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
OUTPUT = HERE.parent / "assets" / "video" / "onda-how-it-works.mp4"

FONT = "General Sans Medium"
SIZE = 50                    # in pixels of a 1080-line picture
INK = "&H00E6DFDA"           # the text color, as blue-green-red
EDGE = "&H00120F0D"          # the background color of the video
MARGIN = 54                  # from the bottom edge of the picture to the text

HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Line,{FONT},{SIZE},{INK},{INK},{EDGE},{EDGE},0,0,0,0,100,100,0.3,0,1,4,0,2,120,120,{MARGIN},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def stamp(seconds: float) -> str:
    centis = round(seconds * 100)
    hours, rest = divmod(centis, 360_000)
    minutes, rest = divmod(rest, 6_000)
    secs, centis = divmod(rest, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def write_subtitles(path: Path) -> int:
    lines = json.loads((HERE / "timings.json").read_text())["subtitles"]
    events = "".join(
        f"Dialogue: 0,{stamp(line['start'])},{stamp(line['end'])},Line,,0,0,0,,{{\\fad(70,70)}}{line['text']}\n"
        for line in lines
    )
    path.write_text(HEADER + events)
    return len(lines)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    picture = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else OUTPUT
    BUILD.mkdir(exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    subtitles = BUILD / "subtitles.ass"
    count = write_subtitles(subtitles)
    total = json.loads((HERE / "timings.json").read_text())["duration"]
    # the filter reads the subtitle file by a relative name, so that no path needs an escape
    command = [
        "ffmpeg", "-y", "-v", "error", "-stats",
        "-i", str(picture), "-i", str(HERE / "narration.m4a"),
        "-vf", "subtitles=subtitles.ass",
        "-map", "0:v:0", "-map", "1:a:0", "-t", str(total),
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-level", "4.2", "-tune", "animation",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
        str(output),
    ]
    subprocess.run(command, check=True, cwd=BUILD)
    size = output.stat().st_size / 1_048_576
    print(f"{output}  {size:.1f} MiB, {count} subtitle lines, {total} s")


if __name__ == "__main__":
    main()
