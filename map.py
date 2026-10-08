"""
Equal Earth Map Generator & Interactive Viewer (Google Maps Format)
===================================================================
- India is NOT highlighted by default (at 0° lon or on reset).
- ONLY the searched or selected country gets highlighted in yellow.
- High-quality exports: High-Res JPEG, Vector PDF, and Self-Contained SVG (with embedded background & styles).
- Disputed borders (Serbia-Kosovo, Morocco-SADR, Bir Tawil & Hala'ib) in light dashed lines (Google Maps style).
- All country names bolded.
- Short names and acronyms (USA, UAE, CAR, DR Congo, etc.).
- Sovereign countries prioritized over dependencies when zoomed out.
- All Oceans labeled with ability to center map around them.
- Survey of India (SOI) 100% official sovereign boundary for India.
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
JSPDF_PATH = BASE_DIR / "jspdf.umd.min.js"
HTML_OUTPUT = BASE_DIR / "equal_earth_interactive.html"
ROOT_INDEX = BASE_DIR / "index.html"

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

    jspdf_script_tag = """
    <script src="jspdf.umd.min.js"></script>
    <script>
      if (typeof window.jspdf === 'undefined') {
        document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"><\\/script>');
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
  {jspdf_script_tag}
  <style>
    :root {{
      --bg-ocean: #d8ecf8;
      --panel-bg: rgba(255, 255, 255, 0.95);
      --panel-border: #cbd5e1;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --accent-highlight: #fef3c7;
      --accent-highlight-border: #d97706;
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
      background: #f1f5f9;
      color: #334155;
      border: 1px solid #cbd5e1;
      font-size: 10px;
      font-weight: 700;
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
      gap: 10px;
      flex-wrap: wrap;
    }}

    .ctrl-group {{
      display: flex;
      align-items: center;
      gap: 5px;
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
      width: 95px;
      accent-color: var(--primary);
      cursor: pointer;
    }}

    .num-box {{
      width: 50px;
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
      padding: 5px 10px;
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

    .btn-success {{
      background: #059669;
      border-color: #059669;
      color: #fff;
    }}

    .btn-success:hover {{
      background: #047857;
      border-color: #047857;
    }}

    .btn-satellite {{
      background: #0f172a;
      border-color: #0284c7;
      color: #38bdf8;
      text-decoration: none;
    }}

    .btn-satellite:hover {{
      background: #0284c7;
      border-color: #0284c7;
      color: #ffffff;
      box-shadow: 0 0 10px rgba(2, 132, 199, 0.4);
    }}

    .nav-satellite-btn {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 6px 11px;
      background: #0f172a;
      border: 1px solid #0284c7;
      border-radius: 6px;
      color: #38bdf8;
      font-size: 11.5px;
      font-weight: 700;
      text-decoration: none;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}

    .nav-satellite-btn:hover {{
      background: #0284c7;
      color: #ffffff;
      transform: translateY(-1px);
    }}

    /* Map Display Viewport */
    #map-container {{
      width: 100vw;
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: grab;
      touch-action: none;
      -webkit-touch-callout: none;
      -webkit-user-select: none;
      user-select: none;
    }}

    #map-container:active {{
      cursor: grabbing;
    }}

    svg {{
      width: 100%;
      height: 100%;
      display: block;
      touch-action: none;
      -webkit-touch-callout: none;
      -webkit-user-select: none;
      user-select: none;
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

    /* Graticule Edge Labels (60°N, 30°N, 0°, 30°S, 60°S & Longitudes) */
    .graticule-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 8.5px;
      font-weight: 600;
      fill: #64748b;
      stroke: #ffffff;
      stroke-width: 2.2px;
      stroke-linejoin: round;
      paint-order: stroke fill;
      pointer-events: none;
      dominant-baseline: central;
    }}

    .country {{
      fill: #ffffff;
      stroke: #94a3b8;
      stroke-width: 0.55px;
      stroke-linejoin: round;
      cursor: pointer;
      transition: fill 0.15s ease, stroke-width 0.15s ease;
    }}

    .country:hover {{
      fill: #e0f2fe !important;
      stroke: #2563eb !important;
      stroke-width: 1.1px;
    }}

    /* Highlighted Country: ONLY applied when searched or clicked */
    .country.highlighted {{
      fill: #fef3c7 !important;
      stroke: #d97706 !important;
      stroke-width: 1.4px !important;
    }}

    .country.highlighted:hover {{
      fill: #fde68a !important;
      stroke: #b45309 !important;
    }}

    /* DISPUTED BORDERS (Light Dashed Line: Serbia-Kosovo, Morocco-SADR, Bir Tawil) */
    .dashed-disputed {{
      fill: none;
      stroke: #718096;
      stroke-width: 1.1px;
      stroke-dasharray: 3.5, 3.0;
      stroke-linecap: round;
      opacity: 0.9;
      pointer-events: none;
    }}

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

    /* Bold Country Names */
    .country-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 11px;
      font-weight: 700;
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

    .action-buttons-wrap {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .mobile-controls-toggle {{
      display: none;
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

    .swatch-dashed {{
      display: inline-block;
      width: 16px;
      height: 0;
      border-top: 2px dashed #718096;
    }}

    /* Mobile Responsive Styles */
    @media (max-width: 768px) {{
      .top-bar {{
        top: 8px;
        left: 8px;
        right: 8px;
        flex-direction: column;
        align-items: stretch;
        gap: 6px;
      }}

      .header-card {{
        padding: 7px 12px;
        justify-content: space-between;
        width: 100%;
      }}

      .title-area h1 {{
        font-size: 13px;
        gap: 6px;
      }}

      .title-area p {{
        display: none;
      }}

      .badge-soi {{
        font-size: 9px;
        padding: 1px 6px;
      }}

      .mobile-controls-toggle {{
        display: inline-flex !important;
        align-items: center;
        gap: 5px;
        padding: 5px 10px;
        font-size: 11.5px;
        font-weight: 700;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        cursor: pointer;
        color: var(--text-main);
      }}

      .controls-strip {{
        display: none;
        flex-direction: column;
        align-items: stretch;
        gap: 9px;
        width: 100%;
        padding: 12px;
        max-height: 80vh;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
      }}

      .controls-strip.open {{
        display: flex !important;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2);
      }}

      .controls-strip .ctrl-group {{
        display: flex;
        justify-content: space-between;
        width: 100%;
        align-items: center;
      }}

      .controls-strip .ctrl-group input[type="range"] {{
        flex: 1;
        margin: 0 8px;
        width: auto;
      }}

      .controls-strip select,
      .controls-strip input[type="text"] {{
        width: 100% !important;
        font-size: 13px;
      }}

      .action-buttons-wrap {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
        width: 100%;
        margin-top: 4px;
      }}

      .action-buttons-wrap #export-svg-btn {{
        grid-column: span 2;
      }}

      .action-buttons-wrap .btn {{
        justify-content: center;
        padding: 7px 10px;
        font-size: 11.5px;
      }}

      .quick-tips {{
        bottom: 8px;
        left: 8px;
        right: 8px;
        padding: 5px 10px;
        font-size: 9.5px;
        gap: 10px;
        overflow-x: auto;
        white-space: nowrap;
        -webkit-overflow-scrolling: touch;
      }}

      .quick-tips::-webkit-scrollbar {{
        display: none;
      }}

      .info-panel {{
        bottom: 8px;
        left: 8px;
        right: 8px;
        width: auto;
        max-width: calc(100vw - 16px);
        padding: 12px;
      }}
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
          <span class="badge-soi">SOI Official India Boundary</span>
        </h1>
        <p>Google Maps format · Bold names · Light dashed disputed borders</p>
      </div>
      <div style="display: flex; align-items: center; gap: 8px;">
        <a href="satellite_day_night.html" class="nav-satellite-btn" title="Switch to Topographic Satellite & Real-Time Day/Night View">
          🛰️ Topographic & Live Day/Night ↗
        </a>
        <button id="mobile-toggle-btn" class="mobile-controls-toggle" aria-label="Toggle Controls">
          <span>⚙️ Controls</span>
          <span id="toggle-chevron">▾</span>
        </button>
      </div>
    </div>

    <div class="card controls-strip" id="controls-strip">
      <div class="ctrl-group">
        <label for="country-search">Search:</label>
        <input type="text" id="country-search" list="target-list" placeholder="Search country, ocean..." style="width: 180px;">
        <datalist id="target-list"></datalist>
      </div>

      <div class="ctrl-group">
        <label for="lon-slider">Center Lon:</label>
        <input type="range" id="lon-slider" min="-180" max="180" step="1" value="{initial_lon}">
        <input type="number" id="lon-box" class="num-box" min="-180" max="180" step="1" value="{initial_lon}">
      </div>

      <div class="ctrl-group">
        <label for="lat-slider">Center Lat:</label>
        <input type="range" id="lat-slider" min="-90" max="90" step="1" value="{initial_lat}">
        <input type="number" id="lat-box" class="num-box" min="-90" max="90" step="1" value="{initial_lat}">
      </div>

      <div class="ctrl-group">
        <label for="proj-mode">Adjustment:</label>
        <select id="proj-mode">
          <option value="natural" {'selected' if mode == 'natural' else ''}>Natural Viewport (Clean & Less Weird)</option>
          <option value="oblique" {'selected' if mode == 'oblique' else ''}>Oblique Projection Tilt (Rough)</option>
        </select>
      </div>

      <div class="action-buttons-wrap">
        <a href="satellite_day_night.html" class="btn btn-satellite" title="Switch to Topographic Satellite & Live Day/Night View">🛰️ Satellite & Day/Night ↗</a>
        <button id="toggle-labels" class="btn">Labels: ON</button>
        <button id="reset-btn" class="btn">Reset</button>
        <button id="export-jpg-btn" class="btn btn-primary">Download JPEG</button>
        <button id="export-pdf-btn" class="btn btn-success">Download PDF</button>
        <button id="export-svg-btn" class="btn">Download SVG</button>
      </div>
    </div>
  </div>

  <!-- Map Container -->
  <div id="map-container">
    <svg id="map-svg"></svg>
  </div>

  <div class="card quick-tips">
    <div class="tip-item">
      <span class="swatch-dashed"></span>
      <span>Disputed Borders (Kosovo/Serbia, Morocco/SADR, Bir Tawil)</span>
    </div>
    <div class="tip-item">
      <span>🟡 Yellow highlight appears ONLY when country is searched</span>
    </div>
    <div class="tip-item">
      <span>🖱️ Click any country or ocean to open its Wikipedia page</span>
    </div>
  </div>

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
    const graticuleLabelsLayer = g.append("g");
    const countryLayer = g.append("g");
    const dashedBordersLayer = g.append("g");
    const oceanLabelsLayer = g.append("g");
    const micronationLayer = g.append("g");
    const labelLayer = g.append("g");

    // State Variables
    let currentLon = INITIAL_LON;
    let currentLat = INITIAL_LAT;
    let currentMode = INITIAL_MODE;
    let currentZoomK = 1.0;
    let showLabels = true;
    let isInitialLoad = true;
    
    // Highlight state: ONLY active if a valid country was specifically targeted
    const initialCountryObj = (INITIAL_TARGET && INITIAL_TARGET !== "World" && !INITIAL_TARGET.startsWith("Custom"))
      ? WORLD_DATA.features.find(f => f.properties.name.toLowerCase() === INITIAL_TARGET.trim().toLowerCase())
      : null;

    let highlightedCountry = initialCountryObj ? initialCountryObj.properties.name : null;

    const zoom = d3.zoom()
      .scaleExtent([0.8, 16])
      .on("zoom", (event) => {{
        currentZoomK = event.transform.k;
        g.attr("transform", event.transform);
        updateLabelStylesAndVisibility(event.transform.k);
      }});

    svg.call(zoom);

    // Populate Datalist
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
      "#ffffff", "#f8fafc", "#f1f5f9", "#e2e8f0", "#ffffff",
      "#ecfdf5", "#f0fdf4", "#eff6ff", "#f5f3ff", "#faf5ff"
    ];

    function getCountryFill(name, i) {{
      return countryFills[i % countryFills.length];
    }}

    function updateProjection() {{
      const scale = Math.min(width / 5.6, height / 2.9);
      let targetTransform = d3.zoomIdentity;

      if (currentMode === "natural") {{
        projection
          .scale(scale)
          .rotate([-currentLon, 0, 0])
          .center([0, 0])
          .translate([width / 2, height / 2]);

        const centerPt = projection([currentLon, currentLat]);
        const dy = centerPt ? ((height / 2) - centerPt[1]) : 0;
        targetTransform = d3.zoomIdentity.translate(0, dy).scale(currentZoomK);
      }} else {{
        projection
          .scale(scale)
          .rotate([-currentLon, -currentLat, 0])
          .center([0, 0])
          .translate([width / 2, height / 2]);

        targetTransform = d3.zoomIdentity.scale(currentZoomK);
      }}

      if (isInitialLoad) {{
        svg.call(zoom.transform, targetTransform);
        isInitialLoad = false;
      }} else {{
        svg.transition().duration(350).call(zoom.transform, targetTransform);
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
          .attr("class", d => {{
            const isMatch = (highlightedCountry && d.properties.name.toLowerCase() === highlightedCountry.toLowerCase());
            return isMatch ? "country highlighted" : "country";
          }})
          .attr("fill", (d, i) => {{
            const isMatch = (highlightedCountry && d.properties.name.toLowerCase() === highlightedCountry.toLowerCase());
            return isMatch ? "#fef3c7" : getCountryFill(d.properties.name, i);
          }})
          .attr("d", pathGenerator)
          .on("mouseenter", handleMouseEnter)
          .on("mousemove", handleMouseMove)
          .on("mouseleave", handleMouseLeave)
          .on("click", handleCountryClick),
        update => update
          .attr("class", d => {{
            const isMatch = (highlightedCountry && d.properties.name.toLowerCase() === highlightedCountry.toLowerCase());
            return isMatch ? "country highlighted" : "country";
          }})
          .attr("fill", (d, i) => {{
            const isMatch = (highlightedCountry && d.properties.name.toLowerCase() === highlightedCountry.toLowerCase());
            return isMatch ? "#fef3c7" : getCountryFill(d.properties.name, i);
          }})
          .attr("d", pathGenerator)
      );

      // Dashed Disputed Borders
      dashedBordersLayer.selectAll("*").remove();
      if (WORLD_DATA.dashed_borders) {{
        WORLD_DATA.dashed_borders.forEach(db => {{
          dashedBordersLayer.append("path")
            .datum(db)
            .attr("class", "dashed-disputed")
            .attr("d", pathGenerator);
        }});
      }}

      // Graticule Edge Labels (60°N, 30°N, 0°, 30°S, 60°S & Longitudes)
      renderGraticuleLabels();

      // Ocean Labels
      renderOceanLabels();

      // Micronation Pins
      renderMicronationPins();

      // Country Labels
      renderCountryLabels();
      updateLabelStylesAndVisibility(currentZoomK);
    }}

    function renderGraticuleLabels() {{
      graticuleLabelsLayer.selectAll("*").remove();

      // 1. Latitude Edge Labels along Left and Right Sides (-60°, -30°, 0°, 30°, 60°)
      const latitudes = [-60, -30, 0, 30, 60];
      latitudes.forEach(lat => {{
        const latLabel = lat === 0 ? "0°" : (lat > 0 ? `${{lat}}°N` : `${{Math.abs(lat)}}°S`);

        // Left Side
        const ptLeft = projection([currentLon - 180, lat]);
        if (ptLeft && !isNaN(ptLeft[0]) && !isNaN(ptLeft[1])) {{
          graticuleLabelsLayer.append("text")
            .attr("class", "graticule-label")
            .attr("x", ptLeft[0] - 8)
            .attr("y", ptLeft[1])
            .attr("text-anchor", "end")
            .text(latLabel);
        }}

        // Right Side
        const ptRight = projection([currentLon + 180, lat]);
        if (ptRight && !isNaN(ptRight[0]) && !isNaN(ptRight[1])) {{
          graticuleLabelsLayer.append("text")
            .attr("class", "graticule-label")
            .attr("x", ptRight[0] + 8)
            .attr("y", ptRight[1])
            .attr("text-anchor", "start")
            .text(latLabel);
        }}
      }});

      // 2. Longitude Edge Labels along Top and Bottom (-120°, -60°, 0°, 60°, 120°)
      const lonOffsets = [-120, -60, 0, 60, 120];
      lonOffsets.forEach(offset => {{
        let rawLon = currentLon + offset;
        while (rawLon > 180) rawLon -= 360;
        while (rawLon < -180) rawLon += 360;

        let lonLabel = rawLon === 0 ? "0°" : (Math.abs(rawLon) === 180 ? "180°" : (rawLon > 0 ? `${{Math.round(rawLon)}}°E` : `${{Math.round(Math.abs(rawLon))}}°W`));

        // Top Edge
        const ptTop = projection([currentLon + offset, 86.5]);
        if (ptTop && !isNaN(ptTop[0]) && !isNaN(ptTop[1])) {{
          graticuleLabelsLayer.append("text")
            .attr("class", "graticule-label")
            .attr("x", ptTop[0])
            .attr("y", ptTop[1] - 8)
            .attr("text-anchor", "middle")
            .text(lonLabel);
        }}

        // Bottom Edge
        const ptBottom = projection([currentLon + offset, -86.5]);
        if (ptBottom && !isNaN(ptBottom[0]) && !isNaN(ptBottom[1])) {{
          graticuleLabelsLayer.append("text")
            .attr("class", "graticule-label")
            .attr("x", ptBottom[0])
            .attr("y", ptBottom[1] + 13)
            .attr("text-anchor", "middle")
            .text(lonLabel);
        }}
      }});
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

    function updateLabelStylesAndVisibility(k) {{
      const isMobile = window.innerWidth <= 768;

      // Base sizes on screen (in CSS pixels)
      // When zoomed in, font must REMAIN PROMINENT AND READABLE on mobile and desktop, NEVER microscopic!
      const baseProminentPx = isMobile ? 15.0 : 13.5;
      const baseStandardPx = isMobile ? 12.5 : 11.2;
      const baseDepPx = isMobile ? 11.0 : 9.8;
      const baseMicroPx = isMobile ? 10.5 : 9.5;

      // Zoom enhancement: as user zooms in, slightly enhance the font size (up to +2.2px) so countries like India remain bold and easy to read
      const zoomBoost = Math.min(2.2, Math.log2(Math.max(1, k)) * 0.55);

      const screenProminentPx = baseProminentPx + zoomBoost;
      const screenStandardPx = baseStandardPx + (zoomBoost * 0.4);
      const screenDepPx = baseDepPx + (zoomBoost * 0.3);
      const screenMicroPx = baseMicroPx + (zoomBoost * 0.3);

      const svgProminentFontSize = (screenProminentPx / k).toFixed(2) + "px";
      const svgCountryFontSize = (screenStandardPx / k).toFixed(2) + "px";
      const svgDepFontSize = (screenDepPx / k).toFixed(2) + "px";
      const svgMicroFontSize = (screenMicroPx / k).toFixed(2) + "px";

      const svgHaloStroke = ((isMobile ? 3.0 : 2.5) / k).toFixed(2) + "px";

      // Micronation pins: clamp radius to 4px on screen, NOT giant blobs!
      micronationLayer.style("display", k >= 2.4 ? "block" : "none");
      if (k >= 2.4) {{
        const pinScreenR = isMobile ? 4.2 : 3.8;
        micronationLayer.selectAll("circle.micronation-pin")
          .attr("r", (pinScreenR / k))
          .style("stroke-width", (1.2 / k) + "px");
      }}

      dashedBordersLayer.selectAll(".dashed-disputed")
        .style("stroke-width", (1.2 / k) + "px");

      const svgGraticuleFontSize = ((isMobile ? 9.5 : 8.5) / k).toFixed(2) + "px";
      graticuleLabelsLayer.selectAll(".graticule-label")
        .style("font-size", svgGraticuleFontSize)
        .style("stroke-width", (2.0 / k) + "px");

      const oceanScreenPx = isMobile ? 13.0 : 12.0;
      const svgOceanFontSize = (oceanScreenPx / k).toFixed(2) + "px";
      oceanLabelsLayer.selectAll(".ocean-label")
        .style("font-size", svgOceanFontSize);

      const placedBoxes = [];
      const labels = labelLayer.selectAll("text").nodes();

      // Strict Priority Ordering:
      // 1. Highlighted country always first
      // 2. Priority sovereigns in ranked order
      // 3. Other sovereign countries
      // 4. Dependencies
      // 5. Micronations
      labels.sort((a, b) => {{
        const nameA = a.getAttribute("data-name");
        const nameB = b.getAttribute("data-name");
        if (nameA === highlightedCountry) return -1;
        if (nameB === highlightedCountry) return 1;

        const aMicro = a.getAttribute("data-micro") === "true";
        const bMicro = b.getAttribute("data-micro") === "true";
        if (aMicro && !bMicro) return 1;
        if (!aMicro && bMicro) return -1;

        const aDep = a.getAttribute("data-dep") === "true";
        const bDep = b.getAttribute("data-dep") === "true";
        if (aDep && !bDep) return 1;
        if (!aDep && bDep) return -1;

        const idxA = prioritySovereigns.indexOf(nameA);
        const idxB = prioritySovereigns.indexOf(nameB);
        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
        if (idxA !== -1) return -1;
        if (idxB !== -1) return 1;

        return 0;
      }});

      const transform = d3.zoomTransform(svg.node());

      labels.forEach(node => {{
        const el = d3.select(node);
        const isMicro = el.attr("data-micro") === "true";
        const isDep = el.attr("data-dep") === "true";
        const name = el.attr("data-name");
        const isHighlighted = (name === highlightedCountry);
        const isProminent = prioritySovereigns.includes(name) || isHighlighted;

        if (isMicro) {{
          if (k < 2.4) {{
            el.style("display", "none");
            return;
          }}
          el.style("font-size", svgMicroFontSize)
            .style("stroke-width", svgHaloStroke);
        }} else if (isDep) {{
          if (k < 2.0) {{
            el.style("display", "none");
            return;
          }}
          el.style("font-size", svgDepFontSize)
            .style("stroke-width", svgHaloStroke);
        }} else if (isProminent) {{
          el.style("font-size", svgProminentFontSize)
            .style("stroke-width", svgHaloStroke);
        }} else {{
          el.style("font-size", svgCountryFontSize)
            .style("stroke-width", svgHaloStroke);
        }}

        const origX = parseFloat(el.attr("data-orig-x"));
        const origY = parseFloat(el.attr("data-orig-y"));
        
        const screenX = origX * transform.k + transform.x;
        const screenY = origY * transform.k + transform.y;

        // Cull offscreen labels
        if (screenX < -80 || screenX > width + 80 || screenY < -40 || screenY > height + 40) {{
          el.style("display", "none");
          return;
        }}

        const fontPx = isMicro ? screenMicroPx : (isDep ? screenDepPx : (isProminent ? screenProminentPx : screenStandardPx));
        const textLen = name.length;
        const boxW = textLen * fontPx * 0.58;
        const boxH = fontPx * 1.30;
        const padX = isMobile ? 8 : 6;
        const padY = isMobile ? 5 : 4;

        const curBox = {{
          x1: screenX - boxW / 2 - padX,
          x2: screenX + boxW / 2 + padX,
          y1: screenY - boxH / 2 - padY,
          y2: screenY + boxH / 2 + padY
        }};

        if (isHighlighted) {{
          el.style("display", "block");
          placedBoxes.push(curBox);
          return;
        }}

        let collides = false;
        for (let b of placedBoxes) {{
          if (!(curBox.x2 < b.x1 || curBox.x1 > b.x2 || curBox.y2 < b.y1 || curBox.y1 > b.y2)) {{
            collides = true;
            break;
          }}
        }}

        if (!collides) {{
          el.style("display", "block");
          placedBoxes.push(curBox);
        }} else {{
          el.style("display", "none");
        }}
      }});
    }}

    const tooltip = document.getElementById("tooltip");
    function handleMouseEnter(event, d) {{
      if (!window.matchMedia("(hover: hover)").matches) return;
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
      highlightedCountry = p.name;
      document.getElementById("country-search").value = p.name;
      renderGeometry();
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

    function centerOnTarget(targetName) {{
      if (!targetName) {{
        updateProjection();
        return;
      }}
      const query = targetName.trim().toLowerCase();

      const ocean = WORLD_DATA.oceans.find(o => o.name.toLowerCase() === query);
      if (ocean) {{
        highlightedCountry = null;
        const [lon, lat] = ocean.centroid;
        currentLon = Math.round(lon);
        currentLat = Math.round(lat);
        syncControls();
        updateProjection();
        return;
      }}

      const target = WORLD_DATA.features.find(f => f.properties.name.toLowerCase() === query);
      if (target) {{
        highlightedCountry = target.properties.name;
        const [lon, lat] = target.properties.centroid;
        currentLon = Math.round(lon);
        currentLat = Math.round(lat);
        syncControls();
        updateProjection();
        showInfoCard(target.properties);
        return;
      }}

      // If query does not match any ocean or feature, still ensure map is projected and rendered!
      updateProjection();
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

    // Mobile controls toggle drawer
    const mobileToggleBtn = document.getElementById("mobile-toggle-btn");
    const controlsStrip = document.getElementById("controls-strip");
    const toggleChevron = document.getElementById("toggle-chevron");

    if (mobileToggleBtn) {{
      mobileToggleBtn.addEventListener("click", () => {{
        const isOpen = controlsStrip.classList.toggle("open");
        toggleChevron.textContent = isOpen ? "▴" : "▾";
      }});
    }}

    // RESET BUTTON: Clear highlighted country, return to 0 lon, 0 lat, NO country highlighted!
    document.getElementById("reset-btn").addEventListener("click", () => {{
      highlightedCountry = null; // No country highlighted!
      currentLon = 0.0;
      currentLat = 0.0;
      currentZoomK = 1.0;
      syncControls();
      document.getElementById("country-search").value = "";
      document.getElementById("info-panel").style.display = "none";
      updateProjection();
      svg.transition().duration(350).call(zoom.transform, d3.zoomIdentity);
    }});

    // --- HIGH QUALITY EXPORT FUNCTIONS ---

    // 1. Standalone Clean SVG String Generator (embedded styles & background rect)
    function generateCleanSvgString() {{
      const svgEl = document.getElementById("map-svg");
      const clone = svgEl.cloneNode(true);
      clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");

      // Insert explicit background rectangle at top of SVG so it never renders black/transparent
      const bgRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      bgRect.setAttribute("width", "100%");
      bgRect.setAttribute("height", "100%");
      bgRect.setAttribute("fill", "#d8ecf8");
      clone.insertBefore(bgRect, clone.firstChild);

      // Embedded full standalone stylesheet inside SVG
      const styleEl = document.createElementNS("http://www.w3.org/2000/svg", "style");
      styleEl.textContent = `
        .ocean-sphere {{ fill: #d8ecf8; stroke: #94a3b8; stroke-width: 0.8px; }}
        .graticule {{ fill: none; stroke: #c8deec; stroke-width: 0.5px; stroke-dasharray: 2, 3; }}
        .graticule-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 8.5px; font-weight: 600; fill: #64748b; stroke: #ffffff; stroke-width: 2.2px; stroke-linejoin: round; paint-order: stroke fill; dominant-baseline: central; }}
        .country {{ fill: #ffffff; stroke: #94a3b8; stroke-width: 0.55px; }}
        .country.highlighted {{ fill: #fef3c7 !important; stroke: #d97706 !important; stroke-width: 1.4px !important; }}
        .dashed-disputed {{ fill: none; stroke: #718096; stroke-width: 1.1px; stroke-dasharray: 3.5, 3.0; stroke-linecap: round; }}
        .micronation-pin {{ fill: #e11d48; stroke: #ffffff; stroke-width: 1.5px; }}
        .country-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; font-weight: 700; fill: #0f172a; stroke: #ffffff; stroke-width: 2.8px; paint-order: stroke fill; text-anchor: middle; }}
        .ocean-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11.5px; font-style: italic; font-weight: 700; letter-spacing: 3.5px; fill: #3f7893; text-anchor: middle; }}
      `;
      clone.insertBefore(styleEl, clone.firstChild);

      const serializer = new XMLSerializer();
      return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\\n' + serializer.serializeToString(clone);
    }}

    // Export SVG
    document.getElementById("export-svg-btn").addEventListener("click", () => {{
      const svgString = generateCleanSvgString();
      const blob = new Blob([svgString], {{ type: "image/svg+xml;charset=utf-8" }});
      const url = URL.createObjectURL(blob);
      const dl = document.createElement("a");
      dl.href = url;
      dl.download = `equal_earth_lon${{currentLon}}_lat${{currentLat}}.svg`;
      document.body.appendChild(dl);
      dl.click();
      document.body.removeChild(dl);
      URL.revokeObjectURL(url);
    }});

    // Helper: Rasterize SVG to high-res HTML5 Canvas
    function rasterizeToCanvas(callback, scale = 2.0) {{
      const svgString = generateCleanSvgString();
      const blob = new Blob([svgString], {{ type: "image/svg+xml;charset=utf-8" }});
      const url = URL.createObjectURL(blob);

      const img = new Image();
      img.onload = () => {{
        const canvas = document.createElement("canvas");
        canvas.width = width * scale;
        canvas.height = height * scale;
        const ctx = canvas.getContext("2d");

        // Background
        ctx.fillStyle = "#d8ecf8";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw image scaled
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        URL.revokeObjectURL(url);
        callback(canvas);
      }};
      img.src = url;
    }}

    // Export High-Quality JPEG
    document.getElementById("export-jpg-btn").addEventListener("click", () => {{
      rasterizeToCanvas((canvas) => {{
        canvas.toBlob((blob) => {{
          const url = URL.createObjectURL(blob);
          const dl = document.createElement("a");
          dl.href = url;
          dl.download = `equal_earth_lon${{currentLon}}_lat${{currentLat}}.jpg`;
          document.body.appendChild(dl);
          dl.click();
          document.body.removeChild(dl);
          URL.revokeObjectURL(url);
        }}, "image/jpeg", 0.95);
      }}, 2.0);
    }});

    // Export PDF
    document.getElementById("export-pdf-btn").addEventListener("click", () => {{
      rasterizeToCanvas((canvas) => {{
        if (window.jspdf && window.jspdf.jsPDF) {{
          const {{ jsPDF }} = window.jspdf;
          const pdf = new jsPDF({{
            orientation: "landscape",
            unit: "pt",
            format: [width, height]
          }});
          const imgData = canvas.toDataURL("image/jpeg", 0.95);
          pdf.addImage(imgData, "JPEG", 0, 0, width, height);
          pdf.save(`equal_earth_lon${{currentLon}}_lat${{currentLat}}.pdf`);
        }} else {{
          // Fallback to direct print/PDF
          window.print();
        }}
      }}, 2.0);
    }});

    // Initial Start: ALWAYS render map immediately so it loads on initial site visit without requiring reset!
    updateProjection();

    if (initialCountryObj) {{
      document.getElementById("country-search").value = initialCountryObj.properties.name;
      centerOnTarget(initialCountryObj.properties.name);
    }} else {{
      const initialOceanObj = (INITIAL_TARGET && INITIAL_TARGET !== "World" && !INITIAL_TARGET.startsWith("Custom"))
        ? WORLD_DATA.oceans.find(o => o.name.toLowerCase() === INITIAL_TARGET.trim().toLowerCase())
        : null;

      if (initialOceanObj) {{
        document.getElementById("country-search").value = initialOceanObj.name;
        centerOnTarget(initialOceanObj.name);
      }} else {{
        document.getElementById("country-search").value = "";
      }}
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

    # Also sync root index.html for GitHub Pages
    with open(ROOT_INDEX, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n[+] Interactive Equal Earth web map generated: {HTML_OUTPUT}")
    return HTML_OUTPUT


def generate_static_png(lon, lat, target_name, output_path=None, show_labels=True):
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

        # 1. Countries (Highlight ONLY target country if specified)
        for feat in world_data["features"]:
            geom = shape(feat["geometry"])
            name = feat["properties"]["name"]

            is_target = (target_name and target_name != "World" and name.lower() == target_name.lower())

            if is_target:
                face = "#fef3c7"
                edge = "#d97706"
                lw = 1.3
            else:
                face = "#ffffff"
                edge = "#94a3b8"
                lw = 0.45

            ax.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor=face, edgecolor=edge, linewidth=lw)

        # 2. Light Dashed Disputed Borders (Kosovo/Serbia, Morocco/SADR, Bir Tawil)
        for db in world_data.get("dashed_borders", []):
            geom = shape(db["geometry"])
            ax.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor="none",
                              edgecolor="#718096", linewidth=1.0, linestyle="--", alpha=0.9)

        # 3. Ocean Labels (if enabled)
        if show_labels:
            for ocean in world_data.get("oceans", []):
                pt = ocean["centroid"]
                ax.text(pt[0], pt[1], ocean["label"], transform=ccrs.PlateCarree(),
                        fontsize=8.5, fontstyle="italic", color="#3f7893", ha="center", va="center",
                        fontweight="bold")

        # 4. BOLD Country Labels (if enabled)
        if show_labels:
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
        gl.top_labels = True
        gl.bottom_labels = True
        gl.left_labels = True
        gl.right_labels = True
        gl.xlabel_style = {"size": 8, "color": "#64748b"}
        gl.ylabel_style = {"size": 8, "color": "#64748b"}

        label_note = "" if show_labels else " (Unlabelled Outline)"
        title_suffix = f" · Centered on {target_name} ({lon:+.1f}°E, {lat:+.1f}°N)" if target_name != "World" else f" · Centered at Lon {lon:+.1f}°"
        plt.title(f"Equal Earth Projection{title_suffix}{label_note}\n(Survey of India Official Sovereign Boundaries & Google Maps Format)",
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
    parser.add_argument("--satellite", action="store_true", help="Open Topographic Satellite & Real-Time Day/Night View in browser")
    args = parser.parse_args()

    if args.satellite:
        sat_html = BASE_DIR / "satellite_day_night.html"
        if not sat_html.exists():
            from build_satellite import generate_satellite_html
            generate_satellite_html()
        print("[*] Opening Topographic Satellite & Real-Time Day/Night View...")
        webbrowser.open(f"file://{sat_html.resolve()}")
        return

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
            lon_in = input("Enter central longitude [-180 to 180] (default 0.0): ").strip() or "0.0"
            lat_in = input("Enter central latitude [-90 to 90] (default 0.0): ").strip() or "0.0"
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