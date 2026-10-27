# The Selection: notes for Claude Code

A static website (no framework, no build step besides the data script) showing an AI negotiation experiment. Hosted on GitHub Pages.

## Structure
- `index.html` (CN Mail): the only page. Self-contained: its CSS and JS are inline, and it loads `data/sessions.js`, which sets `window.SELECTION_DATA`.
- `data/raw/game_XX_result.json`: raw experiment output. Never edit by hand.
- `tools/build_data.py`: builds `data/sessions.js` from the raw files. Relabels countries → AI names and candidates → roles. Reads STATES and INJECTIONS from `experiment/the_selection_v2.py`.
- `experiment/`: the Colab scripts that produce the raw results.

## Commands
- Rebuild data: `python tools/build_data.py`
- Preview locally: open the HTML file directly, or `python -m http.server` and go to http://localhost:8000

## Rules
- Readers must only meet two kinds of characters: AIs (voters) and candidate roles. Never show the fictional country names or candidate names in the UI.
- Keep the "Fictional · not affiliated with any real organisation" notice on the page.
- Do not imitate a real product's branding (no real mail-app logos, names or exact colour schemes).
- Never commit API keys. The experiment reads `OPENROUTER_API_KEY` from Colab Secrets or the environment.
- Every colour is a CSS variable with light and dark values. Pages must work at 400px wide.
- The user prefers short, simple, step-by-step explanations.

## Data shape (one session in `window.SELECTION_DATA`)
`id`, `version`, `voters` (AI names), `veto`, `pub` [round, from, text, reply_to?], `ann` [round, text] (secretariat notices, v2),
`pm` [round, from, to, text], `notes` {"talk1|Opus": text}, `polls` [{n, ballots{ai:{role:E|D|N}}}], `out` [[after_poll, role]],
`win` (role or "DEADLOCK"), `tie`, `expl` {ai: text}, `fails` [[phase, n, ai, reason]], `role`, `public`, `secret` {ai: text},
`inj` [[round, to, from, text]], `coal` [[round, ai, type, role, coalition_id]] (v2).
