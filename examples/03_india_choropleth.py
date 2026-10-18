"""Example 3: Data-Driven Choropleth Map (State-wise Literacy Rate).

Demonstrates:
  - Loading official 2011 Census of India literacy dataset
  - Automating state name normalization and 100% boundary matching
  - Generating discrete color classification intervals and publication legend
"""

from pathlib import Path
from equal_earth import (
    load_sample_dataset,
    generate_choropleth,
    render_india_map,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_file = OUTPUT_DIR / "03_india_literacy_choropleth.png"

print("[*] Loading Census 2011 Literacy Dataset...")
data = load_sample_dataset("literacy")

print("[*] Classifying data into YlGnBu intervals...")
choro = generate_choropleth(data, palette="YlGnBu", num_classes=5)
print(f"    Matched: {choro.matched_count}/36 states (Min: {choro.min_value}%, Max: {choro.max_value}%)")

print("[*] Rendering Choropleth Map...")
result = render_india_map(
    choropleth=choro,
    show_labels=True,
    title="India — Literacy Rate by State & Union Territory",
    subtitle="Census of India 2011 · Equal Earth Projection",
    source_note="Source: Office of the Registrar General & Census Commissioner, India (2011)",
    legend_title="Literacy Rate (%)",
    unit="%",
    output_path=out_file,
    dpi=300
)

print(f"[✓] Successfully generated: {result}")
