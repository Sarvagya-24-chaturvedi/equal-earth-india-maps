"""Example 2: Publication-Ready Labeled India Map.

Demonstrates:
  - Classic Atlas styling with subtle ocean tint and gold sovereign border
  - Precise centroid state label placement with background halos
  - High-resolution 300 DPI raster export
"""

from pathlib import Path
from equal_earth import render_india_map

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_file = OUTPUT_DIR / "02_india_publication_labeled.png"

print("[*] Generating Publication-Ready Labeled India Map...")
result = render_india_map(
    theme="atlas_light",
    show_labels=True,
    title="Republic of India — Administrative Divisions",
    subtitle="Equal Earth Projection · Survey of India Sovereign Boundary (28 States & 8 UTs)",
    source_note="Source: Survey of India Official Administrative Alignments (Post-2019 Reorganization)",
    output_path=out_file,
    dpi=300
)

print(f"[✓] Successfully generated: {result}")
