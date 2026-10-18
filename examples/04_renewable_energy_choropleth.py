"""Example 4: State-Level Energy & Environmental Visualization (Renewable Energy Capacity).

Demonstrates:
  - Official Ministry of New and Renewable Energy (MNRE 2023) data mapping
  - Viridis sequential palette for continuous capacity gradients
  - Custom figure dimensions and units (MW)
"""

from pathlib import Path
from equal_earth import (
    load_sample_dataset,
    generate_choropleth,
    render_india_map,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_file = OUTPUT_DIR / "04_india_renewable_energy.png"

print("[*] Loading MNRE 2023 Renewable Energy Dataset...")
data = load_sample_dataset("renewable_energy")

print("[*] Generating classification with Viridis palette...")
choro = generate_choropleth(data, palette="Viridis", num_classes=5)

print("[*] Rendering Renewable Energy Distribution Map...")
result = render_india_map(
    choropleth=choro,
    theme="carto_dark",
    show_labels=True,
    title="India — Renewable Energy Installed Capacity by State",
    subtitle="Solar, Wind, Biomass, & Small Hydro · Grid-Interactive Power (MNRE 2023)",
    source_note="Source: Ministry of New and Renewable Energy & Central Electricity Authority (2023)",
    legend_title="Installed Capacity (MW)",
    unit="MW",
    output_path=out_file,
    dpi=300
)

print(f"[✓] Successfully generated: {result}")
