[Onda](../../README.md) / [Documentation](../README.md) / Video source

# The video: each scene is code

> **For** engineers who want to change the video, or make one for a different system. **Read time** 4 minutes.

[The video](../assets/video/onda-how-it-works.mp4) follows one rating from the tap of one person to the feed of a friend.
Its length is 1 minute 56 seconds. No person moved clips on a timeline. Five steps make the file from one text.

<p align="center">
  <a href="../assets/video/onda-how-it-works.mp4"><img src="../assets/video/poster.png" alt="Play the video: how Onda works, in 1 minute 56 seconds" width="720"></a>
</p>

## In brief

- The narration is text with cue marks. A cue mark gives a name to the word that follows it.
- The voice service returns the time of each character. Thus each cue has a time.
- Each animation waits for its cue. If the voice changes, the picture follows it.
- A check runs the scene with no frames, and it finds each animation that starts late.
- I gave the brief. Claude Code wrote the script, the scenes and the tools.

## Who did what

| Part | Who | How |
|---|---|---|
| The brief: the audience, the story line, the style | I | A conversation with Claude Code |
| The script, the scenes, the tools, and the review of the frames | Claude Code | Python, [Manim](https://www.manim.community/) and `ffmpeg` |
| The voice | [ElevenLabs](https://elevenlabs.io/) | A voice from my account. The API returns the sound and the time of each character |
| The facts | The code of this repository | Each number and each status code is in [API](../API.md), [Database](../DATABASE.md), [Ingestion](../INGESTION.md) or [Home feed](../HOME_FEED.md) |

## The pipeline

| Step | File | Input | Output |
|---|---|---|---|
| 1. Words | [`narration.py`](narration.py) | | The text of each line, with cue marks |
| 2. Voice | [`voice.py`](voice.py) | The words | `narration.m4a`, [`timings.json`](timings.json), and the subtitles as `.srt` and `.vtt` files |
| 3. Picture | [`scene.py`](scene.py) and [`kit.py`](kit.py) | The cue times | A picture of 1920 by 1080 at 60 frames for each second, with no sound |
| 4. Check | [`check_sync.py`](check_sync.py) | The scene and the cue times | A list of the late cues |
| 5. Join | [`build.py`](build.py) | The picture, the voice and the subtitle times | [`onda-how-it-works.mp4`](../assets/video/onda-how-it-works.mp4) |

## How the picture follows the voice

A line of the narration has a text for the voice and a text for the subtitle:

```python
("{second}Send it again: {c200}two hundred. {onerow}Still one row.",
 "Send it again: 200. Still one row."),
```

`voice.py` removes the marks and sends the text to the voice service.
The answer has the sound and the start time of each character.
The script writes the time of the word that follows each mark:

```json
"second": 18.791, "c200": 19.782, "onerow": 20.931
```

The scene waits for a cue, and then it starts the animation:

```python
self.cue("c200", -0.1)        # 0.1 s before the words "two hundred"
self.play(FadeIn(ok, shift=LEFT * 0.3), FadeIn(ok_label, shift=LEFT * 0.3), run_time=0.35)
```

No animation has a fixed time from the start of the video.
Thus, for a new take of the voice or a different speed, no change in the scene is necessary.

### The check

A cue cannot make an earlier animation shorter.
If the animations before a cue are too long, the picture is behind the voice.
`check_sync.py` runs the scene with no frames, and it lists each cue that the scene reaches late:

```text
ok     0.06 s late at   16.89 s, near the cue 'c201'
ok     0.10 s late at   93.98 s, near the cue 'bytime'
59 cues. Worst delay 0.10 s. Picture 115.68 s, voice track 115.69 s.
```

The limit is 0.12 seconds. The first full version had a delay of 2.0 seconds in the lock scene. This check found it.

## Make the video

The tools: Python 3.11 or later, [Manim Community](https://docs.manim.community/en/stable/installation.html) 0.22, and `ffmpeg` with `libass` and `libx264`.
The typefaces: Rozha One, General Sans and JetBrains Mono.

The repository has the cue times and the final video. It does not have the sound files of the voice.
Thus there are two procedures. Do each command in `docs/video`.

### Change the picture

No key is necessary for this procedure.

1. Get the voice track from the published video.

   ```bash
   ffmpeg -i ../assets/video/onda-how-it-works.mp4 -vn -c:a copy narration.m4a
   ```

2. Change `scene.py`. Then make a draft of one chapter. The names are `hook`, `contract`, `lock`, `layers`, `home` and `close`.

   ```bash
   ONDA_ACTS=lock manim -ql --fps 15 scene.py OndaExplainer
   ```

3. Do the check.

   ```bash
   python3 check_sync.py
   ```

4. Make the full picture.

   ```bash
   manim -qh --fps 60 scene.py OndaExplainer
   ```

5. Join the picture, the voice and the subtitles.

   ```bash
   python3 build.py media/videos/scene/1080p60/OndaExplainer.mp4
   ```

6. Make the poster, and copy it to the assets.

   ```bash
   manim -qh -s scene.py Poster
   ```

   ```bash
   cp media/images/scene/Poster_ManimCE_v0.22.1.png ../assets/video/poster.png
   ```

### Change the words

A key of the voice service is necessary for this procedure.

1. Change `narration.py`. Put a cue mark before each word that starts an animation.
2. Make the voice track. The script calls the service only for a chapter that has new text or no sound file.

   ```bash
   ELEVENLABS_API_KEY=your-key python3 voice.py
   ```

3. Do steps 2 to 6 of the first procedure.

Do not put the key in a file of the repository.

## What the video makes simple

- `ORDER BY time, type, key` is short for `ORDER BY activity_at DESC, activity_type DESC, source_key DESC`.
- The green gate in each branch is the set of filters of that branch. [Home feed](../HOME_FEED.md#why-the-filters-are-in-the-branches) has the full list.
- Event `847` and source ID `2291877` are examples. The figures in [Database](../DATABASE.md#the-three-layers) use the same example.
- The phone screens are drawings. [Product](../PRODUCT.md#the-screens) has pictures of the real screens.
- The lock scene shows two requests of one person. Requests of different persons do not wait for each other.

## Limits

- The voice is synthetic.
- The script sends a fixed seed, but the voice service does not promise the same take for the same text. A new take changes the cue times, and the picture follows.
- The subtitles are part of the picture, because the GitHub player has no subtitle control. A person cannot remove them.
