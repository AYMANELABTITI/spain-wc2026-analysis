# Why Spain Won The 2026 World Cup — A Data Story 🇪🇸🏆

A football analytics report on Spain's victorious FIFA World Cup 2026 campaign,
**generated 100% programmatically in Python** (pandas + matplotlib) from **real
Opta-sourced match data**. One script pulls the data from FotMob's public API,
a second turns it into a designed, magazine-style 15-page PDF — themed after the
World Cup 26 brand (deep navy + the Canada/Mexico/USA tri-colour stripe + trophy
gold) — with a deliberately wide visual vocabulary: touch **heatmaps** built from
7,724 real touch coordinates, an average-position **team-shape map**, **shot maps**
sized by xG, a cumulative **xG race**, **momentum**, **donut** and stacked-zone
charts, percentile **player cards**, radars, steppers, scatters, diverging
butterflies and virtual **tactical-camera** frames, all drawn from scratch on
matplotlib pitches.

> **Data note:** every chart in this report is built from real FotMob (Opta) data —
> per-match xG, possession, shots, passes, tackles, interceptions, touch
> coordinates, full shotmaps, minutes, and tournament-wide rankings across all 48
> teams and 383 players. The only hand-drawn elements are explicitly labelled
> tactical diagrams (the three principle boards and six goal build-up chains),
> which illustrate analysis rather than claim to be measurements.

📄 **Output:** [`output/spain_wc2026_report.pdf`](output/spain_wc2026_report.pdf)

## The story in numbers

| | |
|---|---|
| Matches | 8 — 7 wins, 1 draw, 0 losses |
| Goals | 14 scored, **1 conceded** |
| Clean sheets | 7 of 8 |
| Final | Spain 1–0 Argentina (aet), F. Torres 106' |
| Awards | Golden Ball: Rodri · Golden Glove: U. Simón · Best Young Player: P. Cubarsí |

## Report pages

1. **Title** — campaign at a glance
2. **Tournament Landscape** — the road to the final, cumulative goals, attack–defence balance vs rivals
3. **In Possession** — possession control, chance creation (xG) vs goals, 11 players with a goal involvement
4. **Team Shape & Threat** — average touch positions from 7,724 real touches, real attacking-zone
   split (left/centre/right), territorial dominance, goal-types donut
5. **Goal DNA** — six goal build-up patterns as pass-chain diagrams, beside the real shot map of
   all 140 Spain attempts
6. **Out of Possession I** — the one-goal fortress, conceded-goals ranking, the Final's shot dominance
7. **Out of Possession II — the press** — Spain ranked 1st of 32 for possessions won in the
   attacking third, real PPDA per match, touches in the opposition box
8. **Organisation On The Pitch** — each principle shown twice: analyst plan boards on top and
   **virtual tactical-camera frames** below (a perspective-projected broadcast view rendered in
   matplotlib: grass stripes, depth-scaled players, highlight rings, shaded traps)
9. **The Final Under The Microscope** — shot map with xG-sized markers, the cumulative xG race
   with the red card and the 106' winner annotated, shots per 15-minute window
10. **The Squad** — the Final 4-2-3-1 on a drawn pitch, squad minutes, production vs minutes scatter
11. **Key Players Under The Microscope** — six individual profiles with percentile bars
    (Rodri, Simón, Oyarzabal, Yamal, Cubarsí, Olmo)
12. **Key Players Gallery** — real player photos (CC-licensed) with heatmaps computed from
    each player's real touch coordinates
13. **The One That Got Away** — England, the third-placed heavyweight Spain never met:
    their route, the Kane–Bellingham duo dependency, and a butterfly head-to-head
14. **A Champion In Context** — goals conceded by every World Cup winner 2006–2026
    (Spain's 1 is the modern-era record), and the two-generation age/minutes structure
15. **Identity & Conclusion** — team radar vs beaten rivals, award cards, five reasons Spain won

## How to run

```bash
pip install -r requirements.txt
python scripts/fetch_fotmob.py     # pull real match data (cached after first run)
python src/build_report.py         # render the PDF
```

The PDF is written to `output/spain_wc2026_report.pdf`. The fetch step is optional
on a fresh clone — the CSVs it produces are committed, and the cached FotMob JSON
in `data/fotmob/` makes reruns free.

## Project structure

```
├── data/                          # every file below is written by the fetch script
│   ├── fotmob/                    # raw cached API responses — the audit trail
│   ├── matches.csv                # per-match xG, possession, shots, passes, duels
│   ├── all_shots.csv              # all 140 Spain shots: coords, xG, situation
│   ├── final_shots.csv            # the Final's full shotmap (both teams)
│   ├── final_momentum.csv         # minute-by-minute momentum of the Final
│   ├── player_touches.csv         # 7,724 real touch coordinates
│   ├── player_positions.csv       # average touch position + volume per player
│   ├── players.csv                # minutes, goals, assists, ages
│   ├── player_profiles.csv        # key-player metrics + true position percentiles
│   ├── league_team_stats.csv      # tournament-wide rankings, all 48 teams
│   ├── teams_comparison.csv       # Spain, the sides it beat, and England
│   ├── attacking_zones.csv        # left/centre/right attack split per match
│   ├── goal_types.csv             # goals by FotMob situation tag
│   ├── champions_history.csv      # goals conceded by past winners (FIFA archives)
│   ├── england_matches.csv        # England's route (match reports)
│   └── goal_chains.csv            # the six goal diagrams (tactical reconstruction)
├── scripts/
│   ├── fetch_fotmob.py            # pulls & shapes all real data
│   └── fetch_api_football.py      # optional API-Sports loader (needs a free key)
├── src/
│   ├── config.py                  # visual identity: palette, typography, geometry
│   ├── charts.py                  # reusable chart builders (each draws into an Axes)
│   ├── pages.py                   # page layouts: header bands, commentary, cards
│   └── build_report.py            # entry point: data -> figures -> multi-page PDF
└── output/
    └── spain_wc2026_report.pdf
```

## Data provenance

**All quantitative content is real.** `scripts/fetch_fotmob.py` pulls it from
FotMob's public API (Opta-sourced) and caches every raw JSON response under
`data/fotmob/`, so any number in the report can be traced back to its source:

| Layer | What is real |
|---|---|
| Match metrics | xG for/against (open play and set play split), possession, shots, shots on target, touches in the opposition box, big chances, passes by half, tackles, interceptions |
| Shots | All 140 Spain attempts and both teams' Final shotmaps — true pitch coordinates, per-shot xG, outcome and situation tag |
| Players | Minutes, goals, assists and ages for all 16 players used; 7,724 touch coordinates parsed from FotMob's per-match heatmaps |
| Percentiles | Computed against every WC26 player in the same position group with 180+ minutes (383-player feeds) |
| Tournament context | Team rankings across all 48 teams — including possessions won in the attacking third, where Spain finished 1st of the 32 ranked sides |
| The Final | Minute-by-minute momentum, cumulative xG, shot timings |

Two categories are *not* measurements, and both say so on the page:

- **Tactical diagrams** — the three principle boards, the tactical-camera frames and
  the six goal build-up chains. These illustrate analysis (how the press was
  structured, how a goal was built) the way a coach's whiteboard does. Pass-by-pass
  event chains are not available from any public source.
- **Editorial facts** — the route, awards, Final XI, red card and England's results,
  from [FIFA](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/final),
  [ESPN](https://www.espn.com/soccer/match/_/gameId/760517/argentina-spain),
  [Sports Illustrated](https://www.si.com/soccer/spain-vs-argentina-confirmed-lineups-2026-world-cup-final)
  and [Yahoo Sports](https://sports.yahoo.com/articles/no-yamal-golden-ball-boot-225800390.html).

### What the real data changed

Working from measurements rather than assumptions overturned three things an
earlier draft of this report had guessed at — a useful reminder of why provenance
matters:

- Spain were **not** a left-sided team. The real attacking-zone split is 37% left,
  36% right, 27% centre: two-footed, and re-weighted per opponent.
- **Pau Cubarsí is not a high-volume defender** (25th percentile for interceptions
  among centre-backs). Spain's defence worked by denying the ball, not by winning
  tackles — he took 854 touches, more than any other defender in the squad.
- The Final was even more one-sided than reported: **20-2 on shots and 12-0 on
  target**, with Argentina's first attempt arriving in the 117th minute.

## Designed cover

If `assets/cover_page.pdf` exists (a cover designed outside the pipeline —
Figma, InDesign, Canva…), the build stitches it in as page 1 with `pypdf`,
auto-rotating a portrait canvas that holds landscape artwork, and skips the
generated title page. Delete the file to fall back to the matplotlib cover.

## Plugging in real API data

`scripts/fetch_api_football.py` pulls Spain's real WC26 fixtures and match
statistics from [API-Football](https://www.api-football.com/) (see their
[World Cup 2026 data guide](https://www.api-football.com/news/post/fifa-world-cup-2026-guide-to-using-data-with-api-sports)).
With a free API key in `API_FOOTBALL_KEY`, it caches raw JSON under `data/api/`
and writes `data/matches_api.csv` for diffing against the estimated layer — the
report pipeline itself never needs to change.

## Assets

`assets/wc26_emblem.png` is the official FIFA World Cup 26™ emblem, sourced from the
[Wikipedia article's media](https://en.wikipedia.org/wiki/File:2026_FIFA_World_Cup_emblem.svg)
and used here solely to identify the tournament in a non-commercial fan analysis.
All trademarks belong to FIFA.

`assets/photos/` contains in-match photographs taken at the WC26 semi-final and
final by **Bryan Berlin**, published on
[Wikimedia Commons](https://commons.wikimedia.org/w/index.php?search=Argentina+v+Spain+19+July+2026)
under **CC BY-SA 4.0** (player portraits are the cropped versions used by the
players' Wikipedia articles). Tactic boards are original drawings. Player heatmaps
are **computed** (2D histogram + gaussian kernel smoothing) from
`data/player_touches.csv` — 7,724 real touch coordinates parsed out of FotMob's
per-match heatmap payloads, one point per touch.

## Design

Layout language (header bands, section navigation, chart + commentary + source line per
panel, percentile player cards) inspired by professional scouting reports in the Sports
Data Campus style; colour theme inspired by the FIFA World Cup 26 host-nation identity.
