# Why Spain Won The 2026 World Cup — A Data Story 🇪🇸🏆

A football analytics report on Spain's victorious FIFA World Cup 2026 campaign,
**generated 100% programmatically in Python** (pandas + matplotlib). Running one
script turns nine small CSV datasets into a designed, magazine-style 9-page PDF
report — themed after the World Cup 26 brand (deep navy + the Canada/Mexico/USA
tri-colour stripe + trophy gold) — with a deliberately wide visual vocabulary:
zonal pressing **heatmaps**, a **passing-network graph**, pitch maps of **high
regains** and **line heights**, **donut** charts, percentile **player cards**,
radars, steppers, scatters and comparative bars, all drawn from scratch on
matplotlib pitches.

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
4. **Structure & Networks** — Final-XI passing network, defensive/midfield line heights on a pitch,
   line discipline per match, goal-types donut
5. **Goal DNA** — six goal build-up patterns drawn as pass-chain mini pitches, plus a real
   celebration photo
6. **Out of Possession I** — the one-goal fortress, conceded-goals ranking, the Final's shot dominance
7. **Out of Possession II — the press** — zonal heatmap of defensive actions, high-regains pitch map
   (71 regains → 19 shots → 5 goals), PPDA comparison
8. **Organisation On The Pitch** — three tactic-board reconstructions (3-2-5 build, curve press,
   5-second counter-press) alongside real match photos
9. **The Squad** — the Final 4-2-3-1 on a drawn pitch, squad minutes, production vs minutes scatter
10. **Key Players Under The Microscope** — six individual profiles with percentile bars
    (Rodri, Simón, Oyarzabal, Yamal, Cubarsí, Olmo)
11. **Key Players Gallery** — real player photos (CC-licensed) with modelled positional heatmaps
12. **The One That Got Away** — England, the third-placed heavyweight Spain never met:
    their route, the Kane–Bellingham duo dependency, and a butterfly head-to-head
13. **Identity & Conclusion** — team radar vs beaten rivals, award cards, five reasons Spain won

## How to run

```bash
pip install -r requirements.txt
python src/build_report.py
```

The PDF is written to `output/spain_wc2026_report.pdf`.

## Project structure

```
├── data/
│   ├── matches.csv            # Spain's 8 matches: scores, scorers, per-match metrics
│   ├── teams_comparison.csv   # Spain vs the rivals it eliminated (incl. PPDA)
│   ├── players.csv            # squad: minutes, goals, assists, final starters, awards
│   ├── player_profiles.csv    # per-player metric profiles for the percentile cards
│   ├── pass_network.csv       # Final-XI pass combinations for the network graph
│   ├── line_heights.csv       # defensive & midfield line height per match
│   ├── goal_types.csv         # how the 14 goals were scored
│   ├── pressing_zones.csv     # defensive actions per pitch zone (heatmap)
│   ├── high_regains.csv       # regain locations + outcomes (synthetic layer)
│   └── england_matches.csv    # England's route — the strongest side Spain avoided
├── scripts/
│   └── generate_synthetic_layers.py  # seeded generator for the event-level layer
├── src/
│   ├── config.py              # visual identity: palette, typography, page geometry
│   ├── charts.py              # reusable chart builders (each draws into an Axes)
│   ├── pages.py               # page layouts: header bands, commentary, stat cards
│   └── build_report.py        # entry point: data -> figures -> multi-page PDF
└── output/
    └── spain_wc2026_report.pdf
```

## Data provenance

- **Verified facts** (results, scorers, route, awards, final shot counts, the Final XI)
  are compiled from public reporting: [FIFA](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/final),
  [ESPN](https://www.espn.com/soccer/match/_/gameId/760517/argentina-spain),
  [CBS News](https://www.cbsnews.com/news/2026-fifa-world-cup-final-spain-argentina-sunday/),
  [Striker Report](https://strikerreport.com/every-spain-match-fifa-world-cup-2026-results/),
  [Sports Illustrated — confirmed Final lineups](https://www.si.com/soccer/spain-vs-argentina-confirmed-lineups-2026-world-cup-final) and
  [Yahoo Sports — individual awards](https://sports.yahoo.com/articles/no-yamal-golden-ball-boot-225800390.html).
- **Advanced metrics** (per-match xG, possession shares, minutes, percentile profiles)
  are *estimates* reconstructed from public match reports, clearly labelled "(est.)"
  in the report. The pipeline is data-source-agnostic: swap the CSVs for provider data
  (Opta, StatsBomb, FBref) and rebuild.

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
`data/touch_points.csv`, a modelled touch-event dataset produced by the seeded
generator in `scripts/` — real tracking data for WC26 is not publicly available,
so the pipeline is written to be pointed at provider event data when you have it.

## Design

Layout language (header bands, section navigation, chart + commentary + source line per
panel, percentile player cards) inspired by professional scouting reports in the Sports
Data Campus style; colour theme inspired by the FIFA World Cup 26 host-nation identity.
