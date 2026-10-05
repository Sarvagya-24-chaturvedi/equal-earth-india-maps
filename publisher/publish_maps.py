"""
Equal Earth Map Publishing Pipeline
===================================
Automated batch generator for high-resolution, publication-ready Equal Earth world maps
featuring the 100% official Survey of India (SOI) sovereign boundary.

Outputs:
  - 300 DPI Print & Web PNGs
  - Lossless Vector SVGs & PDFs
  - Ready-to-deploy GitHub Pages static gallery (index.html)
  - Wikimedia Commons upload metadata and copy-paste templates
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "world_data.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "dist"

# Set matplotlib cache
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".mpl_cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from shapely.geometry import shape


THEMES = {
    "atlas_light": {
        "name": "Classic Atlas (Light)",
        "ocean": "#d8ecf8",
        "land": "#ffffff",
        "land_edge": "#94a3b8",
        "india_fill": "#fef3c7",
        "india_edge": "#d97706",
        "graticule": "#c8deec",
        "text": "#0f172a",
        "ocean_text": "#3f7893",
        "bg": "#ffffff"
    },
    "academic_clean": {
        "name": "Academic Publication (Clean)",
        "ocean": "#f1f5f9",
        "land": "#ffffff",
        "land_edge": "#475569",
        "india_fill": "#ffedd5",
        "india_edge": "#ea580c",
        "graticule": "#e2e8f0",
        "text": "#0f172a",
        "ocean_text": "#64748b",
        "bg": "#ffffff"
    },
    "carto_dark": {
        "name": "Cartographic Dark",
        "ocean": "#0f172a",
        "land": "#1e293b",
        "land_edge": "#334155",
        "india_fill": "#78350f",
        "india_edge": "#f59e0b",
        "graticule": "#1e293b",
        "text": "#f8fafc",
        "ocean_text": "#38bdf8",
        "bg": "#0b0f19"
    }
}

SERIES_PRESETS = [
    {
        "id": "india_centered",
        "title": "Centered on India (78°E)",
        "center_lon": 78.0,
        "center_lat": 20.0,
        "theme": "atlas_light",
        "description": "Standard official Indian perspective placing India squarely at the central meridian."
    },
    {
        "id": "greenwich_prime",
        "title": "Centered on Prime Meridian (0°)",
        "center_lon": 0.0,
        "center_lat": 0.0,
        "theme": "atlas_light",
        "description": "Standard international 0° meridian view with correct Survey of India boundaries."
    },
    {
        "id": "indo_pacific",
        "title": "Indo-Pacific Centered (90°E)",
        "center_lon": 90.0,
        "center_lat": 15.0,
        "theme": "academic_clean",
        "description": "Optimized for Indo-Pacific geopolitical and maritime analysis."
    },
    {
        "id": "india_dark",
        "title": "India Centered (Dark Cartography)",
        "center_lon": 78.0,
        "center_lat": 20.0,
        "theme": "carto_dark",
        "description": "Modern dark-mode aesthetic for presentations and high-contrast digital displays."
    },
    {
        "id": "pacific_centered",
        "title": "Pacific Centered (150°E)",
        "center_lon": 150.0,
        "center_lat": 0.0,
        "theme": "atlas_light",
        "description": "Pacific-centric projection with unbroken Asian and American landmasses."
    },
    {
        "id": "americas_centered",
        "title": "Americas Centered (-90°W)",
        "center_lon": -90.0,
        "center_lat": 0.0,
        "theme": "atlas_light",
        "description": "Western Hemisphere view showcasing Asian-American connections."
    }
]


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"world_data.json missing at {DATA_PATH}")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def render_map(config, world_data, output_dir):
    theme = THEMES[config["theme"]]
    lon = config["center_lon"]
    title = config["title"]

    fig = plt.figure(figsize=(16, 8), facecolor=theme["bg"])
    ax = plt.axes(projection=ccrs.EqualEarth(central_longitude=lon))
    ax.set_facecolor(theme["ocean"])

    # 1. Base Countries
    for feat in world_data["features"]:
        geom = shape(feat["geometry"])
        name = feat["properties"]["name"]

        if name == "India":
            face = theme["india_fill"]
            edge = theme["india_edge"]
            lw = 1.3
        else:
            face = theme["land"]
            edge = theme["land_edge"]
            lw = 0.45

        ax.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor=face, edgecolor=edge, linewidth=lw)

    # 2. Dotted Disputed Borders (Much lighter than recognised borders)
    for db in world_data.get("dashed_borders", []):
        geom = shape(db["geometry"])
        ax.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor="none",
                          edgecolor="#b0bec5", linewidth=0.9, linestyle=":", alpha=0.9)

    # 3. Oceans
    for ocean in world_data.get("oceans", []):
        pt = ocean["centroid"]
        ax.text(pt[0], pt[1], ocean["label"], transform=ccrs.PlateCarree(),
                fontsize=8.5, fontstyle="italic", color=theme["ocean_text"],
                ha="center", va="center", fontweight="bold", alpha=0.9)

    # 4. BOLD Country Labels (Google Maps format)
    major_countries = {
        "India", "China", "United States", "Brazil", "Russia", "Canada", "Australia",
        "Argentina", "Algeria", "DR Congo", "Saudi Arabia", "Mexico", "Indonesia",
        "South Africa", "Kazakhstan", "Egypt", "France", "Germany", "United Kingdom",
        "Japan", "Somalia", "Cyprus", "UAE", "CAR", "Congo", "Serbia"
    }
    for feat in world_data["features"]:
        name = feat["properties"]["name"]
        if name in major_countries:
            pt = feat["properties"]["centroid"]
            is_india = (name == "India")
            ax.text(pt[0], pt[1], name, transform=ccrs.PlateCarree(),
                    fontsize=8.5 if is_india else 7.5,
                    fontweight="bold",  # BOLD ALL COUNTRIES
                    color=theme["text"], ha="center", va="center",
                    bbox=dict(boxstyle="square,pad=0.12",
                              facecolor=theme["bg"],
                              alpha=0.75, edgecolor="none"))

    # 5. Graticule
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color=theme["graticule"],
                      alpha=0.8, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 8, "color": theme["text"], "alpha": 0.7}
    gl.ylabel_style = {"size": 8, "color": theme["text"], "alpha": 0.7}

    # 6. Title and Official SOI Attribution
    plt.title(f"Equal Earth Projection · {title}\n(Survey of India Official Sovereign Boundaries)",
              fontsize=13, fontweight="bold", color=theme["text"], pad=14)

    fig.text(0.99, 0.015,
             "International Boundary: Survey of India, Govt. of India | Projection: Equal Earth | License: Creative Commons Attribution 4.0 (CC BY 4.0)",
             ha="right", fontsize=7.5, color=theme["text"], alpha=0.7)

    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{config['id']}.png"
    svg_path = output_dir / f"{config['id']}.svg"
    pdf_path = output_dir / f"{config['id']}.pdf"

    # Export high resolution
    plt.savefig(png_path, dpi=300, bbox_inches="tight", facecolor=theme["bg"])
    plt.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=theme["bg"])
    plt.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=theme["bg"])
    plt.close(fig)

    print(f"  [✓] Generated: {config['id']} (PNG 300DPI, SVG, PDF)")
    return {
        "id": config["id"],
        "title": title,
        "description": config["description"],
        "theme": theme["name"],
        "lon": lon,
        "png": png_path.name,
        "svg": svg_path.name,
        "pdf": pdf_path.name
    }


def generate_gallery_html(manifest, output_dir):
    """Build the GitHub Pages gallery website (index.html)."""
    cards_html = ""
    for item in manifest:
        cards_html += f"""
        <div class="map-card">
          <div class="card-img-wrap">
            <img src="{item['png']}" alt="{item['title']}" loading="lazy">
          </div>
          <div class="card-body">
            <h3>{item['title']}</h3>
            <p class="desc">{item['description']}</p>
            <div class="meta-tag">Theme: {item['theme']} · Central Meridian: {item['lon']:+.0f}°</div>
            <div class="download-row">
              <a href="{item['png']}" download class="btn-dl btn-png">PNG (300 DPI)</a>
              <a href="{item['svg']}" download class="btn-dl btn-svg">Vector SVG</a>
              <a href="{item['pdf']}" download class="btn-dl btn-pdf">Vector PDF</a>
            </div>
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Equal Earth World Maps · Official Survey of India Boundary Gallery</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #f97316;
      --primary: #2563eb;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 0 0 60px 0;
    }}
    header {{
      background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
      border-bottom: 1px solid var(--border);
      padding: 48px 24px;
      text-align: center;
    }}
    .badge {{
      display: inline-block;
      background: #431407;
      color: #fed7aa;
      border: 1px solid #c2410c;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 3px 10px;
      border-radius: 999px;
      margin-bottom: 14px;
    }}
    h1 {{ font-size: 32px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 10px; }}
    p.lead {{ font-size: 16px; color: var(--text-muted); max-width: 780px; margin: 0 auto; }}
    .container {{ max-width: 1240px; margin: 40px auto; padding: 0 24px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 28px;
    }}
    .map-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .map-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 24px rgba(0,0,0,0.3);
    }}
    .card-img-wrap {{
      background: #000;
      aspect-ratio: 16 / 9;
      overflow: hidden;
    }}
    .card-img-wrap img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
      transition: transform 0.3s ease;
    }}
    .map-card:hover .card-img-wrap img {{
      transform: scale(1.03);
    }}
    .card-body {{
      padding: 20px;
      display: flex;
      flex-direction: column;
      flex: 1;
    }}
    .card-body h3 {{ font-size: 18px; margin-bottom: 6px; }}
    .desc {{ font-size: 13px; color: var(--text-muted); margin-bottom: 12px; flex: 1; }}
    .meta-tag {{ font-size: 11px; color: #94a3b8; margin-bottom: 16px; font-weight: 500; }}
    .download-row {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .btn-dl {{
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      display: inline-block;
      transition: opacity 0.15s;
    }}
    .btn-dl:hover {{ opacity: 0.85; }}
    .btn-png {{ background: #2563eb; color: #fff; }}
    .btn-svg {{ background: #059669; color: #fff; }}
    .btn-pdf {{ background: #dc2626; color: #fff; }}
    .attribution-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 24px;
      margin-top: 48px;
    }}
    .attribution-card h2 {{ font-size: 20px; margin-bottom: 10px; }}
    code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; font-size: 12px; color: #f97316; }}
    pre {{ background: #0f172a; padding: 14px; border-radius: 8px; font-size: 12px; overflow-x: auto; color: #cbd5e1; margin-top: 10px; }}
  </style>
</head>
<body>

  <header>
    <div class="badge">Survey of India Sovereign Boundary Compliant</div>
    <h1>Equal Earth World Map Publication Gallery</h1>
    <p class="lead">
      Open-source, high-resolution Equal Earth maps created with the official Survey of India boundary.
      Free for academic publication, journalism, digital encyclopedias, and open-source cartography under CC BY 4.0.
    </p>
  </header>

  <div class="container">
    <div class="grid">
      {cards_html}
    </div>

    <div class="attribution-card">
      <h2>Copy-Paste Citation & Attribution</h2>
      <p style="color:var(--text-muted); font-size:13px;">
        All maps in this gallery are released under <strong>Creative Commons Attribution 4.0 International (CC BY 4.0)</strong>.
        You may freely share, republish, adapt, and use them in books, articles, websites, and broadcasts.
      </p>
      <pre>Map Title: Equal Earth Projection (Centered on India / World)
Data Attribution: Survey of India, Government of India (International Boundaries)
Projection: Equal Earth (Bojan Šavrič, Tom Patterson, Bernhard Jenny, 2018)
License: Creative Commons Attribution 4.0 International (CC BY 4.0)</pre>
    </div>
  </div>

</body>
</html>
"""
    gallery_path = output_dir / "index.html"
    with open(gallery_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [✓] Built GitHub Pages gallery: {gallery_path}")


def generate_wikimedia_template(output_dir):
    """Generate ready-to-use Wikimedia Commons template."""
    content = """== {{int:filedesc}} ==
{{Information
|description    = {{en|1=Equal Earth projection world map centered on India (78°E) featuring the 100% official international sovereign boundary of India as recognized and published by the Survey of India (Department of Science and Technology, Government of India), including the complete Union Territories of Jammu & Kashmir and Ladakh (including PoK and Aksai Chin) and the state of Arunachal Pradesh.}}
|date           = 2026
|source         = {{own}}, using official Survey of India sovereign boundary vector shapefiles and Natural Earth datasets.
|author         = Sarvagya Chaturvedi
|permission     = {{CC-BY-4.0}}
|other_versions = Available in SVG, PDF, and high-resolution PNG on GitHub Pages.
}}

== {{int:license-header}} ==
{{CC-BY-4.0}}
{{Survey of India}}

[[Category:Equal Earth projection]]
[[Category:Maps of the world with Survey of India boundaries]]
[[Category:Maps of India with official borders]]
[[Category:SVG maps of the world]]
"""
    tmpl_path = output_dir / "wikimedia_commons_upload_template.txt"
    with open(tmpl_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [✓] Generated Wikimedia Commons upload template: {tmpl_path}")


def main():
    print("=" * 68)
    print(" EQUAL EARTH BATCH PUBLISHING PIPELINE (SOI OFFICIAL BOUNDARY)")
    print("=" * 68)

    world_data = load_dataset()
    manifest = []

    print("[*] Generating publication-grade maps (PNG 300DPI, SVG, PDF)...")
    for preset in SERIES_PRESETS:
        result = render_map(preset, world_data, OUTPUT_DIR)
        manifest.append(result)

    print("\n[*] Assembling GitHub Pages gallery...")
    generate_gallery_html(manifest, OUTPUT_DIR)
    generate_wikimedia_template(OUTPUT_DIR)

    print("\n" + "=" * 68)
    print(f"[✓] PUBLISHING SUITE GENERATION COMPLETE!")
    print(f"All artifacts saved in: {OUTPUT_DIR}")
    print("=" * 68)


if __name__ == "__main__":
    main()
