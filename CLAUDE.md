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
- `channel/` — standing strategy derived from the baseline (pillars, the concept shortlist, the
  swipe file) plus standing references like `home-studio.md`, the recording setup.
- `methods/` — the prompts you run and the doctrine files they read, grouped by Loop beat
  (signal / package / publish / scale). `package/the-hold.md` is the retention doctrine; every
  beat sheet derives from it. `package/the-marquee.md` is the packaging doctrine; every
  thumbnail is judged by it.
- `.claude/skills/` — working tools Claude Code runs itself. Viewer Soul, the Fast
  Tracked Assembly Line (the editing pipeline), and the Marquee (thumbnail words,
  grader, feed mockup) live here.
- `videos/` — one folder per video (`001/`, `002/`…), each holding that video's beat sheet,
  edit plan, edit log, and marquee (packaging record); reads come in a later session.
  `videos/beat-sheet-template.md` and `videos/edit-plan-template.md` are the templates.
  Raw recordings and renders stay OUTSIDE this repo; only plans, transcripts, and logs
  are committed.

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
