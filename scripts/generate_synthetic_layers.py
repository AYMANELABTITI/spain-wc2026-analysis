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

# ----------------------------------------------------------------- the Final
# Shot-by-shot layer for the Final consistent with the reported aggregates:
# Spain 20 shots / 8 on target / ~2.4 xG, F. Torres goal 106'; Argentina
# 3 shots / 1 on target / ~0.2 xG. Spain attacks left->right (x high).
shot_rows = []
esp_minutes = sorted(rng.choice(np.arange(4, 120), size=19, replace=False))
esp_on_target = set(rng.choice(19, size=7, replace=False))
for i, m in enumerate(esp_minutes):
    x = np.clip(rng.normal(93, 6), 78, 104)
    y = np.clip(rng.normal(34, 9), 12, 56)
    dist = np.hypot(105 - x, 34 - y)
    xg = float(np.clip(0.32 * np.exp(-dist / 9) + rng.uniform(0.01, 0.05),
                       0.02, 0.45))
    out = "on_target" if i in esp_on_target else \
        rng.choice(["off_target", "blocked"], p=[0.6, 0.4])
    shot_rows.append(("Spain", int(m), round(x, 1), round(y, 1),
                      round(xg, 2), out))
shot_rows.append(("Spain", 106, 96.5, 37.0, 0.31, "goal"))
for m, out in [(38, "off_target"), (57, "on_target"), (78, "off_target")]:
    x = np.clip(rng.normal(14, 5), 4, 25)
    y = np.clip(rng.normal(34, 8), 18, 50)
    shot_rows.append(("Argentina", m, round(x, 1), round(y, 1),
                      round(float(rng.uniform(0.04, 0.09)), 2), out))

shots_df = pd.DataFrame(shot_rows,
                        columns=["team", "minute", "x", "y", "xg", "outcome"])
shots_df.to_csv(DATA / "final_shots.csv", index=False)
print(f"wrote {len(shots_df)} shots -> data/final_shots.csv "
      f"(Spain xG {shots_df[shots_df.team == 'Spain'].xg.sum():.2f})")
