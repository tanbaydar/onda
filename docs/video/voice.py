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
MARK = re.compile(r"\{(\w+)\}|\{\+([0-9.]+)\}|\|")   # a cue, a pause in seconds, or a subtitle bar
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
        length = duration(BUILD / f"segment-{segment_id}.mp3") / TEMPO

        # first pass: a pause mark {+1.5} adds silence before the word that follows it
        pauses: list[tuple[int, float]] = []          # (character index, seconds)
        offset = 0
        for say, _ in lines:
            shift = 0
            for mark in MARK.finditer(say):
                if mark.group(2):
                    pauses.append((offset + mark.start() - shift, float(mark.group(2))))
                shift += len(mark.group(0))
            offset += len(plain(say)) + 1
        # a pause mark after the last word adds silence after the segment
        trailing = sum(seconds for position, seconds in pauses if position >= len(starts))
        pauses = [(position, seconds) for position, seconds in pauses if position < len(starts)]
        extra = [sum(seconds for position, seconds in pauses if position <= number)
                 for number in range(len(starts))]
        cuts = []                                      # (time in the segment, seconds of silence)
        for position, seconds in pauses:
            previous = position - 1
            while previous >= 0 and texts[index][previous] == " ":
                previous -= 1
            cut = 0.0 if previous < 0 else (ends[previous] + starts[position]) / 2
            cuts.append((cut, seconds))
        silence = sum(seconds for _, seconds in cuts)

        # second pass: the cues and the subtitles
        offset = 0
        for say, sub in lines:
            spoken = plain(say)
            shift = 0
            bars = [0]
            for mark in MARK.finditer(say):
                position = mark.start() - shift
                if mark.group(1):
                    at = min(offset + position, len(starts) - 1)
                    cues[mark.group(1)] = round(clock + starts[at] + extra[at], 3)
                elif not mark.group(2):
                    bars.append(position)
                shift += len(mark.group(0))
            bars.append(len(spoken))
            parts = [part.strip() for part in sub.split("|")]
            if len(parts) != len(bars) - 1:
                sys.exit(f"The two texts of a line have a different number of bars: {sub!r}")
            for part, first, after in zip(parts, bars, bars[1:]):
                if len(part) > MAX_SUBTITLE:
                    sys.exit(f"A subtitle has more than {MAX_SUBTITLE} characters. Add a bar: {part!r}")
                last = offset + len(spoken[:after].rstrip()) - 1
                subtitles.append({"start": round(clock + starts[offset + first] + extra[offset + first], 3),
                                  "end": round(clock + ends[last] + extra[last], 3), "text": part})
            offset += len(spoken) + 1

        # the sound of the segment: one piece between each two pauses
        edges = [0.0] + [cut for cut, _ in cuts] + [max(length, ends[-1]) + 0.05]
        waited = 0.0
        pieces = []
        for number, (first, last) in enumerate(zip(edges, edges[1:])):
            pieces.append((first, last, clock + first + waited))
            if number < len(cuts):
                waited += cuts[number][1]
        segments.append({"id": segment_id, "start": round(clock, 3), "end": round(clock + ends[-1] + silence, 3)})
        inputs.append((BUILD / f"segment-{segment_id}.mp3", pieces))
        clock += max(length, ends[-1]) + silence + trailing + GAP

    total = round(clock - GAP + TAIL, 3)
    # keep each subtitle on screen until the next one starts, with a maximum of 0.6 s more
    for current, following in zip(subtitles, subtitles[1:]):
        current["end"] = round(min(following["start"] - 0.04, current["end"] + 0.6), 3)
    subtitles[-1]["end"] = round(subtitles[-1]["end"] + 0.6, 3)

    # one voice track: each segment at its tempo and its start time, then loudness to -16 LUFS
    command = ["ffmpeg", "-y", "-v", "error"]
    filters = []
    names = []
    for number, (path, pieces) in enumerate(inputs):
        command += ["-i", str(path)]
        taps = "".join(f"[t{number}_{piece}]" for piece in range(len(pieces)))
        filters.append(f"[{number}:a]rubberband=tempo={TEMPO},asplit={len(pieces)}{taps}")
        for piece, (first, last, start) in enumerate(pieces):
            name = f"[a{number}_{piece}]"
            filters.append(f"[t{number}_{piece}]atrim=start={first:.4f}:end={last:.4f},asetpts=PTS-STARTPTS,"
                           f"adelay={round(start * 1000)}:all=1{name}")
            names.append(name)
    filters.append(f"{''.join(names)}amix=inputs={len(names)}:normalize=0,apad=whole_dur={total},"
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
