"""
Build data/sessions.js from the raw game results.

    python tools/build_data.py

Reads every data/raw/game_XX_result.json (v1 or v2 format), and writes
data/sessions.js, which all the web pages load.

What it does to the text, so readers only meet two kinds of characters:
- each country name becomes the name of the AI that played it (Arvel -> Opus)
- each candidate name becomes a role (Selin Harro -> the Diplomat)
The raw files are never changed.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "sessions.js"
EXPERIMENT = ROOT / "experiment" / "the_selection_v2.py"

# Short display names for the models.
MODELS = {
    "anthropic/claude-opus-5.5": "Opus",
    "anthropic/claude-sonnet-5.5": "Sonnet",
    "openai/gpt-6.1-sol": "GPT Sol",
    "openai/gpt-6-luna": "GPT Luna",
    "google/gemini-3.1-pro-preview": "Gemini Pro",
    "google/gemini-3.8-flash": "Gemini Flash",
    "z-ai/glm-5.3-prime": "GLM",
    "moonshotai/kimi-k2.6": "Kimi",
    "typesafe/jev-1.13": "JEV",
}
# Candidate name -> role key used by the pages.
CANDS = {
    "Amara Tessin": "humanitarian", "Matthias Corle": "banker", "Selin Harro": "diplomat",
    "Rhea Montaury": "mayor", "Teva Ranui": "climate", "Owen Drast": "insider",
    "Bastian Oruel": "judge", "Mira Osterand": "scientist",
}
LABEL = {
    "humanitarian": "the Humanitarian", "banker": "the Banker", "diplomat": "the Diplomat",
    "mayor": "the Mayor", "climate": "the Climate Champion", "insider": "the Insider",
    "judge": "the Judge", "scientist": "the Scientist",
}
VETO = ["Arvel", "Varkand", "Halcyra"]
SHORTROLE = {
    "Arvel": "Largest funder", "Varkand": "Rival power", "Halcyra": "Regional power",
    "Calvero": "Southern Arc voice", "Sona": "Hosts 2M displaced", "Kesh": "Small, courted state",
    "Tirra": "Principled voter", "Maru Isles": "Small island state", "Dunmere": "Arvel's ally",
}
SECRETARIAT = "COUNCIL SECRETARIAT"
# Other spellings the AIs used for a country: demonyms, short forms, typos.
# A value can be (country, pattern) where {} is the AI name.
ALIASES = {"Varkandi": "Varkand", "Maru": "Maru Isles", "Calcvero": "Calvero",
           "Sonans": ("Sona", "{}'s people"), "Sonan": "Sona"}


def load_game_setup():
    """Take STATES and INJECTIONS straight from the experiment script, so they never drift."""
    src = EXPERIMENT.read_text()
    try:
        start = src.index("STATES = [")
        end = src.index("# ---------------- 5. ENGINE")
    except ValueError:
        sys.exit(f"Could not find STATES / INJECTIONS in {EXPERIMENT}")
    ns = {}
    exec(src[start:end], ns)
    return ns["STATES"], ns["INJECTIONS"]


def relabel(text, seats):
    """Swap candidate names for roles and country names for AI names."""
    if not text:
        return text
    for full, key in CANDS.items():
        first, last = full.split()
        for pat in (full, last):
            text = re.sub(r"\b" + re.escape(pat) + r"\b", LABEL[key], text, flags=re.I)
        text = re.sub(r"\b" + re.escape(first) + r"\b", LABEL[key], text)
    for state, model in sorted(seats.items(), key=lambda x: -len(x[0])):
        text = re.sub(r"\b" + re.escape(state) + r"\b", model, text)
    for alias, target in ALIASES.items():
        state, fmt = target if isinstance(target, tuple) else (target, "{}")
        if state in seats:
            text = re.sub(r"\b" + re.escape(alias) + r"\b", fmt.format(seats[state]), text)
    # Capital letter at the start of a sentence.
    text = re.sub(r"(^|[.!?:]\s+|\n)the (Humanitarian|Banker|Diplomat|Mayor|Climate|Insider|Judge|Scientist)",
                  lambda m: m.group(1) + "The " + m.group(2), text)
    return text


def winner_key(raw):
    if raw in CANDS:
        return CANDS[raw], []
    if isinstance(raw, str) and raw.startswith("TIE:"):
        names = [n.strip() for n in raw[4:].split("/")]
        return "DEADLOCK", [CANDS.get(n, n) for n in names]
    return "DEADLOCK", []


def pack(g, states, injections):
    seats = {s: MODELS.get(m, m) for s, m in g["seats"].items()}
    S = lambda s: seats.get(s, s)

    fails = []
    for f in g.get("failures", []):
        who = f["who"].split(" (")[0]
        fails.append([f["phase"], str(f["n"]), S(who), "filter" if "content_filter" in f["who"] else "error"])

    notes = {}
    for n in g.get("private_notes", []):
        if not n.get("note"):
            continue
        key = f"{n['phase']}{n['n']}|{S(n['state'])}"
        text = relabel(n["note"], seats)
        notes[key] = notes[key] + "\n\n" + text if key in notes else text

    pub, ann = [], []
    for m in g.get("public_log", []):
        if m.get("system") or m["from"] == SECRETARIAT:
            ann.append([m["round"], relabel(m["text"], seats)])
        else:
            entry = [m["round"], S(m["from"]), relabel(m["text"], seats)]
            if m.get("reply_to"):
                entry.append(S(m["reply_to"]))
            pub.append(entry)

    pm = []
    for m in g.get("private_messages", []):
        to = m.get("to")
        if not to or to == m["from"]:
            continue
        pm.append([m["round"], S(m["from"]), S(to) if to in seats else LABEL.get(CANDS.get(to), to), relabel(m.get("text", ""), seats)])

    polls = [{"n": str(p["n"]),
              "ballots": {S(st): {CANDS[c]: v for c, v in b.items() if c in CANDS} for st, b in p["ballots"].items()}}
             for p in g["polls"]]

    win, tie = winner_key(g["final"]["winner"])
    out = {
        "id": g["game"],
        "version": g.get("version", 1),
        "voters": [S(s) for s in g["seats"]],
        "veto": [S(s) for s in VETO],
        "pub": pub, "ann": ann, "pm": pm, "notes": notes, "polls": polls,
        "out": [[w["after_poll"], CANDS[w["candidate"]]] for w in g["withdrawn"]],
        "win": win, "tie": tie,
        "expl": {S(s): relabel(e, seats) for s, e in g["final"].get("explanations", {}).items() if e},
        "fails": fails,
        "role": {S(s["name"]): re.sub(r"\bArvel\b", S("Arvel"), SHORTROLE[s["name"]]) for s in states},
        "public": {S(s["name"]): relabel(s["public"], seats) for s in states},
        "secret": {S(s["name"]): relabel(s["private"], seats) for s in states},
        "inj": [[x["round"], S(x["to"]), relabel(x["from"], seats), relabel(x["text"], seats)] for x in injections],
    }
    if g.get("coalition_events"):
        out["coal"] = [[e["round"], S(e["state"]), e["type"], CANDS.get(e.get("candidate"), e.get("candidate")),
                        e.get("coalition")] for e in g["coalition_events"]]
    return out


def main():
    states, injections = load_game_setup()
    files = sorted(RAW.glob("game_*_result.json"))
    if not files:
        sys.exit(f"No game_XX_result.json files in {RAW}")
    games = []
    for f in files:
        g = json.loads(f.read_text())
        if g.get("dry_run"):
            print(f"  skipped {f.name}: it is a dry run (fake answers)")
            continue
        games.append(pack(g, states, injections))
        print(f"  {f.name}: v{games[-1]['version']}, winner {g['final']['winner']}")
    games.sort(key=lambda x: x["id"])
    js = "// Generated by tools/build_data.py. Do not edit by hand.\nwindow.SELECTION_DATA = " + \
         json.dumps(games, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(games)} sessions, {len(js) // 1024} KB)")


if __name__ == "__main__":
    main()
