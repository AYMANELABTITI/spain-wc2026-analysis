"""Pull real FIFA World Cup 2026 data from API-Football (api-sports.io).

The report builds from CSVs in data/, several of which are estimated layers.
This script replaces those estimates with real API data when you have a key:

    1. Create a free account at https://www.api-football.com/  (100 req/day)
    2. Set the key:   $env:API_FOOTBALL_KEY = "your-key"      (PowerShell)
    3. Run:           python scripts/fetch_api_football.py

Raw JSON responses are cached under data/api/ so repeated runs cost no quota,
and a refreshed matches.csv is written next to the estimated one for diffing.
World Cup = league id 1; Spain = team id 9 in the API-Football catalogue.
See: https://www.api-football.com/news/post/fifa-world-cup-2026-guide-to-using-data-with-api-sports
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

BASE = "https://v3.football.api-sports.io"
LEAGUE_WORLD_CUP, SEASON, TEAM_SPAIN = 1, 2026, 9

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "api"


def call(endpoint: str, **params) -> dict:
    """GET an endpoint with caching (one JSON file per unique call)."""
    key = os.environ.get("API_FOOTBALL_KEY")
    if not key:
        sys.exit("Set API_FOOTBALL_KEY first — see the docstring.")
    qs = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    cache_file = CACHE / f"{endpoint.strip('/').replace('/', '_')}_{qs}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    req = urllib.request.Request(f"{BASE}/{endpoint}?{qs}",
                                 headers={"x-apisports-key": key})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("errors"):
        sys.exit(f"API error: {payload['errors']}")
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    return payload


def main() -> None:
    import pandas as pd

    fixtures = call("fixtures", league=LEAGUE_WORLD_CUP, season=SEASON,
                    team=TEAM_SPAIN)["response"]
    rows = []
    for f in sorted(fixtures, key=lambda f: f["fixture"]["date"]):
        home = f["teams"]["home"]["name"] == "Spain"
        opp = f["teams"]["away" if home else "home"]["name"]
        gf = f["goals"]["home" if home else "away"]
        ga = f["goals"]["away" if home else "home"]
        stats = call("fixtures/statistics", fixture=f["fixture"]["id"],
                     team=TEAM_SPAIN)["response"]
        by_name = {s["type"]: s["value"]
                   for s in (stats[0]["statistics"] if stats else [])}
        rows.append({
            "stage": f["league"]["round"], "opponent": opp,
            "date": f["fixture"]["date"][:10], "gf": gf, "ga": ga,
            "xg_for": by_name.get("expected_goals"),
            "possession": str(by_name.get("Ball Possession", "")).rstrip("%"),
            "shots": by_name.get("Total Shots"),
            "shots_on_target": by_name.get("Shots on Goal"),
        })
    out = ROOT / "data" / "matches_api.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {len(rows)} fixtures -> {out}")
    print("Review the diff vs data/matches.csv, then replace the estimated "
          "columns you trust the API for.")


if __name__ == "__main__":
    main()
