"""
Equal Earth Map Generator & Interactive Viewer (Google Maps Format)
===================================================================
- Survey of India (SOI) 100% official sovereign boundary for India
- Somaliland merged into Somalia; Northern Cyprus & military bases merged into Cyprus
- Foreign bases (Baykonur, Akrotiri, Dhekelia, Guantanamo) & Brazilian Island removed/merged
- Disputed borders shown as light, delicate dotted lines (much lighter than recognized borders)
- ALL country names bolded (Google Maps typography)
- Short names and acronyms used (e.g., USA, UAE, CAR, DR Congo, Bosnia & Herz., Dominican Rep.)
- Sovereign countries strictly prioritized over dependencies when zoomed out
- All Oceans labeled with ability to center map around them
- Dynamic Google Maps-style label scaling (no giant fonts on zoom)
- 100% offline & self-contained
"""

import os
import sys
import json
import argparse
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "world_data.json"
D3_PATH = BASE_DIR / "d3.v7.min.js"
HTML_OUTPUT = BASE_DIR / "equal_earth_interactive.html"

os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".mpl_cache"))


def load_world_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"world_data.json not found at {DATA_PATH}.")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_entity(query, world_data):
    """Search for country, micronation, or ocean with exact match priority."""
    query_clean = query.strip().lower()

    # 1. Exact match check (Country / Micronation)
    for feat in world_data["features"]:
        props = feat["properties"]
        if query_clean == props["name"].lower() or query_clean in (props.get("iso_a2", "").lower(), props.get("iso_a3", "").lower()):
            return feat

    # 2. Exact match check (Ocean)
    for ocean in world_data.get("oceans", []):
        if query_clean == ocean["name"].lower():
            return {
                "type": "Ocean",
                "properties": {
                    "name": ocean["name"],
                    "centroid": ocean["centroid"],
                    "wiki": ocean["wiki"],
                    "is_ocean": True
                }
            }

    # 3. Substring match (Ocean)
    for ocean in world_data.get("oceans", []):
        if query_clean in ocean["name"].lower():
            return {
                "type": "Ocean",
                "properties": {
                    "name": ocean["name"],
                    "centroid": ocean["centroid"],
                    "wiki": ocean["wiki"],
                    "is_ocean": True
                }
            }

    # 4. Substring match (Country)
    for feat in world_data["features"]:
        if query_clean in feat["properties"]["name"].lower():
            return feat

    return None


def build_interactive_html(initial_lon=0.0, initial_lat=0.0, initial_target="World", mode="natural"):
    """Build the self-contained interactive Equal Earth web application."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        geojson_str = f.read()

    d3_script_tag = """
    <script src="d3.v7.min.js"></script>
    <script>
      if (typeof d3 === 'undefined') {
        document.write('<script src="https://d3js.org/d3.v7.min.js"><\\/script>');
      }
    </script>
    """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Equal Earth Map · Google Maps Format (Light Mode)</title>
  {d3_script_tag}
  <style>
    :root {{
      --bg-ocean: #d8ecf8;
      --panel-bg: rgba(255, 255, 255, 0.95);
      --panel-border: #cbd5e1;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --accent-india: #f97316;
      --accent-micro: #e11d48;
      --country-fill: #ffffff;
      --country-stroke: #94a3b8;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg-ocean);
      color: var(--text-main);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      user-select: none;
    }}

    /* Top Navigation & Controls */
    .top-bar {{
      position: absolute;
      top: 14px;
      left: 14px;
      right: 14px;
      z-index: 100;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      pointer-events: none;
    }}

    .card {{
      background: var(--panel-bg);
      backdrop-filter: blur(10px);
      border: 1px solid var(--panel-border);
      border-radius: 10px;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.1), 0 1px 4px rgba(15, 23, 42, 0.06);
      pointer-events: auto;
    }}

    .header-card {{
      padding: 8px 16px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .title-area h1 {{
      font-size: 15px;
      font-weight: 800;
      letter-spacing: -0.2px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .badge-soi {{
      background: #ffedd5;
      color: #9a3412;
      border: 1px solid #fed7aa;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 999px;
      letter-spacing: 0.3px;
    }}

    .title-area p {{
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 1px;
    }}

    .controls-strip {{
      padding: 7px 12px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .ctrl-group {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-main);
    }}

    .ctrl-group label {{
      color: var(--text-muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}

    input[type="range"] {{
      width: 100px;
      accent-color: var(--primary);
      cursor: pointer;
    }}

    .num-box {{
      width: 52px;
      padding: 3px 5px;
      border: 1px solid var(--panel-border);
      border-radius: 5px;
      font-size: 12px;
      font-weight: 700;
      text-align: center;
      background: #fff;
    }}

    select, input[type="text"] {{
      padding: 5px 9px;
      border: 1px solid var(--panel-border);
      border-radius: 6px;
      font-size: 12px;
      background: #fff;
      color: var(--text-main);
      outline: none;
    }}

    select:focus, input[type="text"]:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
    }}

    .btn {{
      padding: 5px 11px;
      border: 1px solid var(--panel-border);
      background: #fff;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s ease;
    }}

    .btn:hover {{
      background: #f1f5f9;
      border-color: #94a3b8;
    }}

    .btn-primary {{
      background: var(--primary);
      border-color: var(--primary);
      color: #fff;
    }}

    .btn-primary:hover {{
      background: var(--primary-hover);
      border-color: var(--primary-hover);
    }}

    /* Map Display Viewport */
    #map-container {{
      width: 100vw;
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: grab;
    }}

    #map-container:active {{
      cursor: grabbing;
    }}

    svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    .ocean-sphere {{
      fill: #d8ecf8;
      stroke: #94a3b8;
      stroke-width: 0.8px;
    }}

    .graticule {{
      fill: none;
      stroke: #c8deec;
      stroke-width: 0.5px;
      stroke-dasharray: 2, 3;
    }}

    .country {{
      fill: #ffffff;
      stroke: #94a3b8;
      stroke-width: 0.55px;
      stroke-linejoin: round;
      cursor: pointer;
      transition: fill 0.1s ease;
    }}

    .country:hover {{
      fill: #e0f2fe !important;
      stroke: #2563eb !important;
      stroke-width: 1.1px;
    }}

    .country-india {{
      fill: #fef3c7 !important;
      stroke: #d97706 !important;
      stroke-width: 1.2px !important;
    }}

    .country-india:hover {{
      fill: #fde68a !important;
      stroke: #b45309 !important;
      stroke-width: 1.5px !important;
    }}

    /* DOTTED DISPUTED BORDERS (Much lighter than recognised borders) */
    .dotted-disputed {{
      fill: none;
      stroke: #b0bec5; /* Light soft gray */
      stroke-width: 1.0px;
      stroke-dasharray: 1.5, 2.5; /* Fine dotted style */
      stroke-linecap: round;
      opacity: 0.85;
      pointer-events: none;
    }}

    /* Micronation Pins */
    .micronation-pin {{
      fill: var(--accent-micro);
      stroke: #ffffff;
      stroke-width: 1.5px;
      cursor: pointer;
      transition: r 0.15s ease;
    }}

    .micronation-pin:hover {{
      r: 6px;
      filter: drop-shadow(0 0 5px rgba(225, 29, 72, 0.7));
    }}

    /* BOLD ALL COUNTRIES NAMES (Google Maps Format) */
    .country-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 11px;
      font-weight: 700; /* BOLD */
      fill: #0f172a;
      stroke: #ffffff;
      stroke-width: 2.8px;
      stroke-linejoin: round;
      paint-order: stroke fill;
      pointer-events: none;
      text-anchor: middle;
      dominant-baseline: central;
      letter-spacing: -0.15px;
    }}

    .country-label.prominent {{
      font-size: 12px;
      font-weight: 800;
    }}

    .dependency-label {{
      font-size: 9.5px;
      font-weight: 600;
      fill: #475569;
      stroke: #ffffff;
      stroke-width: 2.4px;
      stroke-linejoin: round;
      paint-order: stroke fill;
      pointer-events: none;
    }}

    .ocean-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 11.5px;
      font-style: italic;
      font-weight: 700;
      letter-spacing: 3.5px;
      fill: #3f7893;
      pointer-events: all;
      cursor: pointer;
      text-anchor: middle;
      dominant-baseline: central;
      transition: fill 0.15s ease;
    }}

    .ocean-label:hover {{
      fill: #0369a1;
      text-decoration: underline;
    }}

    .ocean-sub-label {{
      font-size: 9.5px;
      letter-spacing: 2.5px;
      fill: #5a8eab;
    }}

    .micro-label {{
      font-size: 9.5px;
      font-weight: 700;
      fill: #be123c;
      stroke: #ffffff;
      stroke-width: 2.5px;
      stroke-linejoin: round;
      paint-order: stroke fill;
      pointer-events: none;
    }}

    /* Info Sidebar */
    .info-panel {{
      position: absolute;
      bottom: 20px;
      right: 20px;
      width: 320px;
      padding: 16px;
      z-index: 100;
      display: none;
      animation: fadeIn 0.2s ease-out;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .info-panel h3 {{
      font-size: 15px;
      font-weight: 800;
      margin-bottom: 6px;
    }}

    .info-meta {{
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 12px;
      line-height: 1.5;
    }}

    .info-wiki-btn {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      width: 100%;
      padding: 8px 12px;
      background: #0f172a;
      color: #fff;
      text-decoration: none;
      border-radius: 7px;
      font-size: 12px;
      font-weight: 700;
      transition: background 0.15s ease;
    }}

    .info-wiki-btn:hover {{
      background: #334155;
    }}

    #tooltip {{
      position: absolute;
      background: rgba(15, 23, 42, 0.94);
      color: #fff;
      padding: 6px 11px;
      border-radius: 6px;
      font-size: 12px;
      pointer-events: none;
      z-index: 200;
      display: none;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      line-height: 1.4;
    }}

    #tooltip .wiki-hint {{
      font-size: 10px;
      color: #93c5fd;
      margin-top: 2px;
    }}

    .quick-tips {{
      position: absolute;
      bottom: 16px;
      left: 16px;
      padding: 7px 12px;
      font-size: 11px;
      color: var(--text-muted);
      z-index: 90;
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .tip-item {{
      display: flex;
      align-items: center;
      gap: 5px;
    }}

    .swatch-dotted {{
      display: inline-block;
      width: 16px;
      height: 0;
      border-top: 2px dotted #b0bec5;
    }}
  </style>
</head>
<body>

  <!-- Controls Bar -->
  <div class="top-bar">
    <div class="card header-card">
      <div class="title-area">
        <h1>
          Equal Earth Map
          <span class="badge-soi">SOI Official India Map</span>
        </h1>
        <p>Google Maps format · Bold country names · Light dotted disputed borders · Oceans enabled</p>
      </div>
    </div>

    <div class="card controls-strip">
      <!-- Search Country / Ocean -->
      <div class="ctrl-group">
        <label for="country-search">Search:</label>
        <input type="text" id="country-search" list="target-list" placeholder="Search country, ocean..." style="width: 190px;">
        <datalist id="target-list"></datalist>
      </div>

      <!-- Central Longitude -->
      <div class="ctrl-group">
        <label for="lon-slider">Center Lon:</label>
        <input type="range" id="lon-slider" min="-180" max="180" step="1" value="{initial_lon}">
        <input type="number" id="lon-box" class="num-box" min="-180" max="180" step="1" value="{initial_lon}">
      </div>

      <!-- Central Latitude -->
      <div class="ctrl-group">
        <label for="lat-slider">Center Lat:</label>
        <input type="range" id="lat-slider" min="-90" max="90" step="1" value="{initial_lat}">
        <input type="number" id="lat-box" class="num-box" min="-90" max="90" step="1" value="{initial_lat}">
      </div>

      <!-- Projection Mode -->
      <div class="ctrl-group">
        <label for="proj-mode">Adjustment:</label>
        <select id="proj-mode">
          <option value="natural" {'selected' if mode == 'natural' else ''}>Natural Viewport (Clean & Less Weird)</option>
          <option value="oblique" {'selected' if mode == 'oblique' else ''}>Oblique Projection Tilt (Rough)</option>
        </select>
      </div>

      <button id="toggle-labels" class="btn">Labels: ON</button>
      <button id="reset-btn" class="btn">Reset</button>
      <button id="export-svg-btn" class="btn btn-primary">Export SVG</button>
    </div>
  </div>

  <!-- Map Container -->
  <div id="map-container">
    <svg id="map-svg"></svg>
  </div>

  <!-- Footer Tip -->
  <div class="card quick-tips">
    <div class="tip-item">
      <span style="display:inline-block; width:10px; height:10px; background:#fef3c7; border:1px solid #d97706; border-radius:2px;"></span>
      <span>India (Survey of India 100% Official Border)</span>
    </div>
    <div class="tip-item">
      <span class="swatch-dotted"></span>
      <span>Dotted Disputed Borders (Lighter than Recognized Borders)</span>
    </div>
    <div class="tip-item">
      <span>🖱️ Click any country or ocean to open its Wikipedia page</span>
    </div>
  </div>

  <!-- Sidebar Card -->
  <div class="card info-panel" id="info-panel">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
      <h3 id="info-name">Name</h3>
      <button id="close-info" style="border:none; background:none; font-size:16px; cursor:pointer; color:var(--text-muted);">&times;</button>
    </div>
    <div class="info-meta" id="info-meta">
      ISO: <span id="info-iso"></span><br>
      Coordinates: <span id="info-coords"></span><br>
      Status: <span id="info-type"></span>
    </div>
    <a href="#" target="_blank" class="info-wiki-btn" id="info-wiki-link">
      <span>Read on Wikipedia</span>
      <span>↗</span>
    </a>
  </div>

  <div id="tooltip"></div>

  <!-- Embedded World Data -->
  <script>
    const WORLD_DATA = {geojson_str};
    const INITIAL_LON = {initial_lon};
    const INITIAL_LAT = {initial_lat};
    const INITIAL_TARGET = "{initial_target}";
    const INITIAL_MODE = "{mode}";
  </script>

  <script>
    const width = window.innerWidth;
    const height = window.innerHeight;

    const svg = d3.select("#map-svg")
      .attr("viewBox", [0, 0, width, height])
      .attr("width", width)
      .attr("height", height);

    const g = svg.append("g");

    const projection = d3.geoEqualEarth();
    const pathGenerator = d3.geoPath().projection(projection);
    const graticule = d3.geoGraticule().step([15, 15]);

    // Layer Structure
    const oceanLayer = g.append("path").attr("class", "ocean-sphere");
    const graticuleLayer = g.append("g");
    const countryLayer = g.append("g");
    const dottedBordersLayer = g.append("g");
    const oceanLabelsLayer = g.append("g");
    const micronationLayer = g.append("g");
    const labelLayer = g.append("g");

    // State
    let currentLon = INITIAL_LON;
    let currentLat = INITIAL_LAT;
    let currentMode = INITIAL_MODE;
    let currentZoomK = 1.0;
    let showLabels = true;

    // Zoom handler
    const zoom = d3.zoom()
      .scaleExtent([0.8, 16])
      .on("zoom", (event) => {{
        currentZoomK = event.transform.k;
        g.attr("transform", event.transform);
        updateLabelStylesAndVisibility(event.transform.k);
      }});

    svg.call(zoom);

    // Populate Search Datalist
    const datalist = document.getElementById("target-list");
    WORLD_DATA.oceans.forEach(o => {{
      const opt = document.createElement("option");
      opt.value = o.name;
      datalist.appendChild(opt);
    }});
    WORLD_DATA.features.forEach(feat => {{
      const opt = document.createElement("option");
      opt.value = feat.properties.name;
      datalist.appendChild(opt);
    }});

    const countryFills = [
      "#ffffff", "#f8fafc", "#f1f5f9", "#e2e8f0", "#fef3c7",
      "#ecfdf5", "#f0fdf4", "#eff6ff", "#f5f3ff", "#faf5ff"
    ];

    function getCountryFill(name, i) {{
      if (name === "India") return "#fef3c7";
      return countryFills[i % countryFills.length];
    }}

    function updateProjection() {{
      const scale = Math.min(width / 5.6, height / 2.9);

      if (currentMode === "natural") {{
        projection
          .scale(scale)
          .rotate([-currentLon, 0, 0])
          .center([0, 0])
          .translate([width / 2, height / 2]);

        const centerPt = projection([currentLon, currentLat]);
        if (centerPt) {{
          const dy = (height / 2) - centerPt[1];
          svg.transition().duration(350).call(
            zoom.transform,
            d3.zoomIdentity.translate(0, dy).scale(currentZoomK)
          );
        }}
      }} else {{
        projection
          .scale(scale)
          .rotate([-currentLon, -currentLat, 0])
          .center([0, 0])
          .translate([width / 2, height / 2]);

        svg.transition().duration(350).call(
          zoom.transform,
          d3.zoomIdentity.scale(currentZoomK)
        );
      }}

      renderGeometry();
    }}

    function renderGeometry() {{
      // Ocean sphere
      oceanLayer.datum({{ type: "Sphere" }}).attr("d", pathGenerator);

      // Graticule
      graticuleLayer.selectAll("*").remove();
      graticuleLayer.append("path")
        .datum(graticule)
        .attr("class", "graticule")
        .attr("d", pathGenerator);

      // Countries
      const countries = countryLayer.selectAll("path.country")
        .data(WORLD_DATA.features, d => d.properties.name);

      countries.join(
        enter => enter.append("path")
          .attr("class", d => d.properties.name === "India" ? "country country-india" : "country")
          .attr("fill", (d, i) => getCountryFill(d.properties.name, i))
          .attr("d", pathGenerator)
          .on("mouseenter", handleMouseEnter)
          .on("mousemove", handleMouseMove)
          .on("mouseleave", handleMouseLeave)
          .on("click", handleCountryClick),
        update => update.attr("d", pathGenerator)
      );

      // Dotted Disputed Borders (Lighter than recognized borders)
      dottedBordersLayer.selectAll("*").remove();
      if (WORLD_DATA.dashed_borders) {{
        WORLD_DATA.dashed_borders.forEach(db => {{
          dottedBordersLayer.append("path")
            .datum(db)
            .attr("class", "dotted-disputed")
            .attr("d", pathGenerator);
        }});
      }}

      // Ocean Labels
      renderOceanLabels();

      // Micronation Pins
      renderMicronationPins();

      // Country Labels
      renderCountryLabels();
      updateLabelStylesAndVisibility(currentZoomK);
    }}

    function renderOceanLabels() {{
      oceanLabelsLayer.selectAll("*").remove();
      WORLD_DATA.oceans.forEach(ocean => {{
        const pt = projection(ocean.centroid);
        if (pt && !isNaN(pt[0]) && !isNaN(pt[1])) {{
          oceanLabelsLayer.append("text")
            .attr("class", "ocean-label")
            .attr("x", pt[0])
            .attr("y", pt[1])
            .text(ocean.label)
            .on("click", () => handleOceanClick(ocean));
        }}

        if (ocean.sub_labels) {{
          ocean.sub_labels.forEach(sub => {{
            const spt = projection(sub.centroid);
            if (spt && !isNaN(spt[0]) && !isNaN(spt[1])) {{
              oceanLabelsLayer.append("text")
                .attr("class", "ocean-label ocean-sub-label")
                .attr("x", spt[0])
                .attr("y", spt[1])
                .text(sub.label)
                .on("click", () => handleOceanClick(ocean));
            }}
          }});
        }}
      }});
    }}

    function renderMicronationPins() {{
      const micronations = WORLD_DATA.features.filter(d => d.properties.is_micronation);
      const pins = micronationLayer.selectAll("circle.micronation-pin")
        .data(micronations, d => d.properties.name);

      pins.join(
        enter => enter.append("circle")
          .attr("class", "micronation-pin")
          .attr("r", 4)
          .attr("cx", d => projection(d.properties.centroid)[0])
          .attr("cy", d => projection(d.properties.centroid)[1])
          .on("mouseenter", handleMouseEnter)
          .on("mousemove", handleMouseMove)
          .on("mouseleave", handleMouseLeave)
          .on("click", handleCountryClick),
        update => update
          .attr("cx", d => projection(d.properties.centroid)[0])
          .attr("cy", d => projection(d.properties.centroid)[1])
      );
    }}

    const prioritySovereigns = [
      "India", "China", "United States", "Brazil", "Russia", "Canada", "Australia",
      "Argentina", "Algeria", "DR Congo", "Saudi Arabia", "Mexico", "Indonesia",
      "South Africa", "Kazakhstan", "Iran", "Mongolia", "Egypt", "Nigeria", "Pakistan",
      "Turkey", "France", "Germany", "United Kingdom", "Spain", "Italy", "Japan",
      "Poland", "Ukraine", "Sweden", "Norway", "Finland", "Thailand", "Vietnam",
      "Colombia", "Peru", "Chile", "Kenya", "Tanzania", "Ethiopia", "Sudan",
      "Morocco", "New Zealand", "Philippines", "Madagascar", "Angola", "Myanmar",
      "Somalia", "Cyprus", "CAR", "Congo", "UAE", "Serbia"
    ];

    function renderCountryLabels() {{
      labelLayer.selectAll("*").remove();
      if (!showLabels) return;

      WORLD_DATA.features.forEach(feat => {{
        const p = feat.properties;
        const pt = projection(p.centroid);
        if (!pt || isNaN(pt[0]) || isNaN(pt[1])) return;

        let cls = "country-label";
        if (p.is_micronation) cls = "micro-label";
        else if (p.is_dependency) cls = "dependency-label";
        else if (prioritySovereigns.includes(p.name)) cls += " prominent";

        labelLayer.append("text")
          .attr("class", cls)
          .attr("x", pt[0])
          .attr("y", pt[1])
          .text(p.name)
          .attr("data-name", p.name)
          .attr("data-micro", p.is_micronation ? "true" : "false")
          .attr("data-dep", p.is_dependency ? "true" : "false")
          .attr("data-orig-x", pt[0])
          .attr("data-orig-y", pt[1]);
      }});
    }}

    // Dynamic Google Maps label scaling and prioritization
    function updateLabelStylesAndVisibility(k) {{
      const baseCountryPx = Math.max(9.0, 11.5 - Math.log2(k) * 0.6);
      const svgCountryFontSize = (baseCountryPx / k).toFixed(2) + "px";
      const svgCountryStroke = (2.6 / k).toFixed(2) + "px";

      const svgMicroFontSize = (9.5 / k).toFixed(2) + "px";
      const svgDepFontSize = (8.5 / k).toFixed(2) + "px";

      // Micronation pins: visible ONLY when zoomed in (k >= 2.2)
      micronationLayer.style("display", k >= 2.2 ? "block" : "none");
      if (k >= 2.2) {{
        micronationLayer.selectAll("circle.micronation-pin")
          .attr("r", Math.max(2.5, 4.5 / Math.sqrt(k)))
          .style("stroke-width", (1.5 / k) + "px");
      }}

      // Dotted borders stroke scaling
      dottedBordersLayer.selectAll(".dotted-disputed")
        .style("stroke-width", (1.0 / k) + "px");

      // Ocean labels
      const svgOceanFontSize = (12.0 / Math.sqrt(k)).toFixed(2) + "px";
      oceanLabelsLayer.selectAll(".ocean-label")
        .style("font-size", svgOceanFontSize);

      // Collision Boxes in Screen Space
      const placedBoxes = [];

      // Sort order: Sovereign nations first, dependencies last
      const labels = labelLayer.selectAll("text").nodes();
      labels.sort((a, b) => {{
        const aDep = a.getAttribute("data-dep") === "true";
        const bDep = b.getAttribute("data-dep") === "true";
        const aMicro = a.getAttribute("data-micro") === "true";
        const bMicro = b.getAttribute("data-micro") === "true";
        if (aMicro && !bMicro) return 1;
        if (!aMicro && bMicro) return -1;
        if (aDep && !bDep) return 1;
        if (!aDep && bDep) return -1;
        return 0;
      }});

      labels.forEach(node => {{
        const el = d3.select(node);
        const isMicro = el.attr("data-micro") === "true";
        const isDep = el.attr("data-dep") === "true";
        const name = el.attr("data-name");

        // Micronations only show at zoom >= 2.2
        if (isMicro) {{
          if (k < 2.2) {{
            el.style("display", "none");
            return;
          }}
          el.style("display", "block")
            .style("font-size", svgMicroFontSize)
            .style("stroke-width", (2.2 / k) + "px");
          return;
        }}

        // Dependencies: NEVER displace sovereign countries when zoomed out (k < 2.5)
        if (isDep) {{
          if (k < 2.5) {{
            el.style("display", "none");
            return;
          }}
          el.style("font-size", svgDepFontSize)
            .style("stroke-width", (2.0 / k) + "px");
        }} else {{
          // Bold sovereign country label
          el.style("font-size", svgCountryFontSize)
            .style("stroke-width", svgCountryStroke);
        }}

        const origX = parseFloat(el.attr("data-orig-x"));
        const origY = parseFloat(el.attr("data-orig-y"));
        
        const screenX = origX * k + (d3.zoomTransform(svg.node()).x);
        const screenY = origY * k + (d3.zoomTransform(svg.node()).y);

        const textLen = name.length;
        const boxW = textLen * baseCountryPx * 0.58;
        const boxH = baseCountryPx * 1.35;

        const curBox = {{
          x1: screenX - boxW / 2,
          x2: screenX + boxW / 2,
          y1: screenY - boxH / 2,
          y2: screenY + boxH / 2
        }};

        const isProminent = prioritySovereigns.includes(name);

        let collides = false;
        for (let b of placedBoxes) {{
          if (!(curBox.x2 < b.x1 || curBox.x1 > b.x2 || curBox.y2 < b.y1 || curBox.y1 > b.y2)) {{
            collides = true;
            break;
          }}
        }}

        if (!collides || isProminent) {{
          el.style("display", "block");
          placedBoxes.push(curBox);
        }} else {{
          el.style("display", "none");
        }}
      }});
    }}

    // Tooltip and interactions
    const tooltip = document.getElementById("tooltip");
    function handleMouseEnter(event, d) {{
      const p = d.properties;
      tooltip.style.display = "block";
      tooltip.innerHTML = `
        <strong>${{p.name}}</strong> ${{p.is_micronation ? '· <em>Micronation</em>' : (p.is_dependency ? '· <em>Dependency</em>' : '')}}<br>
        <span style="color:#94a3b8;">Coords: ${{p.centroid[1].toFixed(1)}}°, ${{p.centroid[0].toFixed(1)}}°</span>
        <div class="wiki-hint">🔗 Click to open Wikipedia article ↗</div>
      `;
    }}

    function handleMouseMove(event) {{
      tooltip.style.left = (event.pageX + 14) + "px";
      tooltip.style.top = (event.pageY + 14) + "px";
    }}

    function handleMouseLeave() {{
      tooltip.style.display = "none";
    }}

    function handleCountryClick(event, d) {{
      const p = d.properties;
      window.open(p.wiki, "_blank");
      showInfoCard(p);
    }}

    function handleOceanClick(ocean) {{
      window.open(ocean.wiki, "_blank");
      centerOnTarget(ocean.name);
    }}

    function showInfoCard(p) {{
      const panel = document.getElementById("info-panel");
      panel.style.display = "block";
      document.getElementById("info-name").textContent = p.name;
      document.getElementById("info-iso").textContent = (p.iso_a2 || p.iso_a3) ? `${{p.iso_a2}} / ${{p.iso_a3}}` : "N/A";
      document.getElementById("info-coords").textContent = `${{p.centroid[1].toFixed(2)}}° Lat, ${{p.centroid[0].toFixed(2)}}° Lon`;
      document.getElementById("info-type").textContent = p.is_micronation ? "Micronation" : (p.name === "India" ? "Sovereign Republic (Official SOI Boundary)" : (p.is_dependency ? "Dependency" : "Sovereign Nation"));
      document.getElementById("info-wiki-link").href = p.wiki;
    }}

    document.getElementById("close-info").addEventListener("click", () => {{
      document.getElementById("info-panel").style.display = "none";
    }});

    // Center on Country or Ocean
    function centerOnTarget(targetName) {{
      const query = targetName.trim().toLowerCase();

      const ocean = WORLD_DATA.oceans.find(o => o.name.toLowerCase() === query);
      if (ocean) {{
        const [lon, lat] = ocean.centroid;
        currentLon = Math.round(lon);
        currentLat = Math.round(lat);
        syncControls();
        updateProjection();
        return;
      }}

      const target = WORLD_DATA.features.find(f => f.properties.name.toLowerCase() === query);
      if (target) {{
        const [lon, lat] = target.properties.centroid;
        currentLon = Math.round(lon);
        currentLat = Math.round(lat);
        syncControls();
        updateProjection();
        showInfoCard(target.properties);
      }}
    }}

    function syncControls() {{
      document.getElementById("lon-slider").value = currentLon;
      document.getElementById("lon-box").value = currentLon;
      document.getElementById("lat-slider").value = currentLat;
      document.getElementById("lat-box").value = currentLat;
    }}

    const lonSlider = document.getElementById("lon-slider");
    const lonBox = document.getElementById("lon-box");
    const latSlider = document.getElementById("lat-slider");
    const latBox = document.getElementById("lat-box");

    function syncLon(val) {{
      currentLon = parseFloat(val);
      lonSlider.value = currentLon;
      lonBox.value = currentLon;
      updateProjection();
    }}

    function syncLat(val) {{
      currentLat = parseFloat(val);
      latSlider.value = currentLat;
      latBox.value = currentLat;
      updateProjection();
    }}

    lonSlider.addEventListener("input", (e) => syncLon(e.target.value));
    lonBox.addEventListener("change", (e) => syncLon(e.target.value));
    latSlider.addEventListener("input", (e) => syncLat(e.target.value));
    latBox.addEventListener("change", (e) => syncLat(e.target.value));

    document.getElementById("proj-mode").addEventListener("change", (e) => {{
      currentMode = e.target.value;
      updateProjection();
    }});

    document.getElementById("country-search").addEventListener("change", (e) => {{
      centerOnTarget(e.target.value);
    }});

    document.getElementById("toggle-labels").addEventListener("click", () => {{
      showLabels = !showLabels;
      document.getElementById("toggle-labels").textContent = `Labels: ${{showLabels ? 'ON' : 'OFF'}}`;
      renderCountryLabels();
      updateLabelStylesAndVisibility(currentZoomK);
    }});

    document.getElementById("reset-btn").addEventListener("click", () => {{
      currentLon = INITIAL_LON;
      currentLat = INITIAL_LAT;
      currentZoomK = 1.0;
      syncControls();
      document.getElementById("country-search").value = "";
      updateProjection();
      svg.transition().duration(350).call(zoom.transform, d3.zoomIdentity);
    }});

    document.getElementById("export-svg-btn").addEventListener("click", () => {{
      const svgEl = document.getElementById("map-svg");
      const serializer = new XMLSerializer();
      let source = serializer.serializeToString(svgEl);
      source = '<?xml version="1.0" standalone="no"?>\\r\\n' + source;
      const url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);
      const downloadLink = document.createElement("a");
      downloadLink.href = url;
      downloadLink.download = `equal_earth_lon${{currentLon}}_lat${{currentLat}}.svg`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
    }});

    // Initial Start
    if (INITIAL_TARGET && INITIAL_TARGET !== "World") {{
      document.getElementById("country-search").value = INITIAL_TARGET;
      centerOnTarget(INITIAL_TARGET);
    }} else {{
      updateProjection();
    }}

    window.addEventListener("resize", () => {{
      const w = window.innerWidth;
      const h = window.innerHeight;
      svg.attr("viewBox", [0, 0, w, h]).attr("width", w).attr("height", h);
      updateProjection();
    }});
  </script>
</body>
</html>
"""

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n[+] Interactive Equal Earth web map generated: {HTML_OUTPUT}")
    return HTML_OUTPUT


def generate_static_png(lon, lat, target_name, output_path=None):
    """Generate high-visibility Light Mode static PNG with SOI boundary & dotted borders."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs
        from shapely.geometry import shape

        world_data = load_world_data()

        fig = plt.figure(figsize=(15, 7.5), facecolor="#ffffff")
        ax = plt.axes(projection=ccrs.EqualEarth(central_longitude=lon))
        ax.set_facecolor("#d8ecf8")

        # 1. Countries
        for feat in world_data["features"]:
            geom = shape(feat["geometry"])
            name = feat["properties"]["name"]

            if name == "India":
                face = "#fef3c7"
                edge = "#d97706"
                lw = 1.2
            else:
                face = "#ffffff"
                edge = "#94a3b8"
                lw = 0.45

            ax.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor=face, edgecolor=edge, linewidth=lw)

        # 2. Dotted Disputed Borders (Much lighter than recognised borders)
        for db in world_data.get("dashed_borders", []):
            geom = shape(db["geometry"])
            ax.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor="none",
                              edgecolor="#b0bec5", linewidth=0.9, linestyle=":", alpha=0.9)

        # 3. Ocean Labels
        for ocean in world_data.get("oceans", []):
            pt = ocean["centroid"]
            ax.text(pt[0], pt[1], ocean["label"], transform=ccrs.PlateCarree(),
                    fontsize=8.5, fontstyle="italic", color="#3f7893", ha="center", va="center",
                    fontweight="bold")

        # 4. BOLD Country Labels (Google Maps style)
        major_countries = {
            "India", "China", "United States", "Brazil", "Russia", "Canada", "Australia",
            "Argentina", "Algeria", "DR Congo", "Saudi Arabia", "Mexico", "Indonesia",
            "South Africa", "Kazakhstan", "Egypt", "France", "Germany", "United Kingdom",
            "Japan", "Somalia", "Cyprus", "UAE", "CAR", "Congo", "Serbia"
        }
        if target_name and target_name != "World":
            major_countries.add(target_name)

        for feat in world_data["features"]:
            name = feat["properties"]["name"]
            if name in major_countries:
                centroid = feat["properties"]["centroid"]
                ax.text(centroid[0], centroid[1], name, transform=ccrs.PlateCarree(),
                        fontsize=7.5, fontweight="bold",
                        color="#0f172a", ha="center", va="center",
                        bbox=dict(boxstyle="square,pad=0.12", facecolor="#ffffff", alpha=0.75, edgecolor="none"))

        gl = ax.gridlines(draw_labels=True, linewidth=0.5, color="#c8deec", alpha=0.8, linestyle="--")
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {"size": 8, "color": "#64748b"}
        gl.ylabel_style = {"size": 8, "color": "#64748b"}

        title_suffix = f" · Centered on {target_name} ({lon:+.1f}°E, {lat:+.1f}°N)" if target_name != "World" else f" · Centered at Lon {lon:+.1f}°"
        plt.title(f"Equal Earth Projection{title_suffix}\n(Survey of India Official Sovereign Boundaries & Google Maps Format)",
                  fontsize=12, fontweight="bold", color="#0f172a", pad=12)

        if not output_path:
            clean_name = target_name.lower().replace(" ", "_") if target_name else f"lon_{lon}"
            output_path = BASE_DIR / f"equal_earth_{clean_name}.png"

        plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="#ffffff")
        plt.close(fig)
        print(f"[+] Static Light Mode PNG saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"[-] Note: Static PNG rendering skipped ({e}). Interactive web map is fully operational.")
        return None


def main():
    parser = argparse.ArgumentParser(description="Equal Earth Map Generator & Interactive Viewer")
    parser.add_argument("--target", "--country", type=str, help="Country, micronation, or ocean to center around")
    parser.add_argument("--lon", type=float, help="Custom central longitude (-180 to 180)")
    parser.add_argument("--lat", type=float, help="Custom central latitude (-90 to 90)")
    parser.add_argument("--mode", choices=["natural", "oblique"], default="natural",
                        help="Projection mode: 'natural' (clean) or 'oblique' (rough tilt)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch browser")
    parser.add_argument("--no-png", action="store_true", help="Skip static PNG export")
    args = parser.parse_args()

    world_data = load_world_data()

    target_name = "World"
    lon = 0.0
    lat = 0.0
    mode = args.mode

    if args.target:
        entity = find_entity(args.target, world_data)
        if entity:
            target_name = entity["properties"]["name"]
            lon, lat = entity["properties"]["centroid"]
            print(f"[*] Found: {target_name} (Centroid: {lat:.2f}°N, {lon:.2f}°E)")
        else:
            print(f"[!] Warning: '{args.target}' not found. Defaulting to 0° lon.")
    elif args.lon is not None or args.lat is not None:
        lon = args.lon if args.lon is not None else 0.0
        lat = args.lat if args.lat is not None else 0.0
        target_name = f"Custom ({lon:.1f}°, {lat:.1f}°)"
    else:
        print("=" * 66)
        print(" EQUAL EARTH MAP GENERATOR (Google Maps Format & SOI Compliant)")
        print("=" * 66)
        print("Options:")
        print("  1. Center on Country, Micronation, or Ocean (e.g. India, Indian Ocean, Monaco)")
        print("  2. Enter custom Longitude and Latitude coordinates")
        print("  3. View global map (Centered at Longitude 0°)")
        choice = input("\nEnter choice [1/2/3] (default 1): ").strip() or "1"

        if choice == "1":
            user_input = input("Enter Country or Ocean name (e.g. 'India' or 'Indian Ocean'): ").strip() or "India"
            entity = find_entity(user_input, world_data)
            if entity:
                target_name = entity["properties"]["name"]
                lon, lat = entity["properties"]["centroid"]
                print(f"[*] Centered on: {target_name} ({lat:.2f}°N, {lon:.2f}°E)")
            else:
                print(f"[!] '{user_input}' not found. Defaulting to India.")
                entity = find_entity("India", world_data)
                target_name = "India"
                lon, lat = entity["properties"]["centroid"]
        elif choice == "2":
            lon_in = input("Enter central longitude [-180 to 180] (default 78.96): ").strip() or "78.96"
            lat_in = input("Enter central latitude [-90 to 90] (default 20.59): ").strip() or "20.59"
            lon = float(lon_in)
            lat = float(lat_in)
            target_name = f"Custom ({lon:.1f}°, {lat:.1f}°)"
        else:
            target_name = "World"
            lon, lat = 0.0, 0.0

        print("\nProjection adjustment options to prevent weird distortion:")
        print("  1. Natural Viewport (Recommended: clean horizontal parallels, no shear)")
        print("  2. Oblique Projection Tilt (Rough tilted projection)")
        proj_choice = input("Select mode [1/2] (default 1): ").strip() or "1"
        mode = "natural" if proj_choice == "1" else "oblique"

    html_file = build_interactive_html(
        initial_lon=round(lon, 2),
        initial_lat=round(lat, 2),
        initial_target=target_name,
        mode=mode,
    )

    if not args.no_png:
        generate_static_png(round(lon, 2), round(lat, 2), target_name)

    if not args.no_browser:
        print(f"[*] Opening interactive map in browser...")
        try:
            webbrowser.open(f"file://{html_file.resolve()}")
        except Exception:
            pass

    print("\n[✓] Done! Map is ready.")


if __name__ == "__main__":
    main()