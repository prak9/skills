# CLI, frame selection and follow-ups

Use only the options needed for the requested evidence. Resolve `SKILL_DIR` from the parent `SKILL.md`; pass the source URL/path as one normally quoted argument, separate from the user's question.

## Options

| Option | Effect |
|---|---|
| `--detail transcript` | No automatic frames; skips video download when captions exist, otherwise downloads audio for an authorized ASR fallback |
| `--detail efficient` | Keyframes, cap 50; fewer than four keyframes trigger uniform fallback |
| `--detail balanced` | Scene-aware selection with uniform fallback for effectively static video, cap 100 |
| `--detail token-burner` | Scene-aware, uncapped; warning above 250 frames |
| `--start T` / `--end T` | Focus acquisition and displayed transcript; accepts `SS`, `MM:SS`, `HH:MM:SS` |
| `--timestamps T1,T2,…` | Pin exact absolute cue times; with transcript detail, only these frames are extracted |
| `--max-frames N` | Override the detail cap |
| `--resolution W` | Frame width, default 512; raise only when text/visual detail requires it; height remains capped at 1998 |
| `--fps F` | Override automatic sampling, clamped to 2 fps |
| `--out-dir DIR` | Output location; otherwise a fresh temporary directory |
| `--subtitle-lang CODE` | Prefer a track such as `zh` or `en`; verify actual language and translation provenance |
| `--no-print-transcript` | Suppress console text, not saved transcript segments |
| `--no-whisper` | Disable audio upload/ASR fallback |
| `--whisper groq\|openai` | Select an authorized backend |
| `--no-dedup` | Keep near-duplicate frames, for example when subtle motion matters |

`WATCH_DETAIL` in `~/.config/watch/.env` sets a persistent default; absent that, the default is `balanced`. Do not change it for a one-off task.

Automatic full-video budgets grow with duration up to the detail cap; focused ranges sample more densely, still at most 2 fps. Cue frames count against the cap first and cannot be evicted by uniform selection; cues outside a requested range are dropped and reported. All times remain absolute source times, never offsets from the focus start.

Frame count and resolution dominate image-processing cost. For long videos, use the transcript to choose relevant ranges or cues instead of treating a sparse full-video pass as comprehensive visual coverage.

## Additional frames after reading a transcript

Scene/keyframe selection can miss low-motion cues such as “look here” at a chart. Choose relevant cue times from the transcript, not every occurrence of a phrase. Keep the acquired `transcript.json`, raw VTT, source URL, language and completeness information; do not retranscribe to obtain pictures.

**If a full local video of the same source already exists**, reuse it for a frame-only pass into a separate directory:

```bash
python3 "${SKILL_DIR}/scripts/watch.py" "<verified-local-video>" \
  --detail transcript --timestamps 4:32,7:10 --no-whisper --out-dir "<new-frame-dir>"
```

Local input does not auto-import previous captions, so this pass may report `Transcript: none available`. That is not loss of the earlier spoken evidence: combine these frames with the retained original transcript and its provenance. Do not overwrite the original transcript directory with the frame pass.

**If only captions or audio were acquired**, there is no reusable video for frames. Use the original URL (or a user-supplied authorized full video) instead:

```bash
python3 "${SKILL_DIR}/scripts/watch.py" "<original-video-URL>" \
  --detail transcript --timestamps 4:32,7:10 --no-whisper --out-dir "<new-frame-dir>"
```

`--timestamps` makes this run acquire full video rather than audio-only media. The URL path also checks captions; this does not authorize a new ASR call or invalidate the existing transcript. Retain the original source association when later reusing the downloaded video. If acquisition is blocked, keep the transcript and name the missing visual evidence rather than inventing a local video path.

For a continuous range, use the applicable source above with `--detail balanced --start 4:25 --end 4:40 --no-whisper` and a separate output directory. Inspect every returned frame, align it with the original transcript's absolute times, and report sampling or resolution limits.
