#!/usr/bin/env python3
"""Defect inventory for the edit plan. Run BEFORE writing the plan.

Usage:
    python3 plan_assist.py <name>.words.json

Scans the word-level transcript and lists every mechanical defect candidate:
filler words, long silences, stretched words, and repeated-take candidates,
each with timestamps. The edit plan must mention every line printed here,
either as a cut or as a keep with a reason. Nothing on this list may be
silently ignored - that is what keeps plan quality consistent no matter which
model is doing the reading.
"""

import json
import re
import sys
from pathlib import Path

FILLER = re.compile(r"^(um+|uh+|uhm+|ah+|ahm+|er+|erm+|hm+|hmm+|ugh+)[,.!?]?$",
                    re.IGNORECASE)
GAP_SEC = 1.0          # silences longer than this get listed
STRETCH_SEC = 0.8      # single words longer than this are suspects
REPEAT_WINDOW = 30.0   # a 4-word phrase recurring within this window = retake candidate


def hms(t: float) -> str:
    m, s = divmod(int(t), 60)
    return f"{m}:{s:02d}.{int((t - int(t)) * 10)}"


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: plan_assist.py <name>.words.json", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1]).expanduser()
    words = json.loads(path.read_text(encoding="utf-8"))["words"]
    if not words:
        print("no words in transcript")
        return

    findings = []

    for w in words:
        token = w["w"].strip()
        if FILLER.match(token):
            findings.append((w["s"], f"FILLER    {hms(w['s'])}  {token!r}"))
        if (w["e"] - w["s"]) > STRETCH_SEC:
            findings.append((w["s"], f"STRETCHED {hms(w['s'])}  {token!r} "
                                     f"held {w['e'] - w['s']:.1f}s (possible stammer or dead air)"))

    for a, b in zip(words, words[1:]):
        gap = b["s"] - a["e"]
        if gap > GAP_SEC:
            findings.append((a["e"], f"SILENCE   {hms(a['e'])}  {gap:.1f}s gap "
                                     f"after {a['w']!r}, before {b['w']!r}"))

    norm = [re.sub(r"[^a-z0-9]", "", w["w"].lower()) for w in words]
    seen = {}
    reported = set()
    for i in range(len(norm) - 4):
        gram = tuple(norm[i:i + 4])
        if "" in gram:
            continue
        t = words[i]["s"]
        if gram in seen and (t - seen[gram]) < REPEAT_WINDOW and gram not in reported:
            phrase = " ".join(w["w"] for w in words[i:i + 4])
            findings.append((seen[gram], f"REPEAT    {hms(seen[gram])} and {hms(t)}  "
                                         f"{phrase!r} said twice (retake candidate: "
                                         f"keep ONE, honor any spoken instruction)"))
            reported.add(gram)
        seen[gram] = t

    findings.sort()
    print(f"Defect inventory: {len(findings)} items. The edit plan must "
          f"disposition EVERY line (cut it, or keep it with a reason).\n")
    for _, line in findings:
        print(line)
    if not findings:
        print("(clean take - no mechanical defects found)")


if __name__ == "__main__":
    main()
