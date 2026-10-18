"""Example 1: Clean India State & Union Territory Boundary Map.

Demonstrates:
  - Loading authoritative 28 states + 8 UTs (Survey of India sovereign compliance)
  - Applying minimalist 'academic_clean' cartographic theme
  - Exporting a clean vector-grade outline map without clutter
"""

from pathlib import Path
from equal_earth import render_india_map

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_file = OUTPUT_DIR / "01_india_clean_states.png"

print("[*] Generating Clean India State Boundary Map...")
result = render_india_map(
    theme="academic_clean",
    show_labels=False,
    title="India — States & Union Territories (Outline)",
    subtitle="Equal Earth Projection (Central Meridian 78.0°E) · Survey of India Sovereign Boundary",
    output_path=out_file,
    dpi=300
)

print(f"[✓] Successfully generated: {result}")
