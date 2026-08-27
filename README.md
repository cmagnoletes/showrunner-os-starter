# Showrunner OS — starter

This is the seed of your **Showrunner OS**: one system that runs your YouTube channel,
not a drawer full of disconnected AI prompts.

Most people collect AI like party tricks — a prompt for titles, a prompt for thumbnails,
all separate, none of them aware of the others. That's props. A Showrunner OS is the
opposite: every part reads from the same foundation, so the whole thing gets smarter as
it grows.

You start today with the foundation itself: **the distillation of your brand**, in one file.

---

## What's in here

| File | What it is |
|---|---|
| `brand-baseline-prompt.md` | The interview that produces your brand foundation. You run this. |
| `brand-baseline.md` | Where your finished foundation lives. Empty until you fill it. |
| `CLAUDE.md` | The root config. Claude Code reads it automatically: baseline first, always. |
| `methods/signal/writers-room-prompt.md` | The Writer's Room. Turns your baseline into your Concept Shortlist. |
| `.claude/skills/viewer-soul/` | A working skill: sees YouTube through your viewer's eyes, harvests outliers. |
| `channel/concept-shortlist-template.md` | Where your 4 to 6 video concepts land. |
| `methods/package/the-hold.md` | The retention doctrine. Every beat sheet is built from it. |
| `methods/package/beat-sheet-prompt.md` | The Beat Sheet method. Turns shortlist concepts into recordable outlines, batch-first. |
| `videos/beat-sheet-template.md` | The shape of each video's beat sheet. One folder per video: `videos/001/`, `002/`… |
| `channel/home-studio.md` | The five-minute pre-shoot checklist. The full [Home Studio Guide](https://carlosmagno.me/home-studio-guide.pdf) is a PDF. |

**Session 3 turned the system toward recording.** The Showrunner OS now holds the
retention doctrine as a file (The Hold), the method that applies it to your shortlist
(the Beat Sheet), the per-video folder structure, and your home-studio reference. Same
repo, same foundation, one more part each session.

### How to run Session 3

Have your repo from Sessions 1 and 2? Update it first — open Claude Code inside your
repo folder and tell it:

> Fetch `methods/package/the-hold.md`, `methods/package/beat-sheet-prompt.md`,
> `videos/beat-sheet-template.md`, `videos/README.md`, `channel/home-studio.md`, and the
> updated `CLAUDE.md` from https://github.com/cmagnoletes/showrunner-os-starter and add
> them to this repo, then commit.

Then run the Beat Sheet with one instruction:

> Read `methods/package/beat-sheet-prompt.md` and run it on me.

It shows you your shortlist, you pick your top 2 or 3 concepts, and it builds a beat
sheet for each in one pass: recordable outlines built on The Hold, in your voice, written
to `videos/001/`, `002/`, `003/`. Then set up once — the
[Home Studio Guide](https://carlosmagno.me/home-studio-guide.pdf) covers the whole
setup, and `channel/home-studio.md` keeps the five-minute checklist — and batch-record
them in one session. **Done means footage in the can: 2 or more raw videos, ideally 3.**
Editing is the next session, on purpose; rough is exactly right.

### How to run Session 2

Already have your repo from Session 1? Update it first — open Claude Code inside your
repo folder and tell it:

> Fetch `CLAUDE.md`, `methods/signal/writers-room-prompt.md`, the whole
> `.claude/skills/viewer-soul/` folder (including `scripts/harvest.py`), and the two
> `channel/` templates from https://github.com/cmagnoletes/showrunner-os-starter and add
> them to this repo, then commit.

Then run the Writer's Room with one instruction:

> Read `methods/signal/writers-room-prompt.md` and run it on me.

Budget 60 to 90 minutes the first time. The only extra tool it needs is `yt-dlp`
(free); your Claude will check for it and install it if it is missing.

It reads your `brand-baseline.md`, interviews you on your one viewer and your clusters,
walks you through the free demand checks, runs the `viewer-soul` skill to harvest outliers
into `channel/swipe-file.md`, and writes your finished shortlist to
`channel/concept-shortlist.md`. You approve, edit, and commit. **Done means your shortlist
is committed: 4 to 6 concepts, each with its evidence.** They become beat sheets next
session.

---

## Step 1 — Get your own copy

Click the green **"Use this template"** button at the top of this page → **Create a new
repository** → **set it to Private.** This matters: your baseline will hold your ideal
customer, your positioning, and real customer quotes. Keep it private.

Then bring it down to a folder on your machine:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
```

No Git? Click **Code → Download ZIP**, unzip it, and open that folder; you can ask Claude
Code to "initialize git here and commit everything" later, when you reach Step 4. (Or skip
the harness entirely — see "No harness?" at the bottom.)

This folder is your workspace. Everything your Showrunner OS does happens here.

## Step 2 — Drop your assets in

Create an `inventory/` folder and put anything that already describes you or your customer
into it, so the AI reads your real material instead of making things up. Drop the raw files
in as-is. You do not need to convert anything by hand: it will transcribe your audio and
video, and pull the fonts and colors straight out of your slide decks and PDFs.

- Your website (paste the URL when asked, or save the About / services pages as text)
- ICP or positioning docs, pitch decks, offer descriptions (raw decks and PDFs are fine)
- Sales or customer call recordings or transcripts (raw audio or video is fine)
- Testimonials, reviews, case studies
- A few of your own posts, emails, or video transcripts, so it learns your voice

Whatever you have. Thin is fine, the interview fills the gaps.

## Step 3 — Run it (Claude Code or Codex)

Open the harness **inside this folder** and point it at the prompt. Pick your harness:

### Claude Code

```bash
# install once (Node 18+):
npm install -g @anthropic-ai/claude-code

# from inside your repo folder:
claude
```

Heads-up, first run only: `claude` opens a browser window to log in, and it needs a Claude
account with a paid plan (Claude Pro works) or API billing. Codex is the same idea with a
ChatGPT account.

Then tell it:

> Read `brand-baseline-prompt.md` and run it on me. Use everything in the `inventory/`
> folder and my website as source material, transcribing any audio or video and pulling
> brand tokens from any decks. Mine first, then interview me only on what's missing. Write
> the finished result to `brand-baseline.md`.

### Codex

```bash
# install once (Node 18+):
npm install -g @openai/codex

# from inside your repo folder:
codex
```

Then give it the same instruction:

> Read `brand-baseline-prompt.md` and run it on me. Use everything in the `inventory/`
> folder and my website as source material, transcribing any audio or video and pulling
> brand tokens from any decks. Mine first, then interview me only on what's missing. Write
> the finished result to `brand-baseline.md`.

Either way: it reads the prompt, reads your files, drafts what it can, then interviews you
one question at a time. It takes about 45–60 minutes. Answer honestly; where it proposes
wording, it marks it as proposed until you approve it. Your words win.

## Step 4 — Save it

When the baseline is done, commit it so it's permanent and versioned:

```bash
git add -A
git commit -m "Brand Baseline v1"
git push
```

(Or just ask Claude Code / Codex to commit and push for you — both can run Git. Downloaded
the ZIP instead of cloning? Ask it to "initialize git here, create a private GitHub repo,
and push" — it will walk you through it.)

---

## The one rule that matters: augment, never regenerate

From now on, `brand-baseline.md` is **canonical and living.** When something about your
brand sharpens, you **edit this file in place and commit** — you never regenerate it from
scratch, and you never make a `v2` file. Git keeps every version, so you never lose the
past and you never start over. This is the file every future part of your system reads
first, so it stays the single source of truth.

## No harness? (no problem for today)

You don't need Claude Code or Codex to produce your baseline today. Open
`brand-baseline-prompt.md`, copy the whole prompt, paste it into **claude.ai** (or ChatGPT),
attach your inventory files, and run the interview there. Save the output as
`brand-baseline.md` in a folder you won't lose. We'll formalize the harness setup together
next session — you'll just be moving a file you already have.

## What happens next

Session 4 is the edit: turning the raw takes you just recorded into finished videos, so
bring your footage. Packaging (the thumbnail and title craft) comes right after, on the
runway to publishing. Every session adds one more working part to the same repo: same
foundation, growing machine. You're never cold-starting; you're activating the
Showrunner OS you already have.

---

Part of **The Guild** · [carlosmagno.me/guild](https://carlosmagno.me/guild)
