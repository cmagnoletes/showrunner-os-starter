#!/usr/bin/env python3
"""Turn an approved keep-list into safe, frame-accurate cut points.

Word timestamps mark WHERE a cut belongs; they are not safe places to cut.
This script applies the safety rules so edits never clip speech:

  1. Handles: every kept range starts a little before the first word and ends
     a little after the last word (sentence endings get extra breathing room).
  2. Energy snap: each boundary slides to the quietest moment nearby (searched
     in the discarded region only), so cuts land in silence, not on syllables.
  3. QC flags: boundaries that could still sound rough get flagged for the
     human review pass instead of being silently accepted.

Usage:
    python cutpoints.py <media-file> <keep-ranges.json> [--out cutlist.json]

keep-ranges.json (written during the edit plan, approved by the human):
    {"ranges": [{"start": 12.34, "end": 45.67, "label": "intro take 2",
                 "tail": "sentence"}, ...]}

Output cutlist.json: frame-accurate segments ready for the Resolve timeline.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

PRE_HANDLE = 0.12          # seconds of air kept before the first word
POST_HANDLE = 0.18         # seconds kept after the last word
POST_HANDLE_SENTENCE = 0.40  # sentence endings breathe (0.3-0.5s rule)
SEARCH_WINDOW = 0.25       # how far a boundary may slide to find silence
FRAME_MS = 10              # RMS analysis frame
MERGE_GAP = 0.05           # ranges closer than this merge into one
HOT_CUT_RATIO = 0.35       # boundary louder than this fraction of speech RMS -> flag


def fail(msg: str) -> None:
    print(f"\nPROBLEM: {msg}", file=sys.stderr)
    sys.exit(1)


def ffprobe_fps(media: Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(media)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0 or "/" not in out.stdout:
        fail(f"could not read the frame rate of {media.name}")
    num, den = out.stdout.strip().split("/")
    return float(num) / float(den)


def load_rms(media: Path) -> tuple[list, float]:
    """Short-time RMS of the mono audio, one value per FRAME_MS."""
    if shutil.which("ffmpeg") is None:
        fail("ffmpeg is not installed. Run the setup again.")
    import numpy as np
    with tempfile.TemporaryDirectory() as tmp:
        wav_path = Path(tmp) / "audio.wav"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(media),
               "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav_path)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            fail(f"ffmpeg could not read this file:\n{res.stderr.strip()}")
        with wave.open(str(wav_path), "rb") as w:
            rate = w.getframerate()
            samples = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    samples = samples.astype(np.float32) / 32768.0
    hop = int(rate * FRAME_MS / 1000)
    n = len(samples) // hop
    rms = np.sqrt((samples[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    return rms, 1000.0 / FRAME_MS  # frames per second of the RMS track


def snap_to_silence(t: float, rms, rms_fps: float, lo: float, hi: float) -> float:
    """Move t to the quietest RMS frame inside [lo, hi]. Returns new time."""
    i_lo = max(0, int(lo * rms_fps))
    i_hi = min(len(rms) - 1, int(hi * rms_fps))
    if i_hi <= i_lo:
        return t
    window = rms[i_lo : i_hi + 1]
    return (i_lo + int(window.argmin())) / rms_fps


PLOSIVES = ("p", "b", "t", "d", "k", "g", "f", "s", "x", "z", "ch", "sh")
MIN_BOUNDARY_PAUSE = 0.15  # a real pause; less than this means the cut is mid-speech


def load_words(keep_path: Path, words_arg):
    """Word timing for boundary checks: --words, or the single *.words.json
    sitting next to the keep-ranges file."""
    if words_arg:
        path = Path(words_arg).expanduser()
        return json.loads(path.read_text(encoding="utf-8")).get("words", [])
    hits = list(keep_path.parent.glob("*.words.json"))
    if len(hits) == 1:
        return json.loads(hits[0].read_text(encoding="utf-8")).get("words", [])
    return []


def mid_speech_flags(start: float, end: float, words) -> list:
    """Flag a range whose raw boundary sits inside continuous speech — the
    signature of an anchoring mistake (e.g. a range that starts four words
    into the sentence). Checked against the transcript, before handles."""
    flags = []
    if not words:
        return flags
    prev = None
    nxt = None
    for w in words:
        if w["e"] <= start + 0.05:
            prev = w
        if nxt is None and w["s"] >= end - 0.05:
            nxt = w
    if prev is not None and (start - prev["e"]) < MIN_BOUNDARY_PAUSE:
        flags.append(f"starts mid-speech (right after {prev['w']!r} — does the "
                     "sentence really begin here?)")
    if nxt is not None and (nxt["s"] - end) < MIN_BOUNDARY_PAUSE:
        flags.append(f"ends mid-speech (runs into {nxt['w']!r} — does the "
                     "sentence really end here?)")
    return flags


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("media")
    parser.add_argument("keep_ranges")
    parser.add_argument("--out", default=None)
    parser.add_argument("--words", default=None,
                        help="the *.words.json transcript (default: auto-found "
                             "next to keep-ranges)")
    args = parser.parse_args()

    media = Path(args.media).expanduser()
    keep_path = Path(args.keep_ranges).expanduser()
    if not media.exists():
        fail(f"file not found: {media}")
    if not keep_path.exists():
        fail(f"file not found: {keep_path}")

    data = json.loads(keep_path.read_text(encoding="utf-8"))
    ranges = data.get("ranges", [])
    if not ranges:
        fail("keep-ranges.json has no ranges — nothing to cut")

    fps = ffprobe_fps(media)
    print(f"Source: {media.name} @ {fps:.3f} fps", flush=True)
    words = load_words(keep_path, args.words)
    if words:
        print(f"Boundary-checking against {len(words)} transcript words.", flush=True)
    print("Analyzing audio energy...", flush=True)
    rms, rms_fps = load_rms(media)
    duration = len(rms) / rms_fps
    speech_level = float(sorted(rms)[int(len(rms) * 0.8)])  # 80th percentile ~ speech

    segments = []
    prev_end = 0.0
    for idx, r in enumerate(ranges):
        start, end = float(r["start"]), float(r["end"])
        if end <= start:
            fail(f"range {idx} ends before it starts: {r}")
        transcript_flags = mid_speech_flags(start, end, words)
        post = POST_HANDLE_SENTENCE if r.get("tail") == "sentence" else POST_HANDLE

        # 1. handles
        start -= PRE_HANDLE
        end += post

        # 2. snap each boundary to silence, searching only the discarded side
        start = snap_to_silence(start, rms, rms_fps,
                                max(prev_end, start - SEARCH_WINDOW), start)
        next_start = float(ranges[idx + 1]["start"]) if idx + 1 < len(ranges) else duration
        end = snap_to_silence(end, rms, rms_fps, end,
                              min(next_start, end + SEARCH_WINDOW))
        start = max(0.0, start)
        end = min(duration, end)

        # 3. QC flags
        flags = list(transcript_flags)
        s_i = min(len(rms) - 1, int(start * rms_fps))
        e_i = min(len(rms) - 1, int(end * rms_fps))
        if rms[s_i] > speech_level * HOT_CUT_RATIO:
            flags.append("hot-in (no silent pocket at start)")
        if rms[e_i] > speech_level * HOT_CUT_RATIO:
            flags.append("hot-out (no silent pocket at end)")
        label = r.get("label", "")
        last_word = str(r.get("last_word", "")).lower().strip(".!?,")
        if last_word.endswith(PLOSIVES):
            flags.append(f"ends on a hard consonant ({last_word!r})")

        segments.append({
            "label": label,
            "startSec": round(start, 3),
            "endSec": round(end, 3),
            "startFrame": int(start * fps),
            "endFrame": int(end * fps),
            "flags": flags,
        })
        prev_end = end

    # 4. merge segments that now touch
    merged = [segments[0]]
    for seg in segments[1:]:
        if seg["startSec"] - merged[-1]["endSec"] <= MERGE_GAP:
            merged[-1]["endSec"] = seg["endSec"]
            merged[-1]["endFrame"] = seg["endFrame"]
            merged[-1]["flags"] = list(dict.fromkeys(merged[-1]["flags"] + seg["flags"]))
            if seg["label"]:
                merged[-1]["label"] = f"{merged[-1]['label']} + {seg['label']}".strip(" +")
        else:
            merged.append(seg)

    kept = sum(s["endSec"] - s["startSec"] for s in merged)
    flagged = [s for s in merged if s["flags"]]
    out = {
        "media": str(media),
        "fps": fps,
        "sourceDuration": round(duration, 3),
        "keptDuration": round(kept, 3),
        "removedDuration": round(duration - kept, 3),
        "segments": merged,
    }
    out_path = Path(args.out).expanduser() if args.out else keep_path.with_name("cutlist.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"\n{len(merged)} segments | kept {kept/60:.1f} min of {duration/60:.1f} min "
          f"| {len(flagged)} flagged for review")
    for s in flagged:
        print(f"  REVIEW {s['label'] or s['startSec']}: {', '.join(s['flags'])}")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
