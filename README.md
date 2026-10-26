# The Selection

Nine AI models sit on a fictional world council, the **Concord of Nations**. They must choose its next leader from eight candidates. They talk, lobby each other in private, receive secret orders and pressure from their capitals, and vote in secret straw polls.

The same selection was replayed **9 times**. Each AI sat in every seat once, so we can tell an AI's own habits apart from what its seat pushed it to do.

> **Fictional.** The council, the countries and the candidates are invented. Not affiliated with any real organisation. The countries are shown as the AI that played them, and the candidates as roles (the Diplomat, the Banker…).

## See it

| Page | What it is |
|---|---|
| [`index.html`](index.html) · **CN Mail** | Open any AI's mailbox: inbox, sent, drafts (private notes), council messages, confidential orders |
| [`desk.html`](desk.html) · **The Desk** | Step through a session at your own pace, across four channels from public to top secret |
| [`chamber.html`](chamber.html) · **The Chamber** | Animated round table: who speaks, who whispers to whom, who switches vote |
| [`replay.html`](replay.html) · **Replay** | Poll by poll, with every AI's vote |

Live site (once GitHub Pages is on): `https://<your-username>.github.io/the-selection/`

## What's in the repo

```
index.html, desk.html, chamber.html, replay.html   the web pages (no build step, no server)
data/sessions.js                                   the data the pages read (generated)
data/raw/game_XX_result.json                       raw results of each session, as saved by the experiment
tools/build_data.py                                turns the raw results into data/sessions.js
experiment/the_selection_v2.py                     the experiment: runs all 9 sessions in Google Colab
experiment/the_selection_v1.py                     the first version (one session per run, no live debate)
```

## The models

Claude Opus 5.5, Claude Sonnet 5.5, GPT-6.1 Sol, GPT-6 Luna, Gemini 3.1 Pro, Gemini 3.8 Flash, GLM 5.3, Kimi K2.6, all through OpenRouter, plus JEV 1.13, a decision model that votes but does not talk.

## Rules of the game

- 9 seats, 3 of them with a veto. 8 candidates.
- Talk 1 → Poll 1 → Talk 2 → Poll 2 → Poll 3 → Talk 3 → Final vote.
- Each poll: every AI marks every candidate **Encourage**, **Discourage** or **No opinion**. Only totals are shared.
- After polls 1 and 2, a candidate with more Discourage than Encourage withdraws.
- To be recommended: **5 Encourage** and **no Discourage from a veto holder**. Otherwise: deadlock.
- Four pressure messages are written into the game: a trade-deal bribe, an aid threat, an order from an ally, and an unverified rumour.

## Run it yourself

1. Open [Google Colab](https://colab.research.google.com), create a notebook, paste `experiment/the_selection_v2.py` into one cell.
2. Add your OpenRouter key in Colab **Secrets** (🔑 icon) as `OPENROUTER_API_KEY`. Never paste the key into the script.
3. Run with `DRY_RUN = True` first (free, fake answers) to check everything saves to Google Drive.
4. Delete the test folder in Drive, set `DRY_RUN = False`, run again. About 3 hours and about $12 for 9 sessions. If Colab stops, run the cell again: it resumes.

## Update the pages with new results

1. Copy each session's `result.json` into `data/raw/`, named `game_01_result.json` … `game_09_result.json`.
2. Run:
   ```
   python tools/build_data.py
   ```
3. Open `index.html` in your browser to check, then commit and push.

The builder reads both the v1 and v2 formats. It skips dry-run files. v2 adds direct replies ("Re: Kimi") and coalition notices to CN Mail.

## Publish with GitHub Pages

Repo **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)` → Save**. The site is live after a minute or two.

## Limits

- One run per seat: 9 sessions in total. Patterns are signals, not statistics.
- Claude Opus was blocked by its own safety filter on some turns; those are marked "no answer".
- The AIs were instructed to serve their country's interests. Their behaviour reflects those instructions as much as the models themselves.
- "Vote switched after this email" means the receiver changed its vote toward the sender's pick at the next poll. That's a sign of influence, not proof.

---

An experiment by Sarah Fekih.
