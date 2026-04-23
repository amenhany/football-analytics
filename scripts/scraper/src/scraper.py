import asyncio
import csv
import json
import os
import random
import re
import time
from datetime import datetime
from playwright.async_api import async_playwright

try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("[WARN] rapidfuzz not installed. Run: pip install rapidfuzz")

try:
    from playwright_stealth import stealth_async
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("[WARN] playwright-stealth not installed. Run: pip install playwright-stealth")

# config
SEASON       = "2025/2026"
TM_SEASON_ID = "2025"

LEAGUES = {
    "premier-league": {
        "tm":  "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1",
        "fs":  "https://footystats.org/england/premier-league",
    },
    "la-liga": {
        "tm":  "https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1",
        "fs":  "https://footystats.org/spain/la-liga",
    },
}

TM_CONCURRENCY = 2
FS_CONCURRENCY = 5
TM_SLEEP       = 2.5
FS_SLEEP       = 1.5
MAX_RETRIES    = 3
RETRY_DELAY    = 5

STORAGE_STATE_FILE   = "scripts/scraper/config/tm_auth.json"
CHECKPOINT_TM        = "scripts/scraper/data/raw/tm_players.csv"
CHECKPOINT_FS        = "scripts/scraper/data/raw/fs_players.json"
CHROME_USER_DATA_DIR = None

# stat sections per position
DEFENDER_SECTIONS   = ["general-section", "defending-section",
                       "assists-section",  "dribbles-section", "cards-section"]
MIDFIELDER_SECTIONS = ["general-section", "goal-section",     "assists-section",
                       "dribbles-section", "cards-section",   "defending-section",
                       "pens-section"]
FORWARD_SECTIONS    = ["general-section", "goal-section",     "assists-section",
                       "dribbles-section", "pens-section"]
GOALKEEPER_SECTIONS = ["general-section", "defending-section",
                       "goal-section",    "assists-section"]

def get_sections_for_position(position: str) -> list:
    p = position.lower()
    if any(k in p for k in ("goalkeeper", "keeper", "gk")):
        return GOALKEEPER_SECTIONS
    if any(k in p for k in ("defender", "back", "centre-back", "cb", "lb", "rb")):
        return DEFENDER_SECTIONS
    if any(k in p for k in ("midfielder", "mid", "cm", "dm", "am")):
        return MIDFIELDER_SECTIONS
    if any(k in p for k in ("forward", "winger", "striker", "st", "cf", "lw", "rw")):
        return FORWARD_SECTIONS
    return list(dict.fromkeys(
        DEFENDER_SECTIONS + MIDFIELDER_SECTIONS + FORWARD_SECTIONS
    ))

# helpers
def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def jitter(base: float, lo: float = 0.5, hi: float = 1.5) -> float:
    return base + random.uniform(lo, hi)

async def human_delay(base: float):
    await asyncio.sleep(jitter(base))

async def mouse_jitter(page):
    try:
        await page.mouse.move(
            random.randint(100, 1100),
            random.randint(100, 700)
        )
        await asyncio.sleep(random.uniform(0.1, 0.3))
    except Exception:
        pass

def load_json_checkpoint(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  Resumed checkpoint: {path} ({len(data)} entries)")
        return data
    return {}

def save_json_checkpoint(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_tm_checkpoint() -> list:
    if not os.path.exists(CHECKPOINT_TM):
        return []
    with open(CHECKPOINT_TM, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save_tm_checkpoint(players: list):
    if not players:
        return
    with open(CHECKPOINT_TM, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=players[0].keys())
        writer.writeheader()
        writer.writerows(players)

async def with_retry(coro_fn, label: str, retries: int = MAX_RETRIES):
    delay = RETRY_DELAY
    for attempt in range(1, retries + 1):
        try:
            return await coro_fn()
        except Exception as e:
            if attempt == retries:
                print(f"  FINAL FAIL [{label}]: {e}")
                return None
            print(f"  Retry {attempt}/{retries-1} [{label}]: {e} — waiting {delay}s")
            await asyncio.sleep(delay)
            delay *= 2

async def block_resources(page):
    await page.route("**/*", lambda route: asyncio.ensure_future(
        route.abort() if route.request.resource_type in ("image", "media")
        else route.continue_()
    ))

async def apply_stealth(page):
    if STEALTH_AVAILABLE:
        await stealth_async(page)
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins',   {get: () => [1,2,3,4,5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-GB','en']});
        window.chrome = {runtime: {}};
        delete window.__playwright;
        delete window.__pw_manual;
        delete window.playwright;
    """)

# captcha detection
CAPTCHA_INDICATORS = ["captcha", "cf-challenge", "challenge-form",
                      "recaptcha", "hcaptcha", "cf_chl"]

async def check_and_handle_captcha(page, label: str = "") -> bool:
    try:
        url   = page.url.lower()
        title = (await page.title()).lower()
        html  = (await page.content()).lower()

        if any(i in url or i in title or i in html for i in CAPTCHA_INDICATORS):
            print(f"\n{'='*60}")
            print(f"  CAPTCHA detected{' — ' + label if label else ''}!")
            print(f"  Solve it in the browser window, then press ENTER here.")
            print(f"{'='*60}\n")
            await asyncio.get_event_loop().run_in_executor(None, input)
            print("  Resuming...")
            await human_delay(2.0)
            return True

        tables = await page.query_selector_all("table")
        if len(tables) == 0 and "footystats" in url:
            print(f"\n{'='*60}")
            print(f"  Page looks blocked or empty{' — ' + label if label else ''}!")
            print(f"  Check browser. Solve captcha if shown, then press ENTER.")
            print(f"{'='*60}\n")
            await asyncio.get_event_loop().run_in_executor(None, input)
            print("  Resuming...")
            await human_delay(2.0)
            return True

    except Exception:
        pass
    return False

# browser setup
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-infobars",
    "--window-size=1280,900",
]

CONTEXT_OPTIONS = dict(
    viewport={"width": 1280, "height": 900},
    user_agent=USER_AGENT,
    locale="en-GB",
    timezone_id="Europe/London",
    extra_http_headers={
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Sec-Ch-Ua":       '"Chromium";v="124", "Google Chrome";v="124"',
        "Sec-Ch-Ua-Mobile":   "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
    },
)

async def build_browser_and_context(pw):
    if CHROME_USER_DATA_DIR:
        print(f"  Using persistent Chrome profile: {CHROME_USER_DATA_DIR}")
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=CHROME_USER_DATA_DIR,
            channel="chrome", headless=False,
            args=LAUNCH_ARGS, **CONTEXT_OPTIONS,
        )
        return None, context

    browser = await pw.chromium.launch(
        headless=False, channel="chrome", args=LAUNCH_ARGS
    )
    if os.path.exists(STORAGE_STATE_FILE):
        print(f"  Loading saved session from {STORAGE_STATE_FILE}")
        context = await browser.new_context(
            storage_state=STORAGE_STATE_FILE, **CONTEXT_OPTIONS
        )
    else:
        print("  Starting fresh browser context")
        context = await browser.new_context(**CONTEXT_OPTIONS)
    return browser, context

async def save_storage_state(context):
    try:
        await context.storage_state(path=STORAGE_STATE_FILE)
        print(f"  Saved session -> {STORAGE_STATE_FILE}")
    except Exception as e:
        print(f"  Could not save session: {e}")

# Step 1 — Transfermarkt crawl
async def tm_get_teams(page, league_name: str, league_url: str) -> list:
    await apply_stealth(page)
    await page.goto(
        f"{league_url}?saison_id={TM_SEASON_ID}",
        timeout=60000,
        wait_until="domcontentloaded"
    )
    await check_and_handle_captcha(page, league_name)
    await human_delay(2.0)
    await mouse_jitter(page)

    teams = await page.evaluate("""
        () => {
            const cells = document.querySelectorAll(
                "td.hauptlink.no-border-links a[href*='/startseite/verein/']"
            );
            const seen = new Set();
            return Array.from(cells).map(a => ({
                name: a.innerText.trim(),
                url:  a.href.split("?")[0]
            })).filter(t => {
                if (!t.name || seen.has(t.url)) return false;
                seen.add(t.url);
                return true;
            });
        }
    """)
    for t in teams:
        t["league"] = league_name
    print(f"  TM {league_name}: {len(teams)} teams found")
    return teams


async def tm_fetch_squad(context, team: dict, semaphore) -> list:
    async with semaphore:
        page = await context.new_page()
        await apply_stealth(page)
        await block_resources(page)

        base      = team["url"].replace("startseite", "kader")
        squad_url = f"{base}/plus/1/galerie/0?saison_id={TM_SEASON_ID}"

        async def _go():
            await page.goto(squad_url, timeout=60000, wait_until="domcontentloaded")
            await check_and_handle_captcha(page, team["name"])
            await human_delay(jitter(TM_SLEEP))
            await mouse_jitter(page)

            return await page.evaluate("""
                () => {
                    const rows = document.querySelectorAll(
                        "table.items tbody tr.odd, table.items tbody tr.even"
                    );
                    return Array.from(rows).map(row => {
                        const nameEl  = row.querySelector(
                            "td.hauptlink a[href*='/profil/spieler/']"
                        );
                        const posEl   = row.querySelector("td.posrela .pos-text");
                        const posFb   = row.querySelector(
                            "td.posrela table tr:last-child td:last-child"
                        );

                        // age is embedded in the date cell as "DD/MM/YYYY (27)"
                        // so we extract the number inside parentheses
                        const allCentered = Array.from(
                            row.querySelectorAll("td.zentriert")
                        );
                        let age = "";
                        for (const td of allCentered) {
                            const text = td.innerText.trim();
                            const m = text.match(/\\((\\d{1,2})\\)/);
                            if (m) { age = m[1]; break; }
                        }

                        const valueEl = row.querySelector("td.rechts.hauptlink a");
                        const rawPos  = posEl ? posEl.innerText.trim()
                                      : posFb ? posFb.innerText.trim() : "";
                        return {
                            name:         nameEl  ? nameEl.innerText.trim()   : "",
                            position:     rawPos,
                            age:          age,
                            market_value: valueEl ? valueEl.innerText.trim()  : "N/A",
                        };
                    }).filter(p => p.name);
                }
            """)

        try:
            players = await with_retry(_go, team["name"])
            if players:
                for p in players:
                    p["team"]   = team["name"]
                    p["league"] = team["league"]
                print(f"  TM {team['name']}: {len(players)} players")
                return players
            return []
        except Exception as e:
            print(f"  TM {team['name']} failed: {e}")
            return []
        finally:
            await page.close()


async def step1_tm_crawl(context) -> list:
    existing = load_tm_checkpoint()
    if existing:
        print(f"Step 1 skipped — {len(existing)} TM players from {CHECKPOINT_TM}")
        return existing

    print(f"Step 1: Transfermarkt squad crawl ({SEASON})...")
    nav_page = await context.new_page()
    await apply_stealth(nav_page)
    await block_resources(nav_page)

    all_teams = []
    for league_name, urls in LEAGUES.items():
        teams = await tm_get_teams(nav_page, league_name, urls["tm"])
        all_teams.extend(teams)
        await human_delay(2.0)
    await nav_page.close()

    semaphore   = asyncio.Semaphore(TM_CONCURRENCY)
    results     = await asyncio.gather(
        *[tm_fetch_squad(context, team, semaphore) for team in all_teams]
    )
    all_players = [p for squad in results for p in squad]

    # deduplicate by name + team
    seen    = set()
    deduped = []
    for p in all_players:
        key = (p["name"].lower().strip(), p["team"].lower().strip())
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    print(f"Step 1 done: {len(deduped)} unique TM players")
    save_tm_checkpoint(deduped)
    print(f"  Saved -> {CHECKPOINT_TM}")
    return deduped


# Step 2 — Footystats crawl
FS_EXTRACT_JS = """
(targetSections) => {
    const noDataIndicators = [
        "no stats available", "no data available",
        "stats not available", "player not found"
    ];
    const bodyText = document.body ? document.body.innerText.toLowerCase() : "";
    const hasNoData = noDataIndicators.some(i => bodyText.includes(i));

    const nameEl    = document.querySelector(
        "h1.playerName, h1.player-name, .player-header h1, h1"
    );
    const playerName = nameEl ? nameEl.innerText.trim() : null;

    const teamEl    = document.querySelector(
        ".player-team, .team-name, .playerTeam"
    );
    const playerTeam = teamEl ? teamEl.innerText.trim() : null;

    const stats  = {};
    const tables = document.querySelectorAll("table");

    if (tables.length === 0 || hasNoData) {
        return {
            player_name: playerName,
            player_team: playerTeam,
            stats:       null,
            no_data:     true
        };
    }

    // strips newlines so "0\\n/ 0" becomes "0"
    function cleanCell(raw) {
        if (raw === null || raw === undefined) return null;
        const s = String(raw).trim();
        return s.split(/\\n|\\/\\s/)[0].trim() || null;
    }

    tables.forEach((table, i) => {
        const parentEl = table.parentElement;
        const parentId = parentEl ? parentEl.id || "" : "";

        // only use first table in pens-section to avoid career totals
        if (parentId === "pens-section") {
            const siblingTables = parentEl
                ? Array.from(parentEl.querySelectorAll("table"))
                : [];
            if (siblingTables.length > 0 && table !== siblingTables[0]) return;
        }

        if (!targetSections.includes(parentId) && i !== 4) return;

        table.querySelectorAll("tr").forEach(row => {
            const cells = row.querySelectorAll("td");
            if (cells.length < 2) return;
            const statName = cells[0].innerText.trim();
            if (!statName) return;

            const rawTotal = cells[1] ? cells[1].innerText.trim() : null;
            const rawPer90 = cells[2] ? cells[2].innerText.trim() : null;

            stats[statName] = {
                total:  cleanCell(rawTotal),
                per_90: cleanCell(rawPer90),
            };
        });
    });

    const hasStats = Object.keys(stats).length > 0;
    return {
        player_name: playerName,
        player_team: playerTeam,
        stats:       hasStats ? stats : null,
        no_data:     !hasStats
    };
}
"""


async def fs_get_team_links(page, league_name: str, league_url: str) -> list:
    await apply_stealth(page)
    await page.goto(league_url, timeout=60000, wait_until="domcontentloaded")
    await check_and_handle_captcha(page, f"FS {league_name}")
    await human_delay(2.0)
    await mouse_jitter(page)

    team_links = await page.evaluate("""
        () => {
            const seen  = new Set();
            const teams = [];
            const all   = document.querySelectorAll("a[href]");

            for (const a of all) {
                const href = a.href  || "";
                const text = a.innerText.trim();

                if (!href.includes("/clubs/")) continue;
                if (!text)                     continue;
                if (seen.has(href))            continue;

                seen.add(href);
                teams.push({
                    name: text,
                    url:  href.split("?")[0]
                });
            }
            return teams;
        }
    """)

    print(f"  FS {league_name}: {len(team_links)} teams found")
    return team_links


async def fs_get_player_links(page, team: dict) -> list:
    await apply_stealth(page)
    await page.goto(team["url"], timeout=60000, wait_until="domcontentloaded")
    await check_and_handle_captcha(page, f"FS team {team['name']}")
    await human_delay(jitter(FS_SLEEP, 0.3, 0.8))

    try:
        players_tab = (
            await page.query_selector("a:has-text('Players')") or
            await page.query_selector("a[href*='players']")
        )
        if players_tab:
            await players_tab.click()
            await asyncio.sleep(2)

    except Exception as e:
        print(f"  No Players tab: {e}")

    player_links = await page.evaluate("""
        () => {
            const seen    = new Set();
            const players = [];
            const all     = document.querySelectorAll("a[href]");

            for (const a of all) {
                const href = a.href  || "";
                const text = a.innerText.trim();

                if (!href.includes("/players/")) continue;
                if (!text)                       continue;
                if (seen.has(href))              continue;

                const afterPlayers = href.split("/players/")[1] || "";
                const parts        = afterPlayers.split("/").filter(p => p);
                if (parts.length < 2) continue;

                seen.add(href);
                players.push({
                    name: text,
                    url:  href.split("?")[0]
                });
            }
            return players;
        }
    """)

    print(f"  FS {team['name']}: {len(player_links)} players found")
    return player_links


async def fs_scrape_player(context, player_link: dict,
                           team: dict, league_name: str,
                           semaphore) -> dict:
    async with semaphore:
        page = await context.new_page()
        await apply_stealth(page)
        await block_resources(page)

        try:
            async def _go():
                await page.goto(
                    player_link["url"],
                    timeout=60000,
                    wait_until="domcontentloaded"
                )
                await check_and_handle_captcha(page, f"FS: {player_link['name']}")
                await asyncio.sleep(jitter(FS_SLEEP, 0.2, 0.6))

                title = await page.title()
                if "404" in title or "not found" in title.lower():
                    return None

                # try to select the 2025 season if the dropdown exists
                await page.evaluate("""
                    () => {
                        const selectors = [
                            "select[name='season']",
                            "select.season-select",
                            ".season-selector select",
                            "#season-select"
                        ];
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el) {
                                const options = Array.from(el.options);
                                const opt = options.find(o =>
                                    o.text.includes("2025") ||
                                    o.value.includes("2025")
                                );
                                if (opt) {
                                    el.value = opt.value;
                                    el.dispatchEvent(
                                        new Event('change', {bubbles: true})
                                    );
                                    return true;
                                }
                            }
                        }
                        return false;
                    }
                """)

                position = await page.evaluate("""
                    () => {
                        const posEl = document.querySelector(
                            ".player-position, .position, [data-position]"
                        );
                        return posEl ? posEl.innerText.trim() : "";
                    }
                """)

                target = get_sections_for_position(position)
                return await page.evaluate(FS_EXTRACT_JS, target)

            result = await with_retry(_go, f"FS: {player_link['name']}")

            if result is None:
                result = {
                    "player_name": player_link["name"],
                    "player_team": team["name"],
                    "stats":       None,
                    "no_data":     True
                }

            result["fs_url"]      = player_link["url"]
            result["fs_team"]     = team["name"]
            result["fs_league"]   = league_name
            result["player_name"] = result.get("player_name") or player_link["name"]
            result["player_team"] = result.get("player_team") or team["name"]

            if result.get("no_data"):
                print(f"  FS {player_link['name']}: no stats")
            else:
                print(f"  FS {player_link['name']}: "
                      f"{len(result.get('stats') or {})} stats")

            return result

        except Exception as e:
            print(f"  FS failed {player_link['name']}: {e}")
            return {
                "fs_url":      player_link["url"],
                "fs_team":     team["name"],
                "fs_league":   league_name,
                "player_name": player_link["name"],
                "player_team": team["name"],
                "stats":       None,
                "no_data":     True
            }
        finally:
            await page.close()


async def step2_fs_crawl(context) -> dict:
    checkpoint = load_json_checkpoint(CHECKPOINT_FS)

    print("Step 2: Footystats crawl — collecting team and player links...")
    nav_page = await context.new_page()
    await apply_stealth(nav_page)
    await block_resources(nav_page)

    all_player_links = []

    for league_name, urls in LEAGUES.items():
        print(f"  FS crawling league: {league_name}...")
        team_links = await fs_get_team_links(nav_page, league_name, urls["fs"])

        for team in team_links:
            team["league"] = league_name
            try:
                player_links = await fs_get_player_links(nav_page, team)
                print(f"    FS {team['name']}: {len(player_links)} players found")
                for pl in player_links:
                    if pl["url"] not in checkpoint:
                        all_player_links.append((pl, team, league_name))
                    else:
                        print(f"    Skipping cached: {pl['name']}")
                await human_delay(jitter(FS_SLEEP, 0.3, 0.8))
            except Exception as e:
                print(f"    FS {team['name']} player links failed: {e}")
                continue

    await nav_page.close()

    print(f"  FS: {len(checkpoint)} cached, "
          f"{len(all_player_links)} to scrape")

    if all_player_links:
        semaphore = asyncio.Semaphore(FS_CONCURRENCY)
        total     = len(all_player_links)
        done      = 0
        start     = time.time()
        lock      = asyncio.Lock()

        async def run(player_link, team, league_name):
            nonlocal done
            result = await fs_scrape_player(
                context, player_link, team, league_name, semaphore
            )
            async with lock:
                done += 1
                checkpoint[player_link["url"]] = result
                elapsed = time.time() - start
                rate    = done / elapsed if elapsed > 0 else 1
                eta     = (total - done) / rate
                if done % 25 == 0 or done == total:
                    print(f"  FS Progress: {done}/{total} | "
                          f"{rate:.1f}/s | ETA: {eta/60:.1f} min")
                if done % 100 == 0:
                    save_json_checkpoint(CHECKPOINT_FS, checkpoint)

        await asyncio.gather(*[
            run(pl, team, league_name)
            for pl, team, league_name in all_player_links
        ])
        save_json_checkpoint(CHECKPOINT_FS, checkpoint)
        print(f"  Saved -> {CHECKPOINT_FS}")

    print(f"Step 2 done: {len(checkpoint)} FS players")
    return checkpoint


PENALTY_STATS: set = {
    "Penalties Scored",
    "Penalties Taken",
    "Penalties Missed",
    "Penalty Conversion Rate",
    "Hat-tricks",
    "3 or More Goals",
    "2 or More Goals",
}

NO_PER90_STATS: set = PENALTY_STATS | {
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


def normalize(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_fs_lookup(fs_data: dict) -> dict:
    lookup: dict = {}
    for url, record in fs_data.items():
        if not isinstance(record, dict):
            continue
        name = normalize(record.get("player_name", ""))
        if name:
            lookup.setdefault(name, []).append(record)
    return lookup


FUZZY_THRESHOLD = 80


def match_player(tm_player: dict, fs_lookup: dict) -> dict:
    tm_name = normalize(tm_player.get("name", ""))
    tm_team = normalize(tm_player.get("team", ""))

    # try exact match first
    candidates = fs_lookup.get(tm_name, [])
    if candidates:
        if len(candidates) == 1:
            return candidates[0]
        for c in candidates:
            fs_team = normalize(c.get("fs_team", "") or c.get("player_team", ""))
            if fs_team and tm_team and (fs_team in tm_team or tm_team in fs_team):
                return c
        return candidates[0]

    # fall back to fuzzy matching
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
            print(f"  Fuzzy match: '{tm_player.get('name')}' → '{matched_name}' "
                  f"(score {score:.0f})")
            if len(fuzzy_candidates) == 1:
                return fuzzy_candidates[0]
            for c in fuzzy_candidates:
                fs_team = normalize(c.get("fs_team", "") or c.get("player_team", ""))
                if fs_team and tm_team and (fs_team in tm_team or tm_team in fs_team):
                    return c
            return fuzzy_candidates[0]

    return {}


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


def _safe_float(s):
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "").replace("%", "").strip())
    except (ValueError, TypeError):
        return None


def compute_per90(stat_name: str, total_str, minutes_str):
    if stat_name in NO_PER90_STATS:
        return None
    total   = _safe_float(total_str)
    minutes = _safe_float(minutes_str)
    if total is None or minutes is None or minutes <= 0:
        return None
    return f"{(total / minutes) * 90:.2f}"


def enrich_per90(stats: dict) -> dict:
    minutes_str = None
    for key in ("Minutes", "minutes", "Minutes Played"):
        if key in stats and stats[key].get("total") is not None:
            minutes_str = stats[key]["total"]
            break

    if minutes_str is None:
        return stats

    for stat_name, vals in stats.items():
        if vals.get("per_90") is not None:
            continue
        calculated = compute_per90(stat_name, vals.get("total"), minutes_str)
        if calculated is not None:
            vals["per_90"] = calculated

    return stats


def write_stats_section(f, stats: dict):
    printed: set = set()

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
            vals  = stats[stat_name]
            total = vals.get("total")
            per90 = vals.get("per_90")
            total_str = total if total is not None else "null"

            if is_penalty_cat or stat_name in NO_PER90_STATS:
                f.write(f"  {stat_name:<28} {total_str}\n")
            else:
                per90_str = per90 if per90 is not None else "null"
                f.write(
                    f"  {stat_name:<28} "
                    f"{total_str:<12} "
                    f"{per90_str}\n"
                )
            printed.add(stat_name)

    remaining = {k: v for k, v in stats.items() if k not in printed}
    if remaining:
        f.write(f"  {'─'*48}\n")
        f.write(f"  OTHER\n")
        f.write(f"  {'─'*48}\n")
        f.write(f"  {'STAT':<28} {'TOTAL':<12} PER 90\n")
        f.write(f"  {'─'*48}\n")
        for stat_name, vals in remaining.items():
            total = vals.get("total")
            per90 = vals.get("per_90")
            if stat_name in NO_PER90_STATS:
                f.write(f"  {stat_name:<28} "
                        f"{total if total is not None else 'null'}\n")
            else:
                f.write(
                    f"  {stat_name:<28} "
                    f"{total if total is not None else 'null':<12} "
                    f"{per90 if per90 is not None else 'null'}\n"
                )


async def main():
    print("=" * 60)
    print(f"Football Player Scraper  —  Season: {SEASON}")
    print("Sources: Transfermarkt + Footystats")
    print("=" * 60)

    if not STEALTH_AVAILABLE:
        print("TIP: pip install playwright-stealth")

    t0 = time.time()

    async with async_playwright() as pw:
        browser, context = await build_browser_and_context(pw)

        # Step 1 — scrape TM squads
        tm_players = await step1_tm_crawl(context)
        await save_storage_state(context)

        # Step 2 — scrape Footystats player stats
        fs_data = await step2_fs_crawl(context)
        await save_storage_state(context)

        await context.close()
        if browser:
            await browser.close()

    print(f"\nFinished in {(time.time()-t0)/60:.1f} minutes.")
    print("Delete checkpoint files to re-scrape from scratch.")
    print(f"Delete {STORAGE_STATE_FILE} to force a fresh browser session.")


asyncio.run(main())