#!/usr/bin/env python3
"""Transcribe a recording with edit-safe word timestamps. Free and local.

Usage:
    python transcribe.py <video-or-audio-file> [--out DIR] [--model small] [--language auto]

Writes into --out (default: the folder the media file is in):
    <name>.words.json   word-level timestamps (the edit plan is built from this)
    <name>.stable.json  the full stable-ts result (kept for re-alignment later)
    <name>.srt          captions, ready to import into DaVinci Resolve
    <name>.txt          the plain transcript, for reading

Uses stable-ts on top of faster-whisper: same free local models, but the word
timestamps are stabilized against the actual audio (silence-aware, minimum word
durations), which is what makes automated cuts safe. No accounts, no API keys,
no per-minute fees.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MIN_WORD_DUR = 0.12  # words shorter than this get stretched/flagged by stable-ts

# Pythons installed from python.org on macOS ship without SSL certificates wired
# up, and the first model download then dies with CERTIFICATE_VERIFY_FAILED.
# certifi is always present in this venv; point the SSL machinery at it.
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass


def fail(msg: str) -> None:
    print(f"\nPROBLEM: {msg}", file=sys.stderr)
    sys.exit(1)


def extract_audio(media: Path, wav: Path) -> None:
    if shutil.which("ffmpeg") is None:
        fail("ffmpeg is not installed. Run the setup again: it installs ffmpeg for you.")
    cmd = [
        "ffmpeg", "-v", "error", "-y", "-i", str(media),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"ffmpeg could not read this file. It said:\n{result.stderr.strip()}")


def transcribe(model, wav: Path, language):
    """Call stable-ts with the edit-safe settings, degrading gracefully if an
    installed version does not know one of the newer keyword arguments."""
    kwargs = dict(
        language=language,
        vad=True,
        suppress_silence=True,
        min_word_dur=MIN_WORD_DUR,
    )
    while True:
        try:
            return model.transcribe(str(wav), **kwargs)
        except TypeError as exc:
            # Drop the argument this stable-ts version does not know and retry.
            dropped = next((k for k in list(kwargs) if k in str(exc)), None)
            if dropped is None:
                raise
            kwargs.pop(dropped)
            print(f"  (this stable-ts version has no '{dropped}', continuing without it)",
                  flush=True)
        except Exception as exc:  # noqa: BLE001
            # The VAD refinement downloads a small model on first use; on a
            # machine with broken SSL certificates that download fails AFTER
            # the whole transcription ran. Losing an hour of work to a
            # post-processing download is not acceptable: retry without VAD.
            if kwargs.get("vad") and any(m in str(exc) for m in
                                         ("CERTIFICATE", "SSL", "urlopen", "certificate")):
                kwargs["vad"] = False
                print("  (could not download the VAD model — certificate problem; "
                      "continuing without VAD refinement)", flush=True)
                continue
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Local edit-safe transcription")
    parser.add_argument("media", help="path to the recording")
    parser.add_argument("--out", default=None, help="output folder (default: next to the media)")
    parser.add_argument("--model", default="small",
                        help="model size: small (default, fast) / medium / large-v3 (best)")
    parser.add_argument("--language", default="auto", help="e.g. en, pt, pl (default: auto-detect)")
    args = parser.parse_args()

    media = Path(args.media).expanduser()
    if not media.exists():
        fail(f"file not found: {media}")

    out_dir = Path(args.out).expanduser() if args.out else media.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = media.stem

    try:
        import stable_whisper
    except ImportError:
        fail("stable-ts is not installed in this environment. "
             "Run the setup again (scripts/setup.py) and retry.")

    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.wav"
        print("Extracting audio...", flush=True)
        extract_audio(media, wav)

        print(f"Loading model '{args.model}' (first run downloads it)...", flush=True)
        model = stable_whisper.load_faster_whisper(
            args.model, device="cpu", compute_type="int8"
        )

        language = None if args.language == "auto" else args.language
        print("Transcribing... expect roughly a third of the recording's length "
              "on a typical machine (an hour of footage: 15 to 25 minutes).", flush=True)
        result = transcribe(model, wav, language)

    words = []
    segments = []
    text_parts = []
    for seg in result.segments:
        segments.append({"start": round(seg.start, 3), "end": round(seg.end, 3),
                         "text": seg.text.strip()})
        text_parts.append(seg.text.strip())
        for w in seg.words:
            words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})

    language_out = getattr(result, "language", None) or (language or "auto")
    payload = {
        "file": str(media),
        "language": language_out,
        "engine": "stable-ts + faster-whisper",
        "model": args.model,
        "min_word_dur": MIN_WORD_DUR,
        "words": words,
        "segments": segments,
    }

    json_path = out_dir / f"{stem}.words.json"
    stable_path = out_dir / f"{stem}.stable.json"
    srt_path = out_dir / f"{stem}.srt"
    txt_path = out_dir / f"{stem}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    result.save_as_json(str(stable_path))
    result.to_srt_vtt(str(srt_path), word_level=False, segment_level=True)
    txt_path.write_text("\n".join(text_parts), encoding="utf-8")

    print(f"\nDone. Language: {language_out}. {len(words)} words across "
          f"{len(segments)} segments.")
    for p in (json_path, stable_path, srt_path, txt_path):
        print(f"  {p}")


if __name__ == "__main__":
    main()
