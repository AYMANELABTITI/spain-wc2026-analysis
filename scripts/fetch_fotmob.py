"""Fetch REAL WC26 data for Spain's eight matches from FotMob's public API.

Downloads and caches the raw JSON under data/fotmob/, then rewrites the
data layers that previously carried estimates with provider numbers:

    data/matches.csv       real xG, possession, shots, shots on target
    data/final_shots.csv   the Final's real shotmap (coords, xG, outcomes)
    data/players.csv       real minutes, goals, assists, ages (other columns kept)
    data/teams_comparison.csv  Spain row updated with real totals

Run:  python scripts/fetch_fotmob.py     (no API key needed)
"""

import json
import time
import unicodedata
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://www.fotmob.com/api/data"
LEAGUE_WC, SEASON, SPAIN_ID = 77, 2026, 6720
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = DATA / "fotmob"

STAGES = ["Group C", "Group C", "Group C", "Round of 32", "Round of 16",
          "Quarter-final", "Semi-final", "Final"]


def get(url: str, cache_name: str) -> dict:
    f = CACHE / cache_name
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(payload), encoding="utf-8")
    time.sleep(1.5)  # be polite
    return payload


def norm(name: str) -> str:
    """Accent-insensitive key for joining API names to CSV names."""
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore") \
        .decode().lower()


def stat_pair(period_all: list, title: str):
    for group in period_all:
        for s in group["stats"]:
            if s["title"] == title and s["stats"][0] not in (None, ""):
                return s["stats"]
    return [None, None]


def main() -> None:
    league = get(f"{BASE}/leagues?id={LEAGUE_WC}&season={SEASON}",
                 "league.json")
    spain_fixtures = [m for m in league["fixtures"]["allMatches"]
                      if SPAIN_ID in (int(m["home"]["id"]),
                                      int(m["away"]["id"]))]
    spain_fixtures.sort(key=lambda m: m["status"]["utcTime"])
    assert len(spain_fixtures) == 8, "expected 8 Spain matches"

    old = pd.read_csv(DATA / "matches.csv")           # keep scorers text
    match_rows, minutes, goals, assists, ages = [], {}, {}, {}, {}

    for i, fx in enumerate(spain_fixtures):
        detail = get(f"{BASE}/matchDetails?matchId={fx['id']}",
                     f"match_{fx['id']}.json")
        home = detail["general"]["homeTeam"]
        spain_is_home = home["id"] == SPAIN_ID
        idx, opp_idx = (0, 1) if spain_is_home else (1, 0)
        opponent = detail["general"]["awayTeam" if spain_is_home
                                     else "homeTeam"]["name"]
        all_stats = detail["content"]["stats"]["Periods"]["All"]["stats"]
        xg = stat_pair(all_stats, "Expected goals (xG)")
        poss = stat_pair(all_stats, "Ball possession")
        shots = stat_pair(all_stats, "Total shots")
        sot = stat_pair(all_stats, "Shots on target")
        score = [int(x) for x in
                 detail["header"]["status"]["scoreStr"].split(" - ")]
        match_rows.append({
            "match_no": i + 1, "stage": STAGES[i], "opponent": opponent,
            "date": fx["status"]["utcTime"][:10],
            "venue": old.iloc[i]["venue"],
            "gf": score[idx], "ga": score[opp_idx],
            "xg_for": float(xg[idx]), "xg_against": float(xg[opp_idx]),
            "possession": int(poss[idx]),
            "shots": int(shots[idx]), "shots_on_target": int(sot[idx]),
            "scorers": old.iloc[i]["scorers"],
        })

        for pid, p in detail["content"]["playerStats"].items():
            if p.get("teamId") != SPAIN_ID:
                continue
            key = norm(p["name"])
            top = next((g["stats"] for g in p["stats"]
                        if g["title"] == "Top stats"), {})
            def val(name):
                v = top.get(name, {}).get("stat", {}).get("value")
                return float(v) if v not in (None, "") else 0.0
            minutes[key] = minutes.get(key, 0) + val("Minutes played")
            goals[key] = goals.get(key, 0) + val("Goals")
            assists[key] = assists.get(key, 0) + val("Assists")

        for side in ("homeTeam", "awayTeam"):
            team = detail["content"]["lineup"][side]
            if team["id"] != SPAIN_ID:
                continue
            for p in team["starters"] + team["subs"]:
                if p.get("age"):
                    ages[norm(p["name"])] = int(p["age"])

        # the Final's real shotmap
        if STAGES[i] == "Final":
            shot_rows = []
            for s in detail["content"]["shotmap"]["shots"]:
                team = "Spain" if s["teamId"] == SPAIN_ID else "Argentina"
                x, y = float(s["x"]), float(s["y"])
                if team == "Argentina":   # mirror for a two-sided map
                    x, y = 105 - x, 68 - y
                outcome = ("goal" if s["eventType"] == "Goal" else
                           "on_target" if s.get("isOnTarget") else
                           "off_target" if s["eventType"] == "Miss" else
                           "blocked")
                shot_rows.append({"team": team, "minute": int(s["min"]),
                                  "x": round(x, 1), "y": round(y, 1),
                                  "xg": round(float(s["expectedGoals"]), 3),
                                  "outcome": outcome,
                                  "player": s["playerName"]})
            pd.DataFrame(shot_rows).to_csv(DATA / "final_shots.csv",
                                           index=False)
            print(f"final_shots.csv: {len(shot_rows)} real shots")

    matches = pd.DataFrame(match_rows)
    matches.to_csv(DATA / "matches.csv", index=False)
    print(f"matches.csv: real xG {matches.xg_for.sum():.1f}-"
          f"{matches.xg_against.sum():.1f}, "
          f"avg possession {matches.possession.mean():.0f}%")

    players = pd.read_csv(DATA / "players.csv")
    keys = players.player.map(norm)
    players["minutes"] = [int(minutes.get(k, 0)) for k in keys]
    players["goals"] = [int(goals.get(k, 0)) for k in keys]
    players["assists"] = [int(assists.get(k, 0)) for k in keys]
    players["age"] = [ages.get(k, a) for k, a in zip(keys, players.age)]
    players.to_csv(DATA / "players.csv", index=False)
    print("players.csv: real minutes/goals/assists for",
          (players.minutes > 0).sum(), "players; goal total",
          players.goals.sum())

    teams = pd.read_csv(DATA / "teams_comparison.csv")
    sp = teams.team == "Spain"
    teams.loc[sp, ["gf", "ga"]] = [int(matches.gf.sum()), int(matches.ga.sum())]
    teams.loc[sp, "xg_for"] = round(matches.xg_for.sum(), 1)
    teams.loc[sp, "xg_against"] = round(matches.xg_against.sum(), 1)
    teams.loc[sp, "possession_avg"] = int(matches.possession.mean())
    teams.to_csv(DATA / "teams_comparison.csv", index=False)
    print("teams_comparison.csv: Spain row updated with real totals")


if __name__ == "__main__":
    main()
