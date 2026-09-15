# Why Spain Won The 2026 World Cup — A Data Story 🇪🇸🏆

A football analytics report on Spain's victorious FIFA World Cup 2026 campaign,
**generated 100% programmatically in Python** (pandas + matplotlib). Running one
script turns three small CSV datasets into a designed, magazine-style 5-page PDF
report — charts, layout, typography and commentary included.

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
3. **In Possession** — possession control, chance creation (xG) vs goals, scorer distribution
4. **Out of Possession** — the one-goal fortress, conceded-goals ranking, the Final's shot dominance
5. **Identity & Key Players** — team radar vs beaten rivals, award cards, five reasons Spain won

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
│   └── players.csv            # key player contributions & awards
├── src/
│   ├── config.py              # visual identity: palette, typography, page geometry
│   ├── charts.py              # reusable chart builders (each draws into an Axes)
│   ├── pages.py               # page layouts: header bands, commentary, stat cards
│   └── build_report.py        # entry point: data -> figures -> multi-page PDF
└── output/
    └── spain_wc2026_report.pdf
```

## Data provenance

- **Verified facts** (results, scorers, route, awards, final shot counts) are compiled
  from public reporting: [FIFA](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/final),
  [ESPN](https://www.espn.com/soccer/match/_/gameId/760517/argentina-spain),
  [CBS News](https://www.cbsnews.com/news/2026-fifa-world-cup-final-spain-argentina-sunday/) and
  [Striker Report](https://strikerreport.com/every-spain-match-fifa-world-cup-2026-results/).
- **Advanced metrics** (per-match xG, possession shares) are *estimates* reconstructed
  from public match reports, clearly labelled "(est.)" in the report. The pipeline is
  data-source-agnostic: swap the CSVs for provider data (Opta, StatsBomb, FBref) and
  rebuild.

## Design

Layout language (deep-red header bands, section navigation, chart + commentary + source
line per panel) inspired by professional scouting reports in the Sports Data Campus style.
