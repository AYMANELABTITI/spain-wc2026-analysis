"""Fetch REAL WC26 data from FotMob's public API (Opta-sourced).

Everything the report plots as a data chart comes from here. Raw JSON is
cached under data/fotmob/ so every number is auditable and reruns are free.

Writes:
    data/matches.csv            per-match xG, possession, shots, SOT, passes
    data/final_shots.csv        the Final's shotmap (coords, xG, outcomes)
    data/final_momentum.csv     the Final's minute-by-minute momentum
    data/players.csv            minutes, goals, assists, ages (16 players)
    data/player_touches.csv     real touch coordinates from match heatmaps
    data/player_positions.csv   average touch position + volume per player
    data/player_profiles.csv    key-player metrics + true tournament percentiles
    data/teams_comparison.csv   real totals for Spain and the sides it beat
    data/league_team_stats.csv  tournament-wide team rankings (32 teams)
    data/attacking_zones.csv    left/centre/right attack distribution per match

Run:  python scripts/fetch_fotmob.py        (no API key required)
"""

import gzip
import json
import re
import time
import unicodedata
import urllib.request
from pathlib import Path

import pandas as pd

API = "https://www.fotmob.com/api/data"
STATS = "https://data.fotmob.com/stats/77/season/24254"
SPAIN_ID, LEAGUE_WC, SEASON = 6720, 77, 2026
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0",
      "Accept-Encoding": "gzip"}

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = DATA / "fotmob"

STAGES = ["Group C", "Group C", "Group C", "Round of 32", "Round of 16",
          "Quarter-final", "Semi-final", "Final"]
# rivals Spain eliminated that FotMob covers in every team feed (Uruguay is
# absent from several league feeds, so it is left out rather than part-filled)
RIVALS = ["Argentina", "France", "Portugal", "Belgium"]

# tournament-wide team feeds worth keeping (feed file -> column name)
TEAM_FEEDS = {
    "expected_goals_team": "xg_for",
    "expected_goals_conceded_team": "xg_against",
    "possession_percentage_team": "possession_avg",
    "poss_won_att_3rd_team": "poss_won_final_third",
    "interception_team": "interceptions",
    "total_tackle_team": "tackles",
    "touches_in_opp_box_team": "touches_opp_box",
    "big_chance_team": "big_chances",
    "clean_sheet_team": "clean_sheets",
    "accurate_pass_team": "accurate_passes",
}

# player feeds used to build true percentile profiles
PLAYER_FEEDS = {
    "accurate_pass": "Accurate passes per 90",
    "ball_recovery": "Recoveries per 90",
    "defensive_contributions": "Defensive actions per 90",
    "won_contest": "Successful dribbles per 90",
    "total_att_assist": "Chances created",
    "expected_assists": "Expected assists (xA)",
    "goals": "Goals",
    "expected_goals": "Expected goals (xG)",
    "ontarget_scoring_att": "Shots on target per 90",
    "interception": "Interceptions per 90",
    "effective_clearance": "Clearances per 90",
    "accurate_long_balls": "Accurate long balls per 90",
    "clean_sheet": "Clean sheets",
    "poss_won_att_3rd": "Possession won final 3rd per 90",
}

# which three real metrics each key player's card shows
PROFILE_CARDS = {
    "Rodri": ("DM - Golden Ball winner",
              ["accurate_pass", "ball_recovery", "defensive_contributions"]),
    "Lamine Yamal": ("RW - 19 years old",
                     ["won_contest", "total_att_assist", "expected_assists"]),
    "Mikel Oyarzabal": ("ST - Spain top scorer",
                        ["goals", "expected_goals", "ontarget_scoring_att"]),
    "Unai Simon": ("GK - Golden Glove winner",
                   ["clean_sheet", "ball_recovery", "accurate_pass"]),
    "Pau Cubarsi": ("CB - Best Young Player (19)",
                    ["interception", "effective_clearance", "accurate_long_balls"]),
    "Dani Olmo": ("AM - the pocket finder",
                  ["total_att_assist", "poss_won_att_3rd", "accurate_pass"]),
}
MIN_MINUTES = 180   # qualification threshold for percentile ranking

# FotMob position ids group into four families; percentiles are computed
# within a player's own family so a keeper is never ranked against wingers.
def position_group(positions) -> str:
    pid = (positions or [0])[0]
    if pid == 11:
        return "GK"
    if 30 <= pid < 40:
        return "DEF"
    if 60 <= pid < 80:
        return "MID"
    return "ATT"


# --------------------------------------------------------------- plumbing
def get(url: str, cache_name: str) -> dict:
    """GET with gzip handling and on-disk caching."""
    f = CACHE / cache_name
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    req = urllib.request.Request(url, headers=UA)
    raw = urllib.request.urlopen(req, timeout=30).read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    payload = json.loads(raw.decode("utf-8"))
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(payload), encoding="utf-8")
    time.sleep(1.2)                      # be a polite client
    return payload


def norm(name: str) -> str:
    """Accent-insensitive key so API names join to CSV names."""
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore") \
        .decode().lower().strip()


def stat_pair(all_stats: list, title: str, group: str | None = None):
    """Pull a [home, away] stat pair out of FotMob's nested stat groups."""
    for g in all_stats:
        if group and g["title"] != group:
            continue
        for s in g["stats"]:
            if s["title"] == title and s["stats"][0] not in (None, ""):
                return s["stats"]
    return [None, None]


def num(value) -> float:
    """'763 (89%)' -> 763.0 ; '2.29' -> 2.29 ; None -> 0.0"""
    if value in (None, ""):
        return 0.0
    m = re.match(r"[\d.]+", str(value))
    return float(m.group()) if m else 0.0


# --------------------------------------------------------------- fetchers
def spain_fixtures() -> list[dict]:
    league = get(f"{API}/leagues?id={LEAGUE_WC}&season={SEASON}", "league.json")
    fx = [m for m in league["fixtures"]["allMatches"]
          if SPAIN_ID in (int(m["home"]["id"]), int(m["away"]["id"]))]
    fx.sort(key=lambda m: m["status"]["utcTime"])
    assert len(fx) == 8, f"expected 8 Spain matches, got {len(fx)}"
    return fx


def league_team_stats() -> pd.DataFrame:
    """Tournament-wide team rankings — one row per team, one column per feed."""
    frame = {}
    for feed, col in TEAM_FEEDS.items():
        payload = get(f"{STATS}/{feed}.json", f"stat_{feed}.json")
        for e in payload["TopLists"][0]["StatList"]:
            row = frame.setdefault(e["ParticipantName"], {"matches": e["MatchesPlayed"]})
            row[col] = e["StatValue"]
            row[f"{col}_rank"] = e["Rank"]
    df = pd.DataFrame(frame).T.rename_axis("team").reset_index()
    df.to_csv(DATA / "league_team_stats.csv", index=False)
    print(f"league_team_stats.csv: {len(df)} teams x {len(TEAM_FEEDS)} real metrics")
    return df


def player_percentiles() -> dict:
    """{feed: {player_key: (value, percentile, n_peers)}}.

    Percentile is computed against players in the SAME position family who
    cleared MIN_MINUTES — a real ranking, not a modelled one.
    """
    out = {}
    for feed in PLAYER_FEEDS:
        payload = get(f"{STATS}/{feed}.json", f"stat_{feed}.json")
        rows = [e for e in payload["TopLists"][0]["StatList"]
                if e.get("MinutesPlayed", 0) >= MIN_MINUTES]
        by_group = {}
        for e in rows:
            by_group.setdefault(position_group(e.get("Positions")), []) \
                    .append(e["StatValue"])
        entry = {}
        for e in rows:
            peers = sorted(by_group[position_group(e.get("Positions"))])
            pct = round(100 * sum(v <= e["StatValue"] for v in peers) / len(peers))
            entry[norm(e["ParticipantName"])] = (e["StatValue"], pct, len(peers))
        out[feed] = entry
    print(f"player percentiles: {len(PLAYER_FEEDS)} feeds, ranked within "
          f"position group among {MIN_MINUTES}+ minute players")
    return out


def heatmap_touches(fixtures: list[dict]) -> pd.DataFrame:
    """Real touch coordinates per player, parsed from FotMob's heatmap SVG."""
    circle = re.compile(r'cx="([\d.]+)" cy="([\d.]+)"')
    rows, id_to_name = [], {}
    for fx in fixtures:
        detail = get(f"{API}/matchDetails?matchId={fx['id']}",
                     f"match_{fx['id']}.json")
        # heatmap keys are Opta ids ("p19054"), not FotMob player ids
        for p in detail["content"]["playerStats"].values():
            if p.get("teamId") == SPAIN_ID and p.get("optaId"):
                id_to_name[str(p["optaId"])] = p["name"]
        hm = get("https://www.fotmob.com" + detail["content"]["heatmapUrl"],
                 f"heatmap_{fx['id']}.json")
        # Spain plays right-to-left in some matches; FotMob normalises the
        # heatmap to attacking direction, so coordinates are directly usable.
        for pid, svg in hm["players"].items():
            name = id_to_name.get(pid.lstrip("p"))
            if not name:
                continue
            for cx, cy in circle.findall(svg):
                rows.append((name, float(cx), float(cy)))
    df = pd.DataFrame(rows, columns=["player", "x", "y"])
    # FotMob spells some names differently across matches (Ferran/Ferrán) —
    # collapse to the most common spelling per accent-insensitive key
    canonical = (df.assign(key=df.player.map(norm))
                   .groupby(["key", "player"]).size()
                   .sort_values(ascending=False).reset_index()
                   .drop_duplicates("key").set_index("key").player)
    df["player"] = df.player.map(norm).map(canonical)
    df.to_csv(DATA / "player_touches.csv", index=False)
    pos = (df.groupby("player")
             .agg(x=("x", "mean"), y=("y", "mean"), touches=("x", "size"))
             .round(1).reset_index())
    pos.to_csv(DATA / "player_positions.csv", index=False)
    print(f"player_touches.csv: {len(df)} real touch points, "
          f"{df.player.nunique()} players")
    return df


# --------------------------------------------------------------- builders
def build_matches(fixtures: list[dict], old: pd.DataFrame) -> pd.DataFrame:
    rows, minutes, goals, assists, ages, zones = [], {}, {}, {}, {}, []
    all_shots = []
    for i, fx in enumerate(fixtures):
        d = get(f"{API}/matchDetails?matchId={fx['id']}", f"match_{fx['id']}.json")
        spain_home = d["general"]["homeTeam"]["id"] == SPAIN_ID
        idx, opp = (0, 1) if spain_home else (1, 0)
        opponent = d["general"]["awayTeam" if spain_home else "homeTeam"]["name"]
        st = d["content"]["stats"]["Periods"]["All"]["stats"]
        score = [int(x) for x in d["header"]["status"]["scoreStr"].split(" - ")]
        xg = stat_pair(st, "Expected goals (xG)", "Expected goals (xG)")
        rows.append({
            "match_no": i + 1, "stage": STAGES[i], "opponent": opponent,
            "date": fx["status"]["utcTime"][:10], "venue": old.iloc[i]["venue"],
            "gf": score[idx], "ga": score[opp],
            "xg_for": num(xg[idx]), "xg_against": num(xg[opp]),
            "xg_open_play": num(stat_pair(st, "xG open play")[idx]),
            "xg_set_play": num(stat_pair(st, "xG set play")[idx]),
            "possession": int(num(stat_pair(st, "Ball possession")[idx])),
            "shots": int(num(stat_pair(st, "Total shots", "Shots")[idx])),
            "shots_on_target": int(num(stat_pair(st, "Shots on target", "Shots")[idx])),
            "touches_opp_box": int(num(stat_pair(st, "Touches in opposition box")[idx])),
            "big_chances": int(num(stat_pair(st, "Big chances")[idx])),
            "passes_own_half": int(num(stat_pair(st, "Own half")[idx])),
            "passes_opp_half": int(num(stat_pair(st, "Opposition half")[idx])),
            "tackles": int(num(stat_pair(st, "Tackles")[idx])),
            "interceptions": int(num(stat_pair(st, "Interceptions")[idx])),
            "opp_passes": int(num(stat_pair(st, "Passes", "Passes")[opp])),
            "opp_fouls": int(num(stat_pair(st, "Fouls committed")[opp])),
            "scorers": old.iloc[i]["scorers"],
        })

        az = d["content"]["attackingZones"]["home" if spain_home else "away"]["total"]
        zones.append({"match_no": i + 1, "stage": STAGES[i], "opponent": opponent,
                      **az})

        for p in d["content"]["playerStats"].values():
            if p.get("teamId") != SPAIN_ID:
                continue
            top = next((g["stats"] for g in p["stats"]
                        if g["title"] == "Top stats"), {})
            def v(name):
                return num(top.get(name, {}).get("stat", {}).get("value"))
            k = norm(p["name"])
            minutes[k] = minutes.get(k, 0) + v("Minutes played")
            goals[k] = goals.get(k, 0) + v("Goals")
            assists[k] = assists.get(k, 0) + v("Assists")

        for side in ("homeTeam", "awayTeam"):
            team = d["content"]["lineup"][side]
            if team["id"] == SPAIN_ID:
                for p in team["starters"] + team["subs"]:
                    if p.get("age"):
                        ages[norm(p["name"])] = int(p["age"])

        for s in d["content"]["shotmap"]["shots"]:      # every Spain shot
            if s["teamId"] != SPAIN_ID:
                continue
            all_shots.append({
                "match_no": i + 1, "stage": STAGES[i], "opponent": opponent,
                "minute": int(s["min"]), "player": s["playerName"],
                "x": round(float(s["x"]), 1), "y": round(float(s["y"]), 1),
                "xg": round(float(s["expectedGoals"]), 3),
                "is_goal": int(s["eventType"] == "Goal"),
                "situation": s.get("situation") or "",
                "shot_type": s.get("shotType") or ""})

        if STAGES[i] == "Final":
            shots = []
            for s in d["content"]["shotmap"]["shots"]:
                team = "Spain" if s["teamId"] == SPAIN_ID else "Argentina"
                x, y = float(s["x"]), float(s["y"])
                if team == "Argentina":
                    x, y = 105 - x, 68 - y          # mirror for a two-sided map
                shots.append({
                    "team": team, "minute": int(s["min"]),
                    "x": round(x, 1), "y": round(y, 1),
                    "xg": round(float(s["expectedGoals"]), 3),
                    "outcome": ("goal" if s["eventType"] == "Goal" else
                                "on_target" if s.get("isOnTarget") else
                                "off_target" if s["eventType"] == "Miss" else
                                "blocked"),
                    "player": s["playerName"]})
            pd.DataFrame(shots).to_csv(DATA / "final_shots.csv", index=False)
            print(f"final_shots.csv: {len(shots)} real shots")

            mom = pd.DataFrame(d["content"]["momentum"]["main"]["data"])
            mom.to_csv(DATA / "final_momentum.csv", index=False)
            print(f"final_momentum.csv: {len(mom)} real momentum readings")

    matches = pd.DataFrame(rows)
    matches.to_csv(DATA / "matches.csv", index=False)
    pd.DataFrame(zones).to_csv(DATA / "attacking_zones.csv", index=False)
    shots_df = pd.DataFrame(all_shots)
    shots_df.to_csv(DATA / "all_shots.csv", index=False)
    print(f"all_shots.csv: {len(shots_df)} Spain shots across 8 matches, "
          f"{shots_df.is_goal.sum()} goals")

    # how the goals were scored, straight from FotMob's situation tags
    label = {"RegularPlay": "Open play", "FastBreak": "Fast break",
             "FromCorner": "Corner", "SetPiece": "Set piece",
             "FreeKick": "Free kick", "Penalty": "Penalty",
             "IndividualPlay": "Individual play"}
    types = (shots_df[shots_df.is_goal == 1].situation.map(label)
             .value_counts().rename_axis("type").reset_index(name="count"))
    own_goals = int(matches.gf.sum() - shots_df.is_goal.sum())
    if own_goals:
        types.loc[len(types)] = ["Own goal won", own_goals]
    types.to_csv(DATA / "goal_types.csv", index=False)
    print("goal_types.csv: " + ", ".join(f"{r['count']} {r.type.lower()}"
                                         for _, r in types.iterrows()))
    print(f"matches.csv: real xG {matches.xg_for.sum():.1f}-"
          f"{matches.xg_against.sum():.1f}, possession "
          f"{matches.possession.min()}-{matches.possession.max()}%")
    print("attacking_zones.csv: real left/centre/right attack split per match")
    return matches, minutes, goals, assists, ages


def build_players(minutes, goals, assists, ages) -> pd.DataFrame:
    players = pd.read_csv(DATA / "players.csv")
    keys = players.player.map(norm)
    players["minutes"] = [int(minutes.get(k, 0)) for k in keys]
    players["goals"] = [int(goals.get(k, 0)) for k in keys]
    players["assists"] = [int(assists.get(k, 0)) for k in keys]
    players["age"] = [ages.get(k, a) for k, a in zip(keys, players.age)]
    players.to_csv(DATA / "players.csv", index=False)
    print(f"players.csv: real minutes/goals/assists — {players.goals.sum()} goals, "
          f"{players.minutes.sum()} player-minutes")
    return players


def build_profiles(pct: dict) -> None:
    rows = []
    for player, (role, feeds) in PROFILE_CARDS.items():
        key = norm(player)
        for feed in feeds:
            value, percentile, peers = pct[feed].get(key, (None, None, None))
            if value is None:
                print(f"  ! no qualified entry for {player} / {feed}")
                continue
            rows.append({"player": player, "role_line": role,
                         "metric": PLAYER_FEEDS[feed], "value_label": f"{value:g}",
                         "percentile": percentile, "peers": peers})
    df = pd.DataFrame(rows)
    df.to_csv(DATA / "player_profiles.csv", index=False)
    print(f"player_profiles.csv: {len(df)} real metrics with true percentiles")


def build_teams(league: pd.DataFrame) -> None:
    """Spain + the sides it eliminated, plus England (the side it never met)."""
    wanted = ["Spain"] + RIVALS + ["England"]
    results = {"Spain": "Champions", "Argentina": "Runners-up",
               "France": "Semi-final", "Portugal": "Round of 16",
               "Belgium": "Quarter-final", "England": "Third place"}
    gf_feed = get(f"{STATS}/goals_team_match.json", "stat_goals_team_match.json")
    ga_feed = get(f"{STATS}/goals_conceded_team_match.json",
                  "stat_goals_conceded_team_match.json")

    def total(feed, team):
        e = next((x for x in feed["TopLists"][0]["StatList"]
                  if x["ParticipantName"] == team), None)
        return (round(e["StatValue"] * e["MatchesPlayed"]),
                e["MatchesPlayed"]) if e else (None, None)

    df = league[league.team.isin(wanted)].copy()
    df["gf"] = df.team.map(lambda t: total(gf_feed, t)[0])
    df["ga"] = df.team.map(lambda t: total(ga_feed, t)[0])
    df["matches"] = df.team.map(lambda t: total(gf_feed, t)[1])
    df["final_result"] = df.team.map(results)
    cols = ["team", "matches", "gf", "ga", "xg_for", "xg_against",
            "possession_avg", "poss_won_final_third",
            "poss_won_final_third_rank", "interceptions", "tackles",
            "big_chances", "clean_sheets", "final_result"]
    df = df[cols].dropna(subset=["gf", "xg_for", "possession_avg"])
    df.to_csv(DATA / "teams_comparison.csv", index=False)
    print(f"teams_comparison.csv: real totals for {len(df)} teams "
          f"(Spain, the sides it beat, and England)")


def main() -> None:
    fixtures = spain_fixtures()
    old = pd.read_csv(DATA / "matches.csv")
    league = league_team_stats()
    pct = player_percentiles()
    matches, minutes, goals, assists, ages = build_matches(fixtures, old)
    build_players(minutes, goals, assists, ages)
    build_profiles(pct)
    build_teams(league)
    heatmap_touches(fixtures)
    print("\nAll report data now sourced from FotMob. Raw JSON: data/fotmob/")


if __name__ == "__main__":
    main()
