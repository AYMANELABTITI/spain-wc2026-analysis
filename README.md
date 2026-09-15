# Why Spain Won The 2026 World Cup — A Data Story 🇪🇸🏆

A football analytics report on Spain's victorious FIFA World Cup 2026 campaign,
**generated 100% programmatically in Python** (pandas + matplotlib). Running one
script turns four small CSV datasets into a designed, magazine-style 7-page PDF
report — charts, layout, typography and commentary included — themed after the
World Cup 26 brand (deep navy + the Canada/Mexico/USA tri-colour stripe + trophy gold).

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
4. **Out of Possession** — the one-goal fortress, conceded-goals ranking, the Final's shot dominance
5. **The Squad** — the Final 4-2-3-1 on a drawn pitch, squad minutes, production vs minutes scatter
6. **Key Players Under The Microscope** — six individual profiles with percentile bars
   (Rodri, Simón, Oyarzabal, Yamal, Cubarsí, Olmo)
7. **Identity & Conclusion** — team radar vs beaten rivals, award cards, five reasons Spain won

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
│   ├── teams_comparison.csv   # Spain vs the rivals it eliminated
│   ├── players.csv            # squad: minutes, goals, assists, final starters, awards
│   └── player_profiles.csv    # per-player metric profiles for the percentile cards
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

## Design

Layout language (header bands, section navigation, chart + commentary + source line per
panel, percentile player cards) inspired by professional scouting reports in the Sports
Data Campus style; colour theme inspired by the FIFA World Cup 26 host-nation identity.
