import re
import csv
from collections import Counter

STAT_END  = 31
TOTAL_END = 44

def parse_stat_line(line):
    if len(line.rstrip('\n')) < STAT_END:
        return None, None, None
    stat_name = line[:STAT_END].strip()
    if not stat_name:
        return None, None, None
    total  = line[STAT_END:TOTAL_END].strip() if len(line) > STAT_END  else ""
    per_90 = line[TOTAL_END:].strip()         if len(line) > TOTAL_END else ""
    return stat_name or None, total or None, per_90 or None

def parse_player_block(block):
    row   = {}
    lines = block.splitlines()

    header_fields = ["League", "Team", "Name", "Age", "Position", "Market Value", "Footystats URL"]
    for line in lines:
        stripped = line.strip()
        for field in header_fields:
            if stripped.startswith(field):
                row[field] = stripped[len(field):].strip()
                break

    if not row.get("Name"):
        return None

    if any("NO STATS AVAILABLE" in l or "All stats: null" in l for l in lines):
        return row

    SECTION_NAMES = {
        "GENERAL", "GOALS & SHOTS", "SHOTS", "DEFENDING",
        "PASSING", "DRIBBLING", "CARDS & FOULS", "PENALTIES", "OTHER"
    }

    current_section = None
    stats = {}  # store as (section, stat_name) -> (total, per90)
    for line in lines:
        stripped = line.strip()
        if re.match(r'^[─\-]{5,}$', stripped):
            continue
        if stripped.upper() in SECTION_NAMES:
            current_section = stripped.upper().title()
            continue
        if stripped.startswith("STAT") and "TOTAL" in stripped:
            continue
        if current_section and stripped:
            stat_name, total, per_90 = parse_stat_line(line)
            if stat_name and total:
                stats[(current_section, stat_name)] = (total, per_90)

    row["_stats"] = stats
    return row


def convert(input_path, output_csv):
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    raw_blocks = re.split(r'={20,}', content)
    players = []
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue
        player = parse_player_block(block)
        if player:
            players.append(player)

    # Find which stat names appear in more than one section
    stat_name_counts = Counter()
    for p in players:
        seen_in_player = set()
        for (section, stat_name) in p.get("_stats", {}):
            seen_in_player.add(stat_name)
        for s in seen_in_player:
            stat_name_counts[s] += 0  # just register existence
    # Count across ALL section combos
    all_keys = Counter()
    for p in players:
        for (section, stat_name) in p.get("_stats", {}):
            all_keys[stat_name] += 1

    # Find stat names that appear under multiple different sections
    stat_sections = {}
    for p in players:
        for (section, stat_name) in p.get("_stats", {}):
            stat_sections.setdefault(stat_name, set()).add(section)
    duplicate_stats = {s for s, secs in stat_sections.items() if len(secs) > 1}

    def col_name(section, stat_name, is_per90=False):
        base = f"{section} | {stat_name}" if stat_name in duplicate_stats else stat_name
        return f"{base} (Per90)" if is_per90 else base

    # Build ordered column list
    header_fields = ["League", "Team", "Name", "Age", "Position", "Market Value", "Footystats URL"]
    all_cols = list(header_fields)
    seen_cols = set(header_fields)
    for p in players:
        for (section, stat_name), (total, per_90) in p.get("_stats", {}).items():
            c_total = col_name(section, stat_name)
            c_per90 = col_name(section, stat_name, is_per90=True)
            if c_total not in seen_cols:
                all_cols.append(c_total)
                seen_cols.add(c_total)
            if per_90 and c_per90 not in seen_cols:
                all_cols.append(c_per90)
                seen_cols.add(c_per90)

    # Write CSV
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction="ignore")
        writer.writeheader()
        for p in players:
            row = {k: v for k, v in p.items() if k != "_stats"}
            for (section, stat_name), (total, per_90) in p.get("_stats", {}).items():
                row[col_name(section, stat_name)] = total
                if per_90:
                    row[col_name(section, stat_name, is_per90=True)] = per_90
            writer.writerow({col: row.get(col, "") for col in all_cols})

    print(f"Done! {len(players)} players, {len(all_cols)} columns -> {output_csv}")


if __name__ == "__main__":
    INPUT_FILE = "scripts/scraper/data/merged/players.txt"
    OUTPUT_CSV = "data/raw/players.csv"  
    convert(INPUT_FILE, OUTPUT_CSV)