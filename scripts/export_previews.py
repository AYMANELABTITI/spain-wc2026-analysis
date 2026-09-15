"""Rasterise the finished report into PNG page previews for the README.

GitHub always renders README.md on a repository's landing page and cannot
display a PDF there, so the next best thing is to embed every page as an
image — the README then *is* the report, with the PDF one click away.

Run:  python scripts/export_previews.py
Out:  docs/preview/page-01.png ... page-15.png
"""

from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "spain_wc2026_report.pdf"
OUT = ROOT / "docs" / "preview"
WIDTH_PX = 1600          # wide enough to read on a laptop, small enough to host


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("page-*.png"):
        old.unlink()

    doc = fitz.open(PDF)
    total = 0
    for i, page in enumerate(doc, start=1):
        zoom = WIDTH_PX / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        path = OUT / f"page-{i:02d}.png"
        pix.save(path)
        total += path.stat().st_size
    doc.close()

    print(f"wrote {len(list(OUT.glob('page-*.png')))} previews to docs/preview/ "
          f"({total / 1_048_576:.1f} MB total)")


if __name__ == "__main__":
    main()
