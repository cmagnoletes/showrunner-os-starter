---
name: assembly-line-fast-track
description: The Fast Tracked Assembly Line. Turns a raw talking-head recording into a trimmed, captioned, rendered cut in DaVinci Resolve (free edition), with the owner approving the edit plan before any cut and reviewing the timeline before render. Use when the owner says "edit my video", "run the assembly line", "fast track this recording", "rough cut", or brings raw footage from a recording session. Free stack end to end; requires one-time setup (scripts/setup.py).
---

# The Fast Tracked Assembly Line (starter)

Editing eats days. This method gives the mechanical part of it to the machine: the
transcript-based rough cut, the silence trims, the captions file, the render. The part
that makes the video worth watching stays with the owner: what to keep, what to cut,
how it feels. **The machine has no taste. The owner does.** That is why this pipeline
has two human gates that are never skipped.

The scripts do the deterministic work; you (Claude) do the reading, the plan, and the
conversation. Never cut a single frame that is not in an approved plan.

## The two gates (never skip, never rush)

- **Gate 1 — the plan.** The owner approves the written edit plan before anything is cut.
- **Gate 2 — the timeline.** The owner scrubs the assembled cut in Resolve and asks for
  changes before anything is rendered.

## Session ritual (owner does this at the start of every editing session)

1. Open DaVinci Resolve.
2. Open the project (or create one for this video).
3. Menu bar: **Workspace > Scripts > resolve_bridge**. This starts the connection and
   must be redone every time Resolve is reopened.

## The protocol

### 0. Health check

```
python3 .claude/skills/assembly-line-fast-track/scripts/doctor.py
```

All PASS: continue. Any FAIL: follow the fix lines top to bottom. If setup was never
run, run `python3 .claude/skills/assembly-line-fast-track/scripts/setup.py`, have the
owner do any manual step it names (installing DaVinci Resolve is one), then doctor
again. No restart is needed: the pipeline's scripts talk to Resolve directly through
the bridge — nothing gets registered into Claude Code or Codex. Windows: every
`python3` in this skill is `python`, and the venv paths use `Scripts\python.exe`.
Never assume a tool exists — doctor is the source of truth, and setup is safe to
rerun after every fix.

### 1. Locate the footage

Ask which video this session edits. The raw recording stays wherever it lives (never
copy it into this repo). The video's folder here (`videos/001/`, `002/`...) receives
every pipeline file. Confirm both paths with the owner.

**Multiple raw files for one video** (the camera was stopped between attempts —
common with phones): stitch them into ONE working file first, then run the whole
pipeline on that file. Confirm the order with the owner (usually filename or
recording-time order), then:

```
printf "file '%s'\n" /path/one.mov /path/two.mov > /tmp/join.txt
ffmpeg -f concat -safe 0 -i /tmp/join.txt -c copy "<same-folder>/joined-take.mov"
```

Stream-copy works when the clips came from the same camera with the same settings.
If ffmpeg complains or the clips differ (mixed devices, orientations, frame rates),
re-encode instead: replace `-c copy` with `-c:v libx264 -preset fast -c:a aac -r 60`.
The joined file lives beside the sources, never in the repo; list the source files
in the edit plan and the edit log. Everything downstream (transcript, plan, cuts,
timeline) then works on the joined file exactly as with a single take — including
retakes that span clip boundaries. Screen recordings plus camera as separate angles
are NOT this: that's multi-track editing, out of the fast track's scope.

### 2. Transcribe (deterministic)

```
~/.showrunner-os/venv/bin/python .claude/skills/assembly-line-fast-track/scripts/transcribe.py \
  "<path-to-recording>" --out videos/00X/
```

(Windows: `%USERPROFILE%\.showrunner-os\venv\Scripts\python.exe`.) Default model is
`small`. On a strong machine, or when the owner wants maximum accuracy, add
`--model large-v3` (slower, much bigger download). Non-English footage: add
`--language xx` if auto-detect gets it wrong. Set the expectation out loud: this takes
roughly a third of the recording's length (an hour of footage: 15 to 25 minutes), so
for a batch, run them back to back while the owner does something else. Outputs:
`<name>.words.json` (word timing), `<name>.srt` (timed to the RAW file — working
reference only; the publishable captions come from step 7), `<name>.txt` (readable
transcript).

### 3. Build the edit plan (your judgment, in writing)

FIRST, run the defect inventory - it enumerates every filler word, long silence,
stretched word, and repeated-take candidate with timestamps:

```
~/.showrunner-os/venv/bin/python .claude/skills/assembly-line-fast-track/scripts/plan_assist.py \
  videos/00X/<name>.words.json
```

**Every line of that inventory must appear in the edit plan, dispositioned:
cut, or kept with a stated reason.** Never skip an item silently - a missed
"um" the owner has to point out three times is a failed plan. When the owner
later says "remove all of those", the inventory IS the complete list; re-check
every FILLER line against the ranges, not just the first one you find.

Then read the transcript (`.txt` for flow, `.words.json` for timing) and decide
what stays.

**The cut rules:**
- **Repeated takes:** keep the LAST good take of a repeated line unless the owner has
  said otherwise. Week 3 recording style leaves every retake in; the last one is
  almost always the keeper.
- **Filler and false starts:** cut obvious "um"/"uh" islands, abandoned sentence
  starts, long dead air, and any "start of take" or "end of take" chatter ("okay,
  here we go", "cut, how do I stop this") - meta-commentary about the recording is
  never content. Leave natural breaths and thinking pauses that carry the owner's
  rhythm; this is a person, not a supercut. Mid-sentence fillers default to KEEP
  (cutting them risks choppy joins), but each one must be listed at Gate 1 so the
  owner decides once, for all of them.
- **Stammer suspects:** any word whose timestamps span more than 1 second is a suspect
  (stretched delivery reads as one long token). List every one in the plan for the
  owner to confirm; do not silently cut them.
- **When unsure, keep it and flag it.** A kept flub costs seconds at Gate 2; a wrongly
  cut moment costs a reshoot.
- Mark every range that ends a sentence with `"tail": "sentence"` so it gets breathing
  room in the next step.

Write two files into the video folder:
- `edit-plan.md` — the human-readable plan, from `videos/edit-plan-template.md`.
- `keep-ranges.json` — the same decisions as machine data:
  `{"ranges": [{"start": s, "end": s, "label": "...", "tail": "sentence",
  "last_word": "..."}]}` with times from `.words.json` word boundaries.

### Gate 1 — show the plan, wait

Present the summary (kept vs. removed minutes, every removal with its reason, the
stammer-suspect list) and wait for the owner. They answer in plain language ("keep the
second take of the intro", "also drop the tangent about the dog"); update both files
and show the diff until they approve. **Nothing is cut before the word "approved" (or
its plain equivalent).**

### 4. Make the cuts safe (deterministic)

```
~/.showrunner-os/venv/bin/python .claude/skills/assembly-line-fast-track/scripts/cutpoints.py \
  "<path-to-recording>" videos/00X/keep-ranges.json
```

Word timestamps are anchors, not cut points. This adds air before first words and
after last words (sentence tails breathe longer), slides every boundary to the
quietest nearby moment, and flags anything that could still sound rough. Read the
flags it prints; tell the owner how many boundaries are flagged. Output:
`videos/00X/cutlist.json`.

### 5. Assemble in Resolve (deterministic)

```
python3 .claude/skills/assembly-line-fast-track/scripts/build_timeline.py videos/00X/cutlist.json \
  --timeline "<video name> cut"
```

Builds a fresh timeline with every kept segment in order. Flagged boundaries appear as
**red REVIEW markers** on the timeline itself. Reruns never touch an existing
timeline: they create ` v2`, ` v3`... — the owner's manual timeline edits are never
overwritten.

### Gate 2 — the owner scrubs the cut

The preview is Resolve itself. The owner plays the timeline, jumps between red
markers, and asks for fixes in plain language. For each fix: find the moment in
`.words.json`, adjust `keep-ranges.json`, rerun steps 4 and 5 (new timeline version).
Small one-off fixes the owner prefers to do by hand in Resolve are welcome; note them
in the log and leave that timeline alone afterward.

### 6. Render (deterministic)

```
python3 .claude/skills/assembly-line-fast-track/scripts/render.py --name <video-name>
```

Output lands in `~/Movies/ShowrunnerOS/` (the bridge only writes inside Movies).
Manual fallback if the owner prefers buttons: Deliver page > YouTube preset > Add to
Render Queue > Render All.

### 7. Quality check + captions (one pass, two jobs)

Re-transcribe the rendered file (step 2's command, `--out videos/00X/final/`).

- **QA:** compare its text against the approved plan. Look for: duplicated phrases at
  joins, words cut mid-delivery, sentences that lost their ending. Report what you
  find; fix through Gate 2's loop if needed.
- **Captions:** the `.srt` from THIS pass is timed to the final cut — this is the
  captions file that ships with the video. (The step-2 SRT is timed to the raw
  recording and drifts out of sync the moment anything is cut; never publish it.)
  Upload video + this SRT together. An owner who wants styled burned-in captions
  instead: in Resolve, File > Import > Subtitle with this SRT (it matches the cut
  timeline's timing), drag it onto the timeline, style it in the Inspector, render
  again. Free-edition note: Resolve's built-in auto-caption button is Studio-only;
  nobody needs it.

### 8. Log and commit

Write `videos/00X/edit-log.md`: what was cut and why, stage timings, flags raised and
how they were resolved, render path. Before committing, check `git config user.name`;
on a fresh machine it is unset - ask the owner for the name and email they use on
GitHub and set both with `git config user.name/user.email` so their commits carry
their identity. Then commit the video folder (never the media files).

## When something breaks

| Symptom | Likely cause and fix |
|---|---|
| The cut plays in slow motion | The project's playback frame rate does not match the footage (API-created projects default to 24 and the API cannot change it). In Resolve: Project Settings (gear icon, bottom right) > Master Settings > Playback frame rate > match the footage (e.g. 60) > Save. One time per project. The render is unaffected. |
| doctor: "bridge is running" FAILS | The session ritual was skipped. Resolve must be open, with a project open, and Workspace > Scripts > resolve_bridge clicked this session. |
| resolve_bridge missing from the Scripts menu | Restart Resolve (it scans scripts at launch). Still missing on macOS: run setup again, it repairs the Python discovery, then restart Resolve. |
| build_timeline cannot reach Resolve | Same ritual; also confirm doctor passes. |
| Bridge suddenly times out mid-session | An open dialog window in Resolve (Project Settings, a render dialog, any popup) blocks its entire scripting API. Close the dialog and rerun. |
| Import fails on a recording | Ask the owner to drop the file into Resolve by hand once; if Resolve cannot play it, transcode first: `ffmpeg -i in.ext -c:v libx264 -c:a aac out.mp4`. |
| Render output missing | Open the Deliver page; the job's error is shown there. Free edition cannot write some pro codecs; the default preset works. |
| Windows: bridge stops answering between sessions | A stale `fuscript.exe` may hold the port; end it in Task Manager or reboot. |
| Anything loops twice without progress | Stop and tell the owner what you tried, what failed, and the exact error. Never keep retrying the same command. |

## Hard rules

- Two gates, always, in order. No "quick pass without approval".
- Cuts come only from `cutlist.json` (never raw word boundaries, never eyeballed).
- The machine never claims the video is "done" — it delivers a cut for the owner's
  taste pass.
- Media files never enter this repo; plans, transcripts, and logs always do (commit
  after the session).
- This is the fast track. Motion graphics, sound design, and the fully agentic
  pipeline are the full Assembly Line and live in the paid tiers; do not improvise
  them here.
