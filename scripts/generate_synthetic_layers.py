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
