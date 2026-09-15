"""Entry point: load the data, render every page, write the PDF.

Usage:  python src/build_report.py
Output: output/spain_wc2026_report.pdf

If assets/cover_page.pdf exists (a designed cover, e.g. from Figma/InDesign),
it replaces the generated title page: the matplotlib pages are rendered to a
temporary body PDF and the cover is stitched in front with pypdf.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from config import ASSETS_DIR, DATA_DIR, OUTPUT_DIR, apply_style
from pages import PAGES

COVER = ASSETS_DIR / "cover_page.pdf"
TITLE = "Why Spain Won The 2026 World Cup — A Data Story"
AUTHOR = "Aymane Labtiti"


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
        "final_shots": pd.read_csv(DATA_DIR / "final_shots.csv"),
        "history": pd.read_csv(DATA_DIR / "champions_history.csv"),
    }


def render_pages(pages, data, path) -> None:
    with PdfPages(path) as pdf:
        for build in pages:
            fig = build(data)
            pdf.savefig(fig)
            plt.close(fig)
        meta = pdf.infodict()
        meta["Title"] = TITLE
        meta["Author"] = AUTHOR
        meta["Subject"] = "Football analytics report generated with Python"


def main() -> None:
    apply_style()
    data = load_data()
    OUTPUT_DIR.mkdir(exist_ok=True)
    out = OUTPUT_DIR / "spain_wc2026_report.pdf"

    if not COVER.exists():
        render_pages(PAGES, data, out)
        print(f"Report written to {out}")
        return

    # designed cover replaces the generated title page
    from pypdf import PdfReader, PdfWriter, Transformation

    body = OUTPUT_DIR / "_body.pdf"
    render_pages(PAGES[1:], data, body)

    writer = PdfWriter()
    cover_page = PdfReader(COVER).pages[0]
    pw, ph = float(cover_page.mediabox.width), float(cover_page.mediabox.height)
    target_w, target_h = 960.0, 540.0   # 13.33in x 7.5in — the report page size
    target = writer.add_blank_page(width=target_w, height=target_h)
    if pw < ph:
        # portrait canvas holding rotated 16:9 artwork, centred with white
        # bars: rotate it upright, scale to full width, crop the bars away
        s = target_w / ph
        overflow = (pw * s - target_h) / 2
        t = (Transformation().rotate(-90).translate(0, pw)
             .scale(s).translate(0, -overflow))
    else:
        t = Transformation().scale(target_w / pw, target_h / ph)
    target.merge_transformed_page(cover_page, t)
    for page in PdfReader(body).pages:
        writer.add_page(page)
    writer.add_metadata({"/Title": TITLE, "/Author": AUTHOR,
                         "/Subject": "Football analytics report generated with Python"})
    with open(out, "wb") as fh:
        writer.write(fh)
    body.unlink()
    print(f"Report written to {out} (designed cover + {len(PAGES) - 1} generated pages)")


if __name__ == "__main__":
    main()
