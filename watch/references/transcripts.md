# Transcript artifacts and recovery

Use this reference to export/replay acquired speech evidence or handle partial ASR. For image-only follow-ups, retain these artifacts and use [usage and frames](usage.md); do not transcribe again just to obtain pixels.

## Acquisition and completeness

Native captions are preferred. The downloader selects one track, preferring manual/source-language captions; an explicit `--subtitle-lang` can select an available machine translation. Verify the actual language and provenance, especially when source language is unknown. `manual` means uploaded, not necessarily human-checked, verbatim or original-language.

Each URL download attempt uses a fresh directory under `download/`, so a failed new request cannot adopt earlier media or subtitles. `transcript.json` retains source metadata, selected/available tracks, raw subtitle path, requested range, parse diagnostics, first/last timestamps and segments. Plain `transcript.txt` and timestamped `transcript.md` preserve all acquired text even with `--no-print-transcript`.

`complete` describes processing of the acquired caption file or source audio chunks, not proof that all speech was captioned or accurately recognized. Invalid cues produce `partial`; caption-free intervals alone do not prove missing speech. Preserve raw VTT for reparsing: old cleaned JSON cannot recover discarded words. Metadata exports exclude signed media URLs and credentials; do not publish a raw downloader response as a substitute.

## Offline export

Re-export a saved artifact without a network request:

```bash
python3 "${SKILL_DIR}/scripts/export_transcript.py" "<saved-transcript.json>" --out-dir "<export-dir>"
```

For original VTT replay, use matching metadata for the same video and the actual track language/type:

```bash
python3 "${SKILL_DIR}/scripts/export_transcript.py" "<captions.vtt>" \
  --info-json "<matching-source-info.json>" --subtitle-lang zh --subtitle-kind manual \
  --out-dir "<export-dir>"
```

The language/type above are examples, not defaults to infer from the filename. Supported types are `manual`, `automatic`, `translated`, `unknown`. Exit `0` means nonempty and complete processing within the recorded scope; exit `4` means partial, absent or unverified processing, with usable artifacts retained. Neither code establishes full-speech coverage, reproduction permission or completed external archival.

## ASR gaps

Use [setup and backend recovery](setup.md) only when an authorized ASR backend is needed. Missing captions, a configured key, or a script's setup hint does not authorize an audio transfer.

Audio exceeding the pipeline's 25 MB upload limit is split into chunks. Failed chunks remain missing intervals in the report and JSON; successful later chunks keep their original source offsets. If every chunk fails or there are no speech segments, report `none`, not an empty “complete” transcript. Focused reports filter displayed segments, while failed intervals refer to the full source; preserve both scopes.

Inspect the actual failure before retrying. A switch from Groq to OpenAI or vice versa is appropriate only when the new provider's transfer is already authorized or newly approved. Retain partial evidence and explain the missing intervals; never silently substitute an incomplete transcript or visually inferred dialogue for requested speech.
