# Setup and backend recovery

Use this reference when prerequisites are missing or authorized transcription needs setup. Resolve `SKILL_DIR` from the parent `SKILL.md`; do not assume a harness environment variable or install layout.

## Dependencies

`setup.py --json` checks `ffmpeg`, `ffprobe` and `yt-dlp` without installation or configuration writes. `can_proceed`, not legacy labels such as `needs_key`, determines readiness. `setup.py --check` is silent with exit `0` when binaries exist, or exits `2` when they are missing. For older installations returning `3` or `4`, inspect `missing_binaries`; an optional key is not required.

Check existing tools and isolated runtimes first. Perform and verify a task-local dependency install when covered by the current request and environment. A system-wide install or privilege change outside that authorization requires approval; do not repeat an applicable approval. If no authorized installation is possible, use available captions or supplied media/text and name only the remaining blocker.

Run the installer only when its environment changes are needed and authorized:

```bash
python3 "${SKILL_DIR}/scripts/setup.py"
```

The installer can run Homebrew on macOS; on Linux/Windows it prints commands for the agent to carry out when authorized. It creates an absent `~/.config/watch/.env` at `0600` with blank key placeholders and records `SETUP_COMPLETE` once dependencies are ready. Do not treat the script's suggestion to run setup as authorization to install or upload audio.

## Optional Whisper

Native captions and local frames require no API key. For authorized ASR, the user configures credentials privately; never request, echo or write a key. The pipeline reads `~/.config/watch/.env` and can also read environment variables or a working-directory `.env`. Presence of a key does not authorize this source's upload.

Without `--no-whisper`, missing captions or local input can cause extracted mono 16 kHz audio to be uploaded to the selected provider:

- Groq: `whisper-large-v3`, endpoint `api.groq.com/openai/v1/audio/transcriptions`; selected by default when both keys exist.
- OpenAI: `whisper-1`, endpoint `api.openai.com/v1/audio/transcriptions`; select explicitly with `--whisper openai` when authorized.

The video itself is not uploaded, and each provider receives only its own key. A backend change also needs authorization for that audio transfer; do not retry private/local audio with another provider merely because a key is available. For failed/partial transcription, use [transcript artifacts](transcripts.md).
