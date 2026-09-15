"""Shared visual identity for the report: colors, typography, page geometry."""

from pathlib import Path

import matplotlib as mpl

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

# ---------------------------------------------------------------- palette
SPAIN_RED = "#AA151B"        # flag red — primary accent
DEEP_RED = "#7A1017"         # header bands, dark accents
GOLD = "#C9A227"             # flag gold — secondary accent
DARK = "#22181A"             # body text
GREY = "#8A8384"             # de-emphasised series / opponents
LIGHT_GREY = "#E7E2E0"       # grid lines, empty bar tracks
CREAM = "#FBF8F4"            # page background
WHITE = "#FFFFFF"

# ---------------------------------------------------------------- page geometry (16:9)
PAGE_W, PAGE_H = 13.333, 7.5   # inches
DPI = 200

SERIF = "Georgia"
SANS = "Segoe UI"


def apply_style() -> None:
    """Global matplotlib defaults shared by every figure in the report."""
    mpl.rcParams.update({
        "font.family": SANS,
        "text.color": DARK,
        "axes.edgecolor": GREY,
        "axes.labelcolor": DARK,
        "axes.titlesize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": DARK,
        "ytick.color": DARK,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.facecolor": CREAM,
        "axes.facecolor": "none",
        "savefig.facecolor": CREAM,
    })
