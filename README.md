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
| `brand-baseline-prompt.md` | The interview that produces your brand foundation. Run this. |
| `brand-baseline.md` | Where your finished foundation lives. Empty until you fill it. |

## How to use it

**If you're comfortable with GitHub** — click **"Use this template"** (green button, top
right) to make your own copy. **Make it private** — this file will hold your ideal
customer, your positioning, and real customer quotes. Then point Claude Code at your
folder and run the prompt.

**If you're not** — just open `brand-baseline-prompt.md`, copy the prompt, and run it in
claude.ai with your assets attached. Save the result wherever you keep your work. We'll
formalize the setup together next session.

## The workflow

1. Gather your inventory — the things the prompt asks for (website, docs, call recordings,
   anything in your voice). Assets first.
2. Run `brand-baseline-prompt.md`. It mines what exists, then interviews you only about
   what's missing.
3. Paste the finished baseline into `brand-baseline.md`.
4. Commit it.

From then on you **augment** this file — never regenerate it. It's a foundation, not a draft.

## What happens next

Next session we stand up the rest of the system on a harness (Claude Code or Codex): the
configuration that makes this file the root context every future component reads, then the
first component that consumes it — your content pillars. You're not cold-starting a repo
next week. You're activating the one you already have.

---

Part of **The Guild** · [carlosmagno.me/guild](https://carlosmagno.me/guild)
