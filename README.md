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

No Git? Click **Code → Download ZIP**, unzip it, and open that folder. (Or skip the harness
entirely — see "No harness?" at the bottom.)

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

(Or just ask Claude Code / Codex to commit and push for you — both can run Git.)

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

Next session we stand up the rest of the system on your harness: the config that makes this
file the auto-loaded root context (a `CLAUDE.md` or `AGENTS.md` that tells every agent "read
`brand-baseline.md` first"), then the first component that consumes it — your content
pillars. You're not cold-starting a repo next week. You're activating the one you already have.

---

Part of **The Guild** · [carlosmagno.me/guild](https://carlosmagno.me/guild)
