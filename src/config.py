"""Shared visual identity for the report: FIFA World Cup 26 inspired theme.

Palette logic — deep navy base with the tri-host accent colours
(Canada red / Mexico green / USA blue) and trophy gold.
"""

from pathlib import Path

import matplotlib as mpl

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets"
OUTPUT_DIR = ROOT / "output"

# ---------------------------------------------------------------- WC26 palette
NAVY = "#0B1F3A"             # header/footer bands, dark base
NAVY_DEEP = "#071426"        # title page gradient end
WC_RED = "#D50032"           # Canada red — primary accent (and Spain highlight)
WC_GREEN = "#007A33"         # Mexico green — secondary accent
WC_BLUE = "#0057B8"          # USA blue — tertiary accent
GOLD = "#C9A227"             # trophy gold
DARK = "#1C2431"             # body text
GREY = "#8A8F98"             # de-emphasised series / opponents
LIGHT_GREY = "#E4E6EA"       # grid lines, empty bar tracks
CREAM = "#F7F8FA"            # page background (cool off-white)
WHITE = "#FFFFFF"

TRI = [WC_RED, WC_GREEN, WC_BLUE]   # the host-nation stripe

# Backwards-compatible aliases used across chart code
SPAIN_RED = WC_RED
DEEP_RED = NAVY

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
