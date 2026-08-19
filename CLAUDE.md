# Showrunner OS — root config

This repo is a **Showrunner OS**: one system that runs your YouTube channel. Every part
reads the same foundation, so the whole thing gets smarter as it grows.

## Read this first, always

Before any task in this repo, read `brand-baseline.md`. It is the foundation. Pillars,
topics, concepts, scripts, titles, and thumbnails are all derived from it. If a request
conflicts with the baseline, follow the baseline and say so.

## The one rule

`brand-baseline.md` is canonical and living. **Augment it, never regenerate it.** When the
brand sharpens, edit it in place and commit. Never create a v2 file. Git keeps every
version, so nothing is ever lost and nothing starts over.

## How this Showrunner OS is organized

- `brand-baseline.md` — the foundation. Read first, always.
- `inventory/` — raw source material (docs, transcripts, recordings). Mine it, never invent over it.
- `channel/` — standing strategy derived from the baseline: pillars, the concept shortlist, the swipe file.
- `methods/` — the prompts you run, one per method, grouped by Loop beat (signal / package / publish / scale).
- `.claude/skills/` — working tools Claude Code runs itself. Viewer Soul lives here.
- `videos/` — one folder per video as you produce (beat sheet, packaging, reads). Arrives in later sessions.

## The operating model (the Loop)

**Signal** (decide what to make, on evidence) → **Package** (worth clicking, worth staying) →
**Publish** (ship, then read the first 48 hours) → **Scale** (double down, kill, or iterate).
Scale feeds Signal. There is no magic formula; there are experiments.

## How to work here

- **Your words win.** When you propose language for the owner, mark it proposed until they approve it.
- **Evidence over instinct.** Topic and concept choices carry their evidence (demand, outliers) with them.
- Each method reads `brand-baseline.md` and the relevant `channel/` files first, then writes its
  output into `channel/` or the current video folder.
- **Commit after each meaningful step.** The git history is the memory.
