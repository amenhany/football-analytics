import csv
import json
import os
import re
from datetime import datetime

try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("[WARN] rapidfuzz not installed. Run: pip install rapidfuzz")

SEASON         = "2025/2026"
CHECKPOINT_TM  = "scripts/scraper/data/raw/tm_players.csv"
CHECKPOINT_FS  = "scripts/scraper/data/raw/fs_players.json"
OUTPUT_FILE    = "scripts/scraper/data/merged/players.txt"
FUZZY_THRESHOLD = 80

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ---------------------------------------------------------------------------
# Load checkpoints
# ---------------------------------------------------------------------------
def load_tm() -> list:
    if not os.path.exists(CHECKPOINT_TM):
        raise FileNotFoundError(f"Missing {CHECKPOINT_TM} — run scraper.py first.")
    with open(CHECKPOINT_TM, "r", encoding="utf-8") as f:
        players = list(csv.DictReader(f))
    log(f"Loaded {len(players)} TM players from {CHECKPOINT_TM}")
    return players

def load_fs() -> dict:
    if not os.path.exists(CHECKPOINT_FS):
        raise FileNotFoundError(f"Missing {CHECKPOINT_FS} — run scraper.py first.")
    with open(CHECKPOINT_FS, "r", encoding="utf-8") as f:
        data = json.load(f)
    log(f"Loaded {len(data)} FS records from {CHECKPOINT_FS}")
    return data

# ---------------------------------------------------------------------------
# Stats config
# ---------------------------------------------------------------------------
PENALTY_STATS = {
    "Penalties Scored",
    "Penalties Taken",
    "Penalties Missed",
    "Penalty Conversion Rate",
    "Hat-tricks",
    "3 or More Goals",
    "2 or More Goals",
}

NO_PER90_STATS = PENALTY_STATS | {
    "Shot Conversion Rate",
    "Shot Accuracy",
    "Pass Completion Rate",
    "Cross Completion Rate",
    "Dribble Success Rate",
    "Penalty Conversion Rate",
    "Minutes Per Goal",
    "Minutes Per Assist",
    "Minutes Per Goal Conceded",
    "Minutes Per Booking",
    "Shots Per Goal Scored",
}

CATEGORIES = {
    "General":       ["Matches Played", "Minutes", "Matches Started",
                      "Matches Subbed In", "Matches Subbed Out"],
    "Goals & Shots": ["Goals Scored", "Goal Involvement", "Goals at Home",
                      "Goals at Away", "Expected Goals (xG)",
                      "Non-Penalty xG (npxG)", "Shot Conversion Rate",
                      "Minutes Per Goal"],
    "Shots":         ["Shots Taken", "Shots On Target", "Shots Off Target",
                      "Hit The Woodwork", "Shot Accuracy",
                      "Shots Per Goal Scored"],
    "Defending":     ["Goals Conceded", "Minutes Per Goal Conceded",
                      "Clean Sheets", "Tackles", "Interceptions",
                      "Clearances", "Shots Blocked", "Dribbled Past",
                      "Penalties Given Away", "Ground Duels",
                      "Ground Duels Won", "Aerial Duels Won"],
    "Passing":       ["Assists", "Expected Assists (xA)", "Passes",
                      "Successful Passes", "Pass Completion Rate",
                      "Key Passes", "Crosses", "Successful Crosses",
                      "Cross Completion Rate", "Minutes Per Assist"],
    "Dribbling":     ["Dribbles", "Successful Dribbles", "Dribble Success Rate",
                      "Dispossesed", "Offsides"],
    "Cards & Fouls": ["Yellow Cards", "Red Cards", "Total Cards",
                      "Cards Over 0.5", "Fouls Committed",
                      "Fouled Against", "Minutes Per Booking"],
    "Penalties":     ["Penalties Scored", "Penalties Taken",
                      "Penalties Missed", "Penalty Conversion Rate",
                      "Hat-tricks", "3 or More Goals", "2 or More Goals"],
}

# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------
def normalize(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def build_fs_lookup(fs_data: dict) -> dict:
    lookup = {}
    for url, record in fs_data.items():
        if not isinstance(record, dict):
            continue
        name = normalize(record.get("player_name", ""))
        if name:
            lookup.setdefault(name, []).append(record)
    return lookup

def match_player(tm_player: dict, fs_lookup: dict) -> dict:
    tm_name = normalize(tm_player.get("name", ""))
    tm_team = normalize(tm_player.get("team", ""))

    # 1. Exact match
    candidates = fs_lookup.get(tm_name, [])
    if candidates:
        if len(candidates) == 1:
            return candidates[0]
        for c in candidates:
            fs_team = normalize(c.get("fs_team", "") or c.get("player_team", ""))
            if fs_team and tm_team and (fs_team in tm_team or tm_team in fs_team):
                return c
        return candidates[0]

    # 2. Rapidfuzz fuzzy match
    if RAPIDFUZZ_AVAILABLE and tm_name:
        all_fs_names = list(fs_lookup.keys())
        result = rf_process.extractOne(
            tm_name,
            all_fs_names,
            scorer=rf_fuzz.WRatio,
            score_cutoff=FUZZY_THRESHOLD,
        )
        if result:
            matched_name, score, _ = result
            fuzzy_candidates = fs_lookup[matched_name]
            log(f"  Fuzzy: '{tm_player.get('name')}' → '{matched_name}' (score {score:.0f})")
            if len(fuzzy_candidates) == 1:
                return fuzzy_candidates[0]
            for c in fuzzy_candidates:
                fs_team = normalize(c.get("fs_team", "") or c.get("player_team", ""))
                if fs_team and tm_team and (fs_team in tm_team or tm_team in fs_team):
                    return c
            return fuzzy_candidates[0]

    return {}

# ---------------------------------------------------------------------------
# Per-90 enrichment
# ---------------------------------------------------------------------------
def _safe_float(s):
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "").replace("%", "").strip())
    except (ValueError, TypeError):
        return None

def enrich_per90(stats: dict) -> dict:
    minutes_str = None
    for key in ("Minutes", "minutes", "Minutes Played"):
        if key in stats and stats[key].get("total") is not None:
            minutes_str = stats[key]["total"]
            break
    if minutes_str is None:
        return stats
    minutes = _safe_float(minutes_str)
    if not minutes or minutes <= 0:
        return stats
    for stat_name, vals in stats.items():
        if vals.get("per_90") is not None:
            continue
        if stat_name in NO_PER90_STATS:
            continue
        total = _safe_float(vals.get("total"))
        if total is not None:
            vals["per_90"] = f"{(total / minutes) * 90:.2f}"
    return stats

# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------
def write_stats_section(f, stats: dict):
    printed = set()

    for cat, stat_names in CATEGORIES.items():
        section = {k: v for k, v in stats.items() if k in stat_names}
        if not section:
            continue

        is_penalty_cat = (cat == "Penalties")
        f.write(f"  {'─'*48}\n")
        f.write(f"  {cat.upper()}\n")
        f.write(f"  {'─'*48}\n")
        if is_penalty_cat:
            f.write(f"  {'STAT':<28} TOTAL\n")
        else:
            f.write(f"  {'STAT':<28} {'TOTAL':<12} PER 90\n")
        f.write(f"  {'─'*48}\n")

        for stat_name in stat_names:
            if stat_name not in stats:
                continue
            vals      = stats[stat_name]
            total_str = vals.get("total") if vals.get("total") is not None else "null"
            per90_str = vals.get("per_90") if vals.get("per_90") is not None else "null"
            printed.add(stat_name)

            if is_penalty_cat or stat_name in NO_PER90_STATS:
                f.write(f"  {stat_name:<28} {total_str}\n")
            else:
                f.write(f"  {stat_name:<28} {total_str:<12} {per90_str}\n")

    remaining = {k: v for k, v in stats.items() if k not in printed}
    if remaining:
        f.write(f"  {'─'*48}\n")
        f.write(f"  OTHER\n")
        f.write(f"  {'─'*48}\n")
        f.write(f"  {'STAT':<28} {'TOTAL':<12} PER 90\n")
        f.write(f"  {'─'*48}\n")
        for stat_name, vals in remaining.items():
            total_str = vals.get("total") if vals.get("total") is not None else "null"
            per90_str = vals.get("per_90") if vals.get("per_90") is not None else "null"
            if stat_name in NO_PER90_STATS:
                f.write(f"  {stat_name:<28} {total_str}\n")
            else:
                f.write(f"  {stat_name:<28} {total_str:<12} {per90_str}\n")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log("=" * 60)
    log(f"merge_only.py — Step 3 standalone  ({SEASON})")
    log("=" * 60)

    if not RAPIDFUZZ_AVAILABLE:
        log("[WARN] rapidfuzz not available — fuzzy matching disabled.")

    tm_players = load_tm()
    fs_data    = load_fs()
    fs_lookup  = build_fs_lookup(fs_data)

    matched   = 0
    not_found = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for player in tm_players:
            fs = match_player(player, fs_lookup)

            f.write("=" * 60 + "\n")
            f.write(f"  {'League':<40} {player.get('league',       'null')}\n")
            f.write(f"  {'Team':<40} {player.get('team',         'null')}\n")
            f.write(f"  {'Name':<40} {player.get('name',         'null')}\n")
            f.write(f"  {'Age':<40} {player.get('age',          'null')}\n")
            f.write(f"  {'Position':<40} {player.get('position',     'null')}\n")
            f.write(f"  {'Market Value':<40} {player.get('market_value', 'null')}\n")
            f.write(f"  {'Footystats URL':<40} "
                    f"{fs.get('fs_url', 'null') if fs else 'null'}\n")
            f.write("\n")

            if not fs or fs.get("no_data") or not fs.get("stats"):
                f.write(f"  {'─'*48}\n")
                f.write(f"  FOOTYSTATS — NO STATS AVAILABLE FOR {SEASON}\n")
                f.write(f"  All stats: null\n")
                f.write(f"  {'─'*48}\n")
                not_found += 1
            else:
                enriched = enrich_per90(dict(fs["stats"]))
                write_stats_section(f, enriched)
                matched += 1

            f.write("\n")

    log(f"Matched:   {matched} players")
    log(f"No stats:  {not_found} players")
    log(f"Saved {len(tm_players)} players -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()