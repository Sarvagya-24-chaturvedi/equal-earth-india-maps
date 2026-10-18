"""Example 5: High-Resolution Multi-Format Export Pipeline.

Demonstrates:
  - Ultra-high resolution 600 DPI publication raster PNG
  - Lossless vector SVG for interactive web integration
  - Publication-ready vector PDF for academic print and report inclusion
"""

from pathlib import Path
from equal_earth import render_india_map

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

png_path = OUTPUT_DIR / "05_india_ultra_hd_600dpi.png"
svg_path = OUTPUT_DIR / "05_india_vector.svg"
pdf_path = OUTPUT_DIR / "05_india_publication.pdf"

print("[1/3] Exporting 600 DPI Ultra-HD Raster PNG...")
render_india_map(
    theme="atlas_light",
    title="Republic of India (600 DPI Ultra High Resolution)",
    output_path=png_path,
    dpi=600
)
print(f"      Saved: {png_path} ({png_path.stat().st_size / (1024*1024):.2f} MB)")

print("[2/3] Exporting Lossless Vector SVG...")
render_india_map(
    theme="academic_clean",
    title="Republic of India (Lossless Vector SVG)",
    output_path=svg_path
)
print(f"      Saved: {svg_path} ({svg_path.stat().st_size / 1024:.1f} KB)")

print("[3/3] Exporting Publication Vector PDF...")
render_india_map(
    theme="academic_clean",
    title="Republic of India (Vector PDF)",
    output_path=pdf_path
)
print(f"      Saved: {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")

print("[✓] All multi-format exports completed successfully!")
