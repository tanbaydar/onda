#!/usr/bin/env python3
"""Make the voice track, the cue times and the subtitles of the video.

Run:    ELEVENLABS_API_KEY=... python3 docs/video/voice.py
Needs:  ffmpeg on the PATH. No Python package.

Output in docs/video/build/ (not in git):
  segment-<id>.mp3   one file for each segment, from the voice service
Output in docs/video/:
  narration.m4a      the full voice track at -16 LUFS (not in git)
  timings.json       the time of each cue and of each subtitle line
Output in docs/assets/video/:
  onda-how-it-works.srt, onda-how-it-works.vtt

The script keeps a segment file if it is there. Delete the file to make a new take.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from narration import GAP, LEAD_IN, MODEL_ID, SEGMENTS, TAIL, TEMPO, VOICE_ID

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
ASSETS = HERE.parent / "assets" / "video"
CUE = re.compile(r"\{(\w+)\}")
MARK = re.compile(r"\{(\w+)\}|\|")          # a cue mark, or a bar that splits the subtitle
API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_192"
MAX_SUBTITLE = 48          # characters in one subtitle line


def plain(text: str) -> str:
    return MARK.sub("", text)


def synthesize(segment_id: str, text: str, before: str, after: str) -> dict:
    """Return the alignment of one segment. Call the service only if the file is absent."""
    audio = BUILD / f"segment-{segment_id}.mp3"
    meta = BUILD / f"segment-{segment_id}.json"
    if audio.exists() and meta.exists():
        saved = json.loads(meta.read_text())
        if saved["text"] == text:
            return saved["alignment"]
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY to make a new take of the voice.")
    body = {"text": text, "model_id": MODEL_ID, "previous_text": before, "next_text": after, "seed": 847}
    request = urllib.request.Request(
        API.format(voice=VOICE_ID), data=json.dumps(body).encode(), method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as error:
        sys.exit(f"Voice service returned {error.code}: {error.read()[:400]!r}")
    audio.write_bytes(base64.b64decode(data["audio_base64"]))
    meta.write_text(json.dumps({"text": text, "alignment": data["alignment"]}))
    return data["alignment"]


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def stamp(seconds: float, separator: str) -> str:
    millis = round(seconds * 1000)
    hours, rest = divmod(millis, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    texts = [" ".join(plain(say) for say, _ in lines) for _, lines in SEGMENTS]
    cues: dict[str, float] = {}
    subtitles: list[dict] = []
    segments: list[dict] = []
    clock = LEAD_IN
    inputs: list[str] = []

    for index, (segment_id, lines) in enumerate(SEGMENTS):
        before = " ".join(texts[:index])[-400:]
        after = " ".join(texts[index + 1:])[:400]
        alignment = synthesize(segment_id, texts[index], before, after)
        starts = [time / TEMPO for time in alignment["character_start_times_seconds"]]
        ends = [time / TEMPO for time in alignment["character_end_times_seconds"]]
        if len(starts) != len(texts[index]):
            sys.exit(f"Alignment of {segment_id} has {len(starts)} characters, text has {len(texts[index])}.")
        offset = 0
        for say, sub in lines:
            spoken = plain(say)
            # a mark names the position, in the spoken text, of the word that follows it
            shift = 0
            cuts = [0]
            for mark in MARK.finditer(say):
                position = mark.start() - shift
                if mark.group(1):
                    cues[mark.group(1)] = round(clock + starts[min(offset + position, len(starts) - 1)], 3)
                else:
                    cuts.append(position)
                shift += len(mark.group(0))
            cuts.append(len(spoken))
            parts = [part.strip() for part in sub.split("|")]
            if len(parts) != len(cuts) - 1:
                sys.exit(f"The two texts of a line have a different number of bars: {sub!r}")
            for part, first, after in zip(parts, cuts, cuts[1:]):
                if len(part) > MAX_SUBTITLE:
                    sys.exit(f"A subtitle has more than {MAX_SUBTITLE} characters. Add a bar: {part!r}")
                last = offset + len(spoken[:after].rstrip()) - 1
                subtitles.append({"start": round(clock + starts[offset + first], 3),
                                  "end": round(clock + ends[last], 3), "text": part})
            offset += len(spoken) + 1
        length = duration(BUILD / f"segment-{segment_id}.mp3") / TEMPO
        segments.append({"id": segment_id, "start": round(clock, 3), "end": round(clock + ends[-1], 3)})
        inputs.append((BUILD / f"segment-{segment_id}.mp3", clock))
        clock += max(length, ends[-1]) + GAP

    total = round(clock - GAP + TAIL, 3)
    # keep each subtitle on screen until the next one starts, with a maximum of 0.6 s more
    for current, following in zip(subtitles, subtitles[1:]):
        current["end"] = round(min(following["start"] - 0.04, current["end"] + 0.6), 3)
    subtitles[-1]["end"] = round(subtitles[-1]["end"] + 0.6, 3)

    # one voice track: each segment at its tempo and its start time, then loudness to -16 LUFS
    command = ["ffmpeg", "-y", "-v", "error"]
    filters = []
    for number, (path, start) in enumerate(inputs):
        command += ["-i", str(path)]
        filters.append(f"[{number}:a]rubberband=tempo={TEMPO},adelay={round(start * 1000)}:all=1[a{number}]")
    mix = "".join(f"[a{number}]" for number in range(len(inputs)))
    filters.append(f"{mix}amix=inputs={len(inputs)}:normalize=0,apad=whole_dur={total},"
                   f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[out]")
    command += ["-filter_complex", ";".join(filters), "-map", "[out]", "-t", str(total),
                "-c:a", "aac", "-b:a", "192k", str(HERE / "narration.m4a")]
    subprocess.run(command, check=True)

    (HERE / "timings.json").write_text(json.dumps(
        {"duration": total, "segments": segments, "cues": cues, "subtitles": subtitles}, indent=1) + "\n")
    srt = "".join(
        f"{number}\n{stamp(item['start'], ',')} --> {stamp(item['end'], ',')}\n{item['text']}\n\n"
        for number, item in enumerate(subtitles, start=1)
    )
    vtt = "WEBVTT\n\n" + "".join(
        f"{stamp(item['start'], '.')} --> {stamp(item['end'], '.')}\n{item['text']}\n\n" for item in subtitles
    )
    (ASSETS / "onda-how-it-works.srt").write_text(srt)
    (ASSETS / "onda-how-it-works.vtt").write_text(vtt)
    print(f"duration {total} s, {len(cues)} cues, {len(subtitles)} subtitle lines")
    for segment in segments:
        print(f"  {segment['id']:9s} {segment['start']:7.2f} to {segment['end']:7.2f}")


if __name__ == "__main__":
    main()
