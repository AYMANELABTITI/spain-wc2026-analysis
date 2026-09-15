"""Entry point: load the data, render every page, write the PDF.

Usage:  python src/build_report.py
Output: output/spain_wc2026_report.pdf
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from config import DATA_DIR, OUTPUT_DIR, apply_style
from pages import PAGES


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "matches": pd.read_csv(DATA_DIR / "matches.csv"),
        "teams": pd.read_csv(DATA_DIR / "teams_comparison.csv"),
        "players": pd.read_csv(DATA_DIR / "players.csv"),
        "profiles": pd.read_csv(DATA_DIR / "player_profiles.csv"),
        "network": pd.read_csv(DATA_DIR / "pass_network.csv"),
        "lines": pd.read_csv(DATA_DIR / "line_heights.csv"),
        "goal_types": pd.read_csv(DATA_DIR / "goal_types.csv"),
        "press_zones": pd.read_csv(DATA_DIR / "pressing_zones.csv"),
        "regains": pd.read_csv(DATA_DIR / "high_regains.csv"),
        "england": pd.read_csv(DATA_DIR / "england_matches.csv"),
        "chains": pd.read_csv(DATA_DIR / "goal_chains.csv"),
        "touches": pd.read_csv(DATA_DIR / "touch_points.csv"),
    }


def main() -> None:
    apply_style()
    data = load_data()
    OUTPUT_DIR.mkdir(exist_ok=True)
    out = OUTPUT_DIR / "spain_wc2026_report.pdf"

    with PdfPages(out) as pdf:
        for build in PAGES:
            fig = build(data)
            pdf.savefig(fig)
            plt.close(fig)
        meta = pdf.infodict()
        meta["Title"] = "Why Spain Won The 2026 World Cup — A Data Story"
        meta["Author"] = "Aymane Labtiti"
        meta["Subject"] = "Football analytics report generated with Python"

    print(f"Report written to {out}")


if __name__ == "__main__":
    main()
