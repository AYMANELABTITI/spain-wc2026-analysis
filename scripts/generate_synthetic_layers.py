"""Generate the illustrative event-level layer: high-turnover regain locations.

True event data for WC26 is not public, so this seeded generator produces a
plausible spatial distribution of Spain's high regains (recoveries in the last
40 m of the pitch), consistent with the aggregate estimates used in the report:
~71 high regains, 19 leading to a shot within 15 s, 5 leading to a goal.

Run once; the CSV is committed so the report build stays deterministic.
"""

import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(2026)
DATA = Path(__file__).resolve().parents[1] / "data"

N = 71
# pitch: x 0-105 (attacking ->), y 0-68 ; high regain zone = x >= 65
x = np.clip(rng.normal(80, 8.5, N), 65, 103)
y = np.clip(rng.normal(34, 15, N), 3, 65)

outcome = np.array(["regain"] * N, dtype=object)
idx = rng.choice(N, size=19, replace=False)   # shot within 15 s
outcome[idx] = "shot"
goal_idx = rng.choice(idx, size=5, replace=False)  # of which goals
outcome[goal_idx] = "goal"

df = pd.DataFrame({"x": x.round(1), "y": y.round(1), "outcome": outcome})
df.to_csv(DATA / "high_regains.csv", index=False)
print(f"wrote {len(df)} regains -> data/high_regains.csv "
      f"({(outcome=='shot').sum()} shots, {(outcome=='goal').sum()} goals)")

# ----------------------------------------------------------------- touches
# Per-player touch events for the gallery heatmaps. Mixture centres encode
# each player's role (105x68 pitch, attacking ->); the heatmap chart then
# computes a density from these points — nothing is drawn by hand.
TOUCH_MODEL = {
    "rodri": [(48, 34, .5, 13, 10), (60, 30, .3, 11, 9), (38, 40, .2, 10, 8)],
    "yamal": [(78, 11, .45, 10, 6), (88, 20, .25, 7, 7), (60, 14, .2, 11, 7),
              (70, 30, .1, 8, 8)],
    "oyarzabal": [(88, 32, .4, 8, 8), (72, 22, .25, 10, 8), (80, 45, .2, 8, 7),
                  (60, 30, .15, 9, 8)],
    "simon": [(5, 34, .7, 4, 8), (14, 34, .3, 7, 11)],
    "cubarsi": [(26, 23, .5, 10, 8), (40, 27, .3, 9, 8), (55, 30, .2, 8, 7)],
    "olmo": [(68, 38, .35, 9, 8), (77, 26, .3, 8, 7), (58, 44, .2, 9, 8),
             (85, 38, .15, 6, 6)],
}

rows = []
for player, mix in TOUCH_MODEL.items():
    n_pts = 420
    weights = np.array([m[2] for m in mix])
    weights /= weights.sum()
    comp = rng.choice(len(mix), size=n_pts, p=weights)
    for c in comp:
        cx, cy, _, sx, sy = mix[c]
        px = np.clip(rng.normal(cx, sx), 0.5, 104.5)
        py = np.clip(rng.normal(cy, sy), 0.5, 67.5)
        rows.append((player, round(px, 1), round(py, 1)))

touches = pd.DataFrame(rows, columns=["player", "x", "y"])
touches.to_csv(DATA / "touch_points.csv", index=False)
print(f"wrote {len(touches)} touches -> data/touch_points.csv "
      f"({len(TOUCH_MODEL)} players)")

# NOTE: data/final_shots.csv is REAL provider data (FotMob shotmap) written by
# scripts/fetch_fotmob.py — it is deliberately not generated here.
