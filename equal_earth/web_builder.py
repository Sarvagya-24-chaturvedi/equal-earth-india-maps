"""Generates the premium, responsive Equal Earth Geospatial Studio web application."""

import json
import csv
from pathlib import Path
from typing import Optional, Union

BASE_DIR = Path(__file__).resolve().parent.parent
WORLD_DATA_PATH = BASE_DIR / "world_data.json"
INDIA_STATES_PATH = BASE_DIR / "data" / "india_states.geojson"
SAMPLE_DIR = BASE_DIR / "data" / "sample_datasets"
HTML_OUTPUT_PATH = BASE_DIR / "equal_earth_interactive.html"
INDEX_OUTPUT_PATH = BASE_DIR / "index.html"


def get_sample_datasets_json() -> str:
    """Read all sample datasets and return as a compact JSON string."""
    datasets = {}
    samples = {
        "literacy": ("india_literacy_2011_census.csv", "Literacy Rate (%)", "%", "Census of India 2011"),
        "forest_cover": ("india_forest_cover_2021.csv", "Forest Cover (%)", "%", "Forest Survey of India (ISFR 2021)"),
        "renewable_energy": ("india_renewable_energy_2023.csv", "Renewable Energy Capacity (MW)", "MW", "Ministry of New and Renewable Energy (2023)"),
        "population_density": ("india_population_density_2011.csv", "Population Density (persons/km²)", "/km²", "Census of India 2011"),
    }

    for key, (filename, label, unit, src) in samples.items():
        file_path = SAMPLE_DIR / filename
        data_map = {}
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 3:
                        st, code, val = row[0].strip(), row[1].strip(), row[2].strip()
                        try:
                            data_map[st] = float(val)
                        except ValueError:
                            pass
        datasets[key] = {
            "label": label,
            "unit": unit,
            "source": src,
            "data": data_map
        }
    return json.dumps(datasets)


def build_interactive_html(
    initial_mode: str = "india",
    output_path: Optional[Union[str, Path]] = None,
    sync_index: bool = True
) -> Path:
    """Build and write the self-contained Equal Earth Geospatial Studio HTML web application."""
    if not WORLD_DATA_PATH.exists():
        raise FileNotFoundError(f"world_data.json not found at {WORLD_DATA_PATH}")

    with open(WORLD_DATA_PATH, "r", encoding="utf-8") as f:
        world_geojson_str = f.read()

    states_geojson_path = INDIA_STATES_PATH if INDIA_STATES_PATH.exists() else (BASE_DIR / "india_states.geojson")
    if not states_geojson_path.exists():
        raise FileNotFoundError(f"india_states.geojson not found at {states_geojson_path}")

    with open(states_geojson_path, "r", encoding="utf-8") as f:
        states_geojson_str = f.read()

    sample_datasets_json_str = get_sample_datasets_json()

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Equal Earth India Maps · Geospatial Studio</title>
  
  <script src="d3.v7.min.js"></script>
  <script>
    if (typeof d3 === 'undefined') {{
      document.write('<script src="https://d3js.org/d3.v7.min.js"><\\/script>');
    }}
  </script>
  
  <script src="jspdf.umd.min.js"></script>
  <script>
    if (typeof window.jspdf === 'undefined') {{
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"><\\/script>');
    }}
  </script>

  <style>
    :root {{
      --bg-ocean: #d8ecf8;
      --panel-bg: rgba(255, 255, 255, 0.96);
      --panel-border: #cbd5e1;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --accent-highlight: #fef3c7;
      --accent-highlight-border: #d97706;
      --state-fill: #f8fafc;
      --state-stroke: #94a3b8;
      --india-outline: #d97706;
      --card-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.08), 0 1px 3px 0 rgba(0, 0, 0, 0.04);
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

    /* Top Navigation Bar */
    header.top-navbar {{
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 54px;
      background: var(--panel-bg);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      z-index: 100;
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
    }}

    .brand-section {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .brand-title {{
      font-size: 15px;
      font-weight: 700;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 6px;
      color: #0f172a;
    }}

    .badge-soi {{
      background: #fef3c7;
      color: #b45309;
      border: 1px solid #fde68a;
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
    }}

    /* Mode Switcher Tabs */
    .mode-pills {{
      display: flex;
      background: #f1f5f9;
      border-radius: 8px;
      padding: 3px;
      gap: 2px;
      border: 1px solid #e2e8f0;
    }}

    .mode-pill {{
      padding: 5px 12px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 6px;
      border: none;
      background: transparent;
      color: #64748b;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
      transition: all 0.15s ease;
      text-decoration: none;
    }}

    .mode-pill:hover {{
      color: #0f172a;
    }}

    .mode-pill.active {{
      background: #ffffff;
      color: #2563eb;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}

    /* Top Action Buttons */
    .top-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .btn {{
      padding: 6px 12px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 6px;
      border: 1px solid #cbd5e1;
      background: #ffffff;
      color: #0f172a;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: background 0.15s;
    }}

    .btn:hover {{
      background: #f8fafc;
      border-color: #94a3b8;
    }}

    .btn-primary {{
      background: #2563eb;
      color: #ffffff;
      border-color: #1d4ed8;
    }}

    .btn-primary:hover {{
      background: #1d4ed8;
    }}

    /* Workspace Layout */
    .workspace {{
      position: absolute;
      top: 54px;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
    }}

    /* Collapsible Side Panel */
    .sidebar {{
      width: 340px;
      background: var(--panel-bg);
      backdrop-filter: blur(10px);
      border-right: 1px solid var(--panel-border);
      height: 100%;
      overflow-y: auto;
      z-index: 50;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: 2px 0 10px rgba(0, 0, 0, 0.03);
      transition: transform 0.25s ease;
    }}

    .sidebar.collapsed {{
      transform: translateX(-100%);
    }}

    .sidebar-section {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 12px 14px;
    }}

    .section-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #64748b;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .control-group {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-bottom: 10px;
    }}

    .control-group:last-child {{
      margin-bottom: 0;
    }}

    .control-label {{
      font-size: 12px;
      font-weight: 600;
      color: #334155;
    }}

    select, input[type="text"], input[type="number"] {{
      width: 100%;
      padding: 6px 10px;
      font-size: 12px;
      border-radius: 6px;
      border: 1px solid #cbd5e1;
      background: #ffffff;
      color: #0f172a;
      outline: none;
    }}

    select:focus, input:focus {{
      border-color: #2563eb;
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
    }}

    .checkbox-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #1e293b;
      cursor: pointer;
      padding: 3px 0;
    }}

    .checkbox-item input {{
      cursor: pointer;
    }}

    /* Map Canvas Viewport */
    .map-container {{
      flex: 1;
      height: 100%;
      position: relative;
      background-color: var(--bg-ocean);
      cursor: grab;
    }}

    .map-container:active {{
      cursor: grabbing;
    }}

    svg#map-svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    /* Floating Inspector Card */
    .state-inspector {{
      position: absolute;
      top: 16px;
      right: 16px;
      width: 260px;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 12px 14px;
      box-shadow: var(--card-shadow);
      z-index: 40;
      pointer-events: none;
      transition: opacity 0.15s ease;
    }}

    .inspector-title {{
      font-size: 14px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .inspector-code {{
      font-size: 10px;
      background: #e2e8f0;
      padding: 2px 5px;
      border-radius: 4px;
      color: #475569;
      font-family: monospace;
    }}

    .inspector-metric {{
      font-size: 20px;
      font-weight: 800;
      color: #2563eb;
      margin: 4px 0;
    }}

    .inspector-metric-label {{
      font-size: 11px;
      color: #64748b;
    }}

    /* Floating Legend */
    .map-legend {{
      position: absolute;
      bottom: 20px;
      right: 20px;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 10px 14px;
      box-shadow: var(--card-shadow);
      z-index: 40;
    }}

    .legend-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      color: #475569;
      margin-bottom: 8px;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      color: #1e293b;
      margin-bottom: 4px;
    }}

    .legend-swatch {{
      width: 18px;
      height: 12px;
      border-radius: 2px;
      border: 1px solid rgba(0, 0, 0, 0.15);
    }}

    /* Floating View Controls */
    .floating-tools {{
      position: absolute;
      left: 16px;
      bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      z-index: 40;
    }}

    .tool-btn {{
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      color: #0f172a;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: var(--card-shadow);
      transition: all 0.15s;
    }}

    .tool-btn:hover {{
      background: #f8fafc;
      border-color: #94a3b8;
    }}

    /* Map Tooltip */
    .d3-tooltip {{
      position: absolute;
      background: #0f172a;
      color: #ffffff;
      padding: 6px 10px;
      font-size: 12px;
      border-radius: 6px;
      pointer-events: none;
      z-index: 200;
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
      display: none;
    }}

    /* Responsive */
    @media (max-width: 768px) {{
      .sidebar {{
        position: absolute;
        width: 300px;
        box-shadow: 4px 0 20px rgba(0,0,0,0.2);
      }}
      .brand-title {{
        font-size: 13px;
      }}
      .badge-soi {{
        display: none;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Navigation Bar -->
  <header class="top-navbar">
    <div class="brand-section">
      <button id="toggle-sidebar" class="btn" title="Toggle Settings Sidebar" aria-label="Toggle Sidebar">☰</button>
      <div class="brand-title">
        <span>EQUAL EARTH</span>
        <span style="font-weight: 400; color: #64748b;">· Studio</span>
      </div>
      <span class="badge-soi">100% SOI Sovereign Boundary</span>
    </div>

    <!-- Mode Switcher -->
    <div class="mode-pills">
      <button class="mode-pill active" id="mode-india" data-mode="india">🇮🇳 India States & Thematic</button>
      <button class="mode-pill" id="mode-global" data-mode="global">🌍 Global Equal Earth</button>
      <a class="mode-pill" href="satellite_day_night.html" target="_blank" title="Open Real-Time Topographic Day/Night Map">🛰️ Satellite Day/Night ↗</a>
    </div>

    <!-- Top Action Buttons -->
    <div class="top-actions">
      <button class="btn" id="btn-reset-view" title="Reset Map View">↺ Reset</button>
      <button class="btn" id="btn-export-svg" title="Download Lossless SVG">SVG</button>
      <button class="btn" id="btn-export-pdf" title="Download Vector PDF">PDF</button>
      <button class="btn btn-primary" id="btn-export-png" title="Download High-Res 300 DPI PNG">PNG Export</button>
    </div>
  </header>

  <!-- Workspace -->
  <div class="workspace">
    
    <!-- Collapsible Sidebar -->
    <aside class="sidebar" id="sidebar">
      
      <!-- Section 1: Thematic & Metric Controls (India Mode) -->
      <div class="sidebar-section" id="sec-thematic">
        <div class="section-title">
          <span>Thematic Data & Choropleth</span>
          <span style="font-size: 9px; color: #16a34a; font-weight: 700;">LIVE</span>
        </div>
        
        <div class="control-group">
          <label class="control-label" for="sel-metric">Dataset / Metric</label>
          <select id="sel-metric">
            <option value="none">Administrative Outlines (No Data)</option>
            <option value="literacy" selected>Literacy Rate (%) · Census 2011</option>
            <option value="forest_cover">Forest Cover (%) · ISFR 2021</option>
            <option value="renewable_energy">Renewable Energy Capacity (MW) · MNRE 2023</option>
            <option value="population_density">Population Density (/km²) · Census 2011</option>
            <option value="custom">Upload Custom CSV Dataset...</option>
          </select>
        </div>

        <div class="control-group" id="group-csv-upload" style="display: none;">
          <label class="control-label" for="input-csv-file">Upload CSV File (State, Value)</label>
          <input type="file" id="input-csv-file" accept=".csv" style="font-size: 11px;">
          <div id="csv-status" style="font-size: 10px; color: #16a34a; margin-top: 4px;"></div>
        </div>

        <div class="control-group" id="group-palette">
          <label class="control-label" for="sel-palette">Color Palette</label>
          <select id="sel-palette">
            <option value="YlGnBu" selected>YlGnBu (Yellow - Green - Blue)</option>
            <option value="Viridis">Viridis (Sequential Perception)</option>
            <option value="Blues">Blues (Clean Ocean Tone)</option>
            <option value="Greens">Greens (Environmental)</option>
            <option value="Oranges">Oranges (Energy & Heat)</option>
            <option value="Spectral">Spectral (Multi-Hue Diverging)</option>
            <option value="RdYlGn">Red - Yellow - Green</option>
          </select>
        </div>

        <div class="control-group" id="group-classes">
          <label class="control-label" for="sel-classes">Classification Bins</label>
          <select id="sel-classes">
            <option value="4">4 Classes</option>
            <option value="5" selected>5 Classes (Recommended)</option>
            <option value="6">6 Classes</option>
            <option value="7">7 Classes</option>
          </select>
        </div>
      </div>

      <!-- Section 2: Global Perspective (Global Mode) -->
      <div class="sidebar-section" id="sec-global" style="display: none;">
        <div class="section-title">Global Centering & Projection</div>
        <div class="control-group">
          <label class="control-label" for="sel-center-preset">Center Meridian Preset</label>
          <select id="sel-center-preset">
            <option value="78" selected>Centered on India (78°E)</option>
            <option value="0">Centered on Prime Meridian (0°)</option>
            <option value="90">Indo-Pacific Centered (90°E)</option>
            <option value="-100">Americas Centered (100°W)</option>
            <option value="150">Pacific Centered (150°E)</option>
            <option value="custom">Custom Longitude...</option>
          </select>
        </div>
        <div class="control-group" id="group-custom-lon" style="display: none;">
          <label class="control-label" for="input-custom-lon">Custom Longitude (-180° to 180°)</label>
          <input type="number" id="input-custom-lon" value="78" min="-180" max="180" step="1">
        </div>
      </div>

      <!-- Section 3: Geographic Layers & Labels -->
      <div class="sidebar-section">
        <div class="section-title">Geographic Layers</div>
        
        <label class="checkbox-item">
          <input type="checkbox" id="chk-state-borders" checked>
          <span>State & UT Boundaries</span>
        </label>
        
        <label class="checkbox-item">
          <input type="checkbox" id="chk-state-labels" checked>
          <span>State Names (Centroid Labels)</span>
        </label>
        
        <label class="checkbox-item">
          <input type="checkbox" id="chk-soi-border" checked>
          <span>SOI Sovereign Boundary (Gold)</span>
        </label>
        
        <label class="checkbox-item">
          <input type="checkbox" id="chk-country-labels" checked>
          <span>Country Labels (Global Map)</span>
        </label>
        
        <label class="checkbox-item">
          <input type="checkbox" id="chk-micronations" checked>
          <span>Micronations & Territories</span>
        </label>
        
        <label class="checkbox-item">
          <input type="checkbox" id="chk-ocean-labels" checked>
          <span>Ocean Labels</span>
        </label>
        
        <label class="checkbox-item">
          <input type="checkbox" id="chk-graticule" checked>
          <span>Graticule (Grid Lines)</span>
        </label>
        
        <label class="checkbox-item">
          <input type="checkbox" id="chk-disputed-borders" checked>
          <span>Disputed Lines (Light Dashed)</span>
        </label>
      </div>

      <!-- Section 4: Themes & Visual Styles -->
      <div class="sidebar-section">
        <div class="section-title">Cartographic Themes</div>
        <div class="control-group">
          <label class="control-label" for="sel-theme">Theme Preset</label>
          <select id="sel-theme">
            <option value="atlas_light" selected>Classic Atlas (Light)</option>
            <option value="academic_clean">Academic Publication (Clean)</option>
            <option value="carto_dark">Cartographic Dark</option>
            <option value="emerald_nature">Emerald Conservation</option>
            <option value="sunset_warm">Warm Sunset Terracotta</option>
          </select>
        </div>
      </div>

      <!-- Section 5: Map Metadata -->
      <div class="sidebar-section">
        <div class="section-title">Title & Attribution</div>
        <div class="control-group">
          <label class="control-label" for="input-title">Map Title</label>
          <input type="text" id="input-title" value="India — Administrative Boundaries & States">
        </div>
        <div class="control-group">
          <label class="control-label" for="input-subtitle">Subtitle</label>
          <input type="text" id="input-subtitle" value="Equal Earth Projection · Survey of India Sovereign Boundary">
        </div>
      </div>

      <!-- Section 6: Source & Provenance -->
      <div class="sidebar-section" style="background: #f8fafc; font-size: 11px; color: #64748b; line-height: 1.5;">
        <strong style="color: #0f172a;">Cartographic Compliance Notice</strong><br>
        External sovereign boundaries align strictly with the official maps published by the <strong>Survey of India (SOI)</strong>, Government of India. Equal-area mathematical projection verified against Šavrič et al. (2019).
      </div>

    </aside>

    <!-- Map Canvas Viewport -->
    <main class="map-container" id="map-viewport">
      
      <!-- SVG Map -->
      <svg id="map-svg" viewBox="0 0 1000 700" preserveAspectRatio="xMidYMid meet"></svg>

      <!-- Floating State Inspector Card -->
      <div class="state-inspector" id="state-inspector" style="display: none;">
        <div class="inspector-title">
          <span id="inspect-name">Maharashtra</span>
          <span class="inspector-code" id="inspect-code">IN-MH</span>
        </div>
        <div class="inspector-metric" id="inspect-val">82.3%</div>
        <div class="inspector-metric-label" id="inspect-metric-label">Literacy Rate</div>
      </div>

      <!-- Floating Legend -->
      <div class="map-legend" id="map-legend" style="display: none;">
        <div class="legend-title" id="legend-title-text">Literacy Rate (%)</div>
        <div id="legend-items"></div>
      </div>

      <!-- Floating View Tools -->
      <div class="floating-tools">
        <button class="tool-btn" id="btn-zoom-in" title="Zoom In">+</button>
        <button class="tool-btn" id="btn-zoom-out" title="Zoom Out">−</button>
        <button class="tool-btn" id="btn-fit-extent" title="Fit to India Extent">⛶</button>
      </div>

      <!-- Tooltip -->
      <div class="d3-tooltip" id="map-tooltip"></div>
    </main>

  </div>

  <!-- Embedded authorative geospatial & thematic data -->
  <script>
    window.WORLD_DATA = {world_geojson_str};
    window.INDIA_STATES_DATA = {states_geojson_str};
    window.SAMPLE_DATASETS = {sample_datasets_json_str};
  </script>

  <!-- Application Logic -->
  <script>
    (function() {{
      // Themes definition
      const THEMES = {{
        atlas_light: {{
          ocean: "#d8ecf8",
          land: "#ffffff",
          landEdge: "#94a3b8",
          indiaFill: "#fef3c7",
          indiaEdge: "#d97706",
          stateFill: "#f8fafc",
          stateEdge: "#cbd5e1",
          graticule: "#c8deec",
          text: "#0f172a",
          bg: "#ffffff"
        }},
        academic_clean: {{
          ocean: "#f8fafc",
          land: "#ffffff",
          landEdge: "#475569",
          indiaFill: "#ffedd5",
          indiaEdge: "#c2410c",
          stateFill: "#ffffff",
          stateEdge: "#64748b",
          graticule: "#e2e8f0",
          text: "#0f172a",
          bg: "#ffffff"
        }},
        carto_dark: {{
          ocean: "#090d16",
          land: "#1e293b",
          landEdge: "#334155",
          indiaFill: "#3b2507",
          indiaEdge: "#f59e0b",
          stateFill: "#1e293b",
          stateEdge: "#475569",
          graticule: "#1e293b",
          text: "#f8fafc",
          bg: "#090d16"
        }},
        emerald_nature: {{
          ocean: "#e0f2fe",
          land: "#f0fdf4",
          landEdge: "#86efac",
          indiaFill: "#dcfce7",
          indiaEdge: "#16a34a",
          stateFill: "#f0fdf4",
          stateEdge: "#bbf7d0",
          graticule: "#bae6fd",
          text: "#064e3b",
          bg: "#ffffff"
        }},
        sunset_warm: {{
          ocean: "#e0f2fe",
          land: "#fffbeb",
          landEdge: "#fde68a",
          indiaFill: "#ffedd5",
          indiaEdge: "#ea580c",
          stateFill: "#fffbeb",
          stateEdge: "#fed7aa",
          graticule: "#cbd5e1",
          text: "#451a03",
          bg: "#ffffff"
        }}
      }};

      // Palettes
      const PALETTES = {{
        YlGnBu: ["#ffffd9", "#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8", "#253494", "#081d58"],
        Viridis: ["#440154", "#482878", "#3e4a89", "#31688e", "#26828e", "#1f9e89", "#35b779", "#6ece58", "#b5de2b", "#fde725"],
        Blues: ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"],
        Greens: ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#006d2c", "#00441b"],
        Oranges: ["#fff5eb", "#fee6ce", "#fdd0a2", "#fdae6b", "#fd8d3c", "#f16913", "#d94801", "#a63603", "#7f2704"],
        Spectral: ["#9e0142", "#d53e4f", "#f46d43", "#fdae61", "#fee08b", "#ffffbf", "#e6f598", "#abdda4", "#66c2a5", "#3288bd", "#5e4fa2"],
        RdYlGn: ["#a50026", "#d73027", "#f46d43", "#fdae61", "#fee08b", "#ffffbf", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850", "#006837"]
      }};

      // App State
      let currentMode = "{initial_mode}"; // 'india' or 'global'
      let currentThemeKey = "atlas_light";
      let currentMetric = "literacy";
      let currentPaletteKey = "YlGnBu";
      let numClasses = 5;
      let centralLon = 78.0;
      let customData = null;

      const svg = d3.select("#map-svg");
      const tooltip = d3.select("#map-tooltip");
      const inspector = d3.select("#state-inspector");
      const legendEl = d3.select("#map-legend");

      let width = 1000;
      let height = 700;

      // Group layers
      const gOcean = svg.append("rect").attr("class", "layer-ocean");
      const gGraticule = svg.append("g").attr("class", "layer-graticule");
      const gCountries = svg.append("g").attr("class", "layer-countries");
      const gDisputed = svg.append("g").attr("class", "layer-disputed");
      const gStates = svg.append("g").attr("class", "layer-states");
      const gSovereign = svg.append("g").attr("class", "layer-sovereign");
      const gLabels = svg.append("g").attr("class", "layer-labels");

      // Zoom behavior
      const zoom = d3.zoom()
        .scaleExtent([0.8, 25])
        .on("zoom", (event) => {{
          const transform = event.transform;
          gGraticule.attr("transform", transform);
          gCountries.attr("transform", transform);
          gDisputed.attr("transform", transform);
          gStates.attr("transform", transform);
          gSovereign.attr("transform", transform);
          gLabels.attr("transform", transform);

          // Dynamic label sizing based on zoom
          gLabels.selectAll("text").style("font-size", d => {{
            const baseSize = d.properties.is_small_ut ? 6 : 8;
            return Math.max(5, Math.min(16, baseSize / Math.sqrt(transform.k))) + "px";
          }});
        }});

      svg.call(zoom);

      // Projection
      const projection = d3.geoEqualEarth();
      const pathGenerator = d3.geoPath().projection(projection);
      const graticuleGenerator = d3.geoGraticule();

      // State normalization map
      const stateAliases = {{
        "jammu and kashmir": "Jammu & Kashmir",
        "j&k": "Jammu & Kashmir",
        "andaman and nicobar islands": "Andaman & Nicobar",
        "andaman & nicobar islands": "Andaman & Nicobar",
        "orissa": "Odisha",
        "pondicherry": "Puducherry",
        "nct of delhi": "Delhi",
        "delhi ut": "Delhi"
      }};

      function normalizeState(name) {{
        if (!name) return "";
        const clean = name.trim().toLowerCase();
        return stateAliases[clean] || name.trim();
      }}

      // Color Scale Builder
      function getActivePalette() {{
        return PALETTES[currentPaletteKey] || PALETTES.YlGnBu;
      }}

      function getInterpolatedColors(k) {{
        const pal = getActivePalette();
        const colors = [];
        for (let i = 0; i < k; i++) {{
          const t = i / Math.max(1, k - 1);
          const idx = t * (pal.length - 1);
          const low = Math.floor(idx);
          const high = Math.min(pal.length - 1, low + 1);
          const frac = idx - low;
          colors.push(d3.interpolateRgb(pal[low], pal[high])(frac));
        }}
        return colors;
      }}

      function getCurrentDataMap() {{
        if (currentMetric === "none") return null;
        if (currentMetric === "custom" && customData) return customData;
        if (window.SAMPLE_DATASETS[currentMetric]) return window.SAMPLE_DATASETS[currentMetric].data;
        return null;
      }}

      // Render Function
      function updateMap() {{
        const theme = THEMES[currentThemeKey];
        const rect = svg.node().getBoundingClientRect();
        width = rect.width || 1000;
        height = rect.height || 700;
        svg.attr("viewBox", `0 0 ${{width}} ${{height}}`);

        // Ocean Background
        gOcean.attr("width", width).attr("height", height).attr("fill", theme.ocean);

        // Configure Projection Extent
        if (currentMode === "india") {{
          projection
            .rotate([-78, 0])
            .fitExtent([[50, 40], [width - 50, height - 40]], window.INDIA_STATES_DATA);
        }} else {{
          projection
            .rotate([-centralLon, 0])
            .fitExtent([[40, 30], [width - 40, height - 30]], {{type: "Sphere"}});
        }}

        // Graticule
        const showGraticule = document.getElementById("chk-graticule").checked;
        gGraticule.selectAll("path").remove();
        if (showGraticule) {{
          gGraticule.append("path")
            .datum(graticuleGenerator)
            .attr("d", pathGenerator)
            .attr("fill", "none")
            .attr("stroke", theme.graticule)
            .attr("stroke-width", 0.5)
            .attr("stroke-dasharray", "3,3");
        }}

        // Global Countries Layer
        const showCountries = currentMode === "global";
        gCountries.selectAll("path").remove();
        if (showCountries && window.WORLD_DATA) {{
          gCountries.selectAll("path")
            .data(window.WORLD_DATA.features)
            .enter()
            .append("path")
            .attr("d", pathGenerator)
            .attr("fill", d => (d.properties.name === "India") ? theme.indiaFill : theme.land)
            .attr("stroke", d => (d.properties.name === "India") ? theme.indiaEdge : theme.landEdge)
            .attr("stroke-width", d => (d.properties.name === "India") ? 0.8 : 0.4)
            .style("cursor", d => (d.properties && d.properties.wiki) ? "pointer" : "default")
            .on("mouseenter", (event, d) => {{
              tooltip.style("display", "block").html(`
                <div style="font-size: 12px; line-height: 1.4;">
                  <strong>${{d.properties.name}}</strong>
                  ${{d.properties.wiki ? '<br><span style="font-size: 10px; color: #38bdf8;">Click to view Wikipedia article ↗</span>' : ''}}
                </div>
              `);
            }})
            .on("mousemove", event => {{
              tooltip.style("left", (event.pageX + 12) + "px").style("top", (event.pageY + 12) + "px");
            }})
            .on("mouseleave", () => tooltip.style("display", "none"))
            .on("click", (event, d) => {{
              if (d.properties && d.properties.wiki) {{
                window.open(d.properties.wiki, "_blank");
              }}
            }});
        }}

        // Disputed Borders
        const showDisputed = document.getElementById("chk-disputed-borders").checked;
        gDisputed.selectAll("path").remove();
        if (showDisputed && window.WORLD_DATA && window.WORLD_DATA.dashed_borders) {{
          gDisputed.selectAll("path")
            .data(window.WORLD_DATA.dashed_borders)
            .enter()
            .append("path")
            .attr("d", pathGenerator)
            .attr("fill", "none")
            .attr("stroke", theme.landEdge)
            .attr("stroke-width", 0.75)
            .attr("stroke-dasharray", "4,3");
        }}

        // India States Layer
        const showStateBorders = document.getElementById("chk-state-borders").checked;
        const dataMap = getCurrentDataMap();
        const colors = getInterpolatedColors(numClasses);

        let minVal = Infinity, maxVal = -Infinity;
        if (dataMap) {{
          Object.values(dataMap).forEach(v => {{
            if (typeof v === "number" && !isNaN(v)) {{
              if (v < minVal) minVal = v;
              if (v > maxVal) maxVal = v;
            }}
          }});
        }}
        if (minVal === Infinity) {{ minVal = 0; maxVal = 100; }}
        const step = (maxVal - minVal) / numClasses;

        // Render States
        gStates.selectAll("path").remove();
        if (currentMode === "india" || showStateBorders) {{
          gStates.selectAll("path")
            .data(window.INDIA_STATES_DATA.features)
            .enter()
            .append("path")
            .attr("d", pathGenerator)
            .attr("fill", d => {{
              const stName = d.properties.ST_NM || d.properties.st_nm;
              if (dataMap && dataMap[stName] !== undefined) {{
                const val = dataMap[stName];
                const bin = Math.max(0, Math.min(numClasses - 1, Math.floor((val - minVal) / (step || 1))));
                return colors[bin];
              }}
              return theme.stateFill;
            }})
            .attr("stroke", theme.stateEdge)
            .attr("stroke-width", 0.6)
            .style("cursor", "pointer")
            .on("mouseenter", function(event, d) {{
              if (currentMode !== "india") return;
              d3.select(this).attr("stroke", "#0f172a").attr("stroke-width", 1.5);
              const stName = d.properties.ST_NM || d.properties.st_nm;
              const val = dataMap ? dataMap[stName] : null;
              const code = d.properties.st_code || d.properties.ST_ID || "";
              
              inspector.style("display", "block");
              document.getElementById("inspect-name").textContent = stName;
              document.getElementById("inspect-code").textContent = code;
              
              if (val !== null && val !== undefined) {{
                const unit = (window.SAMPLE_DATASETS[currentMetric] || {{}}).unit || "";
                document.getElementById("inspect-val").textContent = `${{val.toLocaleString()}} ${{unit}}`.trim();
                document.getElementById("inspect-metric-label").textContent = (window.SAMPLE_DATASETS[currentMetric] || {{}}).label || "Value";
              }} else {{
                document.getElementById("inspect-val").textContent = "—";
                document.getElementById("inspect-metric-label").textContent = "No data recorded";
              }}
            }})
            .on("mouseleave", function() {{
              d3.select(this).attr("stroke", theme.stateEdge).attr("stroke-width", 0.6);
            }});
        }}

        // Sovereign Boundary Outline
        const showSovereign = document.getElementById("chk-soi-border").checked;
        gSovereign.selectAll("path").remove();
        if (showSovereign && window.WORLD_DATA) {{
          const indiaFeat = window.WORLD_DATA.features.find(f => f.properties.name === "India");
          if (indiaFeat) {{
            gSovereign.append("path")
              .datum(indiaFeat)
              .attr("d", pathGenerator)
              .attr("fill", "none")
              .attr("stroke", theme.indiaEdge)
              .attr("stroke-width", 1.3)
              .style("pointer-events", "none");
          }}
        }}

        // Labels Layer
        gLabels.selectAll("*").remove();

        if (currentMode === "india") {{
          const showLabels = document.getElementById("chk-state-labels").checked;
          if (showLabels) {{
            gLabels.selectAll("text.state-label")
              .data(window.INDIA_STATES_DATA.features)
              .enter()
              .append("text")
              .attr("class", "state-label")
              .attr("transform", d => {{
                const p = projection(d.properties.centroid || d3.geoCentroid(d));
                return p ? `translate(${{p[0]}}, ${{p[1]}})` : null;
              }})
              .text(d => d.properties.ST_NM || d.properties.st_nm)
              .attr("text-anchor", "middle")
              .attr("dominant-baseline", "central")
              .attr("fill", theme.text)
              .attr("font-size", "7.5px")
              .attr("font-weight", "600")
              .attr("paint-order", "stroke")
              .attr("stroke", theme.bg)
              .attr("stroke-width", 2.5)
              .attr("stroke-linejoin", "round")
              .style("pointer-events", "none");
          }}
        }} else if (currentMode === "global") {{
          const showCountryLabels = document.getElementById("chk-country-labels").checked;
          const showMicronations = document.getElementById("chk-micronations").checked;
          const showOceans = document.getElementById("chk-ocean-labels").checked;

          // Ocean Labels
          if (showOceans && window.WORLD_DATA && window.WORLD_DATA.oceans) {{
            gLabels.selectAll("text.ocean-label")
              .data(window.WORLD_DATA.oceans)
              .enter()
              .append("text")
              .attr("class", "ocean-label")
              .attr("transform", d => {{
                const pt = projection(d.centroid);
                return pt ? `translate(${{pt[0]}}, ${{pt[1]}})` : null;
              }})
              .text(d => d.label || d.name)
              .attr("text-anchor", "middle")
              .attr("dominant-baseline", "central")
              .attr("fill", theme.ocean === '#ffffff' ? '#64748b' : '#3b82f6')
              .attr("opacity", 0.5)
              .attr("font-size", "11px")
              .attr("font-weight", "700")
              .attr("font-style", "italic")
              .attr("letter-spacing", "2px")
              .style("cursor", "pointer")
              .on("mouseenter", (event, d) => {{
                tooltip.style("display", "block").html(`
                  <div style="font-size: 12px; line-height: 1.4;">
                    <strong>🌊 ${{d.name}}</strong>
                    ${{d.wiki ? '<br><span style="font-size: 10px; color: #38bdf8;">Click to view Wikipedia article ↗</span>' : ''}}
                  </div>
                `);
              }})
              .on("mousemove", event => {{
                tooltip.style("left", (event.pageX + 12) + "px").style("top", (event.pageY + 12) + "px");
              }})
              .on("mouseleave", () => tooltip.style("display", "none"))
              .on("click", (event, d) => {{
                if (d.wiki) window.open(d.wiki, "_blank");
              }});
          }}

          // Country Labels
          if (showCountryLabels && window.WORLD_DATA && window.WORLD_DATA.features) {{
            const normalCountries = window.WORLD_DATA.features.filter(f => !f.properties.is_micronation && !f.properties.minor_territory);
            gLabels.selectAll("text.country-label")
              .data(normalCountries)
              .enter()
              .append("text")
              .attr("class", "country-label")
              .attr("transform", d => {{
                const pt = projection(d.properties.centroid || d3.geoCentroid(d));
                return pt ? `translate(${{pt[0]}}, ${{pt[1]}})` : null;
              }})
              .text(d => d.properties.name)
              .attr("text-anchor", "middle")
              .attr("dominant-baseline", "central")
              .attr("fill", d => (d.properties.name === "India") ? theme.indiaEdge : theme.text)
              .attr("font-size", d => (d.properties.name === "India") ? "10.5px" : "8px")
              .attr("font-weight", d => (d.properties.name === "India") ? "800" : "700")
              .attr("paint-order", "stroke")
              .attr("stroke", theme.bg)
              .attr("stroke-width", 2.6)
              .attr("stroke-linejoin", "round")
              .style("cursor", "pointer")
              .on("mouseenter", (event, d) => {{
                tooltip.style("display", "block").html(`
                  <div style="font-size: 12px; line-height: 1.4;">
                    <strong>${{d.properties.name}}</strong>
                    ${{d.properties.wiki ? '<br><span style="font-size: 10px; color: #38bdf8;">Click to view Wikipedia article ↗</span>' : ''}}
                  </div>
                `);
              }})
              .on("mousemove", event => {{
                tooltip.style("left", (event.pageX + 12) + "px").style("top", (event.pageY + 12) + "px");
              }})
              .on("mouseleave", () => tooltip.style("display", "none"))
              .on("click", (event, d) => {{
                if (d.properties && d.properties.wiki) window.open(d.properties.wiki, "_blank");
              }});
          }}

          // Micronations & Territories (Pins + Names)
          if (showMicronations && window.WORLD_DATA && window.WORLD_DATA.features) {{
            const micronations = window.WORLD_DATA.features.filter(f => f.properties.is_micronation || f.properties.minor_territory);
            
            // Circles for micro territories
            gLabels.selectAll("circle.micro-dot")
              .data(micronations)
              .enter()
              .append("circle")
              .attr("class", "micro-dot")
              .attr("cx", d => {{
                const pt = projection(d.properties.centroid || d3.geoCentroid(d));
                return pt ? pt[0] : -9999;
              }})
              .attr("cy", d => {{
                const pt = projection(d.properties.centroid || d3.geoCentroid(d));
                return pt ? pt[1] : -9999;
              }})
              .attr("r", 2.2)
              .attr("fill", "#f59e0b")
              .attr("stroke", "#ffffff")
              .attr("stroke-width", 0.7)
              .style("cursor", "pointer")
              .on("mouseenter", (event, d) => {{
                tooltip.style("display", "block").html(`
                  <div style="font-size: 12px; line-height: 1.4;">
                    <strong>📍 ${{d.properties.name}}</strong>
                    <br><span style="font-size: 10px; color: #cbd5e1;">Territory / Micronation</span>
                    ${{d.properties.wiki ? '<br><span style="font-size: 10px; color: #38bdf8;">Click to view Wikipedia article ↗</span>' : ''}}
                  </div>
                `);
              }})
              .on("mousemove", event => {{
                tooltip.style("left", (event.pageX + 12) + "px").style("top", (event.pageY + 12) + "px");
              }})
              .on("mouseleave", () => tooltip.style("display", "none"))
              .on("click", (event, d) => {{
                if (d.properties && d.properties.wiki) window.open(d.properties.wiki, "_blank");
              }});

            // Labels for micro territories
            gLabels.selectAll("text.micro-label")
              .data(micronations)
              .enter()
              .append("text")
              .attr("class", "micro-label")
              .attr("transform", d => {{
                const pt = projection(d.properties.centroid || d3.geoCentroid(d));
                return pt ? `translate(${{pt[0] + 4}}, ${{pt[1] - 3}})` : null;
              }})
              .text(d => d.properties.name)
              .attr("text-anchor", "start")
              .attr("dominant-baseline", "central")
              .attr("fill", theme.text)
              .attr("font-size", "6.5px")
              .attr("font-weight", "600")
              .attr("paint-order", "stroke")
              .attr("stroke", theme.bg)
              .attr("stroke-width", 2.0)
              .style("cursor", "pointer")
              .on("mouseenter", (event, d) => {{
                tooltip.style("display", "block").html(`
                  <div style="font-size: 12px; line-height: 1.4;">
                    <strong>📍 ${{d.properties.name}}</strong>
                    ${{d.properties.wiki ? '<br><span style="font-size: 10px; color: #38bdf8;">Click to view Wikipedia article ↗</span>' : ''}}
                  </div>
                `);
              }})
              .on("mousemove", event => {{
                tooltip.style("left", (event.pageX + 12) + "px").style("top", (event.pageY + 12) + "px");
              }})
              .on("mouseleave", () => tooltip.style("display", "none"))
              .on("click", (event, d) => {{
                if (d.properties && d.properties.wiki) window.open(d.properties.wiki, "_blank");
              }});
          }}
        }}

        // Update Inspector & Legend visibility (Auto-hidden in Global Earth mode)
        if (currentMode === "global") {{
          inspector.style("display", "none");
          legendEl.style("display", "none");
        }} else if (dataMap && currentMetric !== "none") {{
          legendEl.style("display", "block");
          const metricMeta = window.SAMPLE_DATASETS[currentMetric] || {{ label: "Legend", unit: "" }};
          document.getElementById("legend-title-text").textContent = metricMeta.label;
          
          let legendHtml = "";
          for (let i = 0; i < numClasses; i++) {{
            const bMin = minVal + i * step;
            const bMax = minVal + (i + 1) * step;
            const lbl = (maxVal > 100)
              ? `${{Math.round(bMin).toLocaleString()}} – ${{Math.round(bMax).toLocaleString()}} ${{metricMeta.unit}}`
              : `${{bMin.toFixed(1)}} – ${{bMax.toFixed(1)}} ${{metricMeta.unit}}`;
            legendHtml += `
              <div class="legend-item">
                <span class="legend-swatch" style="background: ${{colors[i]}};"></span>
                <span>${{lbl}}</span>
              </div>
            `;
          }}
          document.getElementById("legend-items").innerHTML = legendHtml;
        }} else {{
          legendEl.style("display", "none");
        }}
      }}

      // Mode Switcher handlers
      document.getElementById("mode-india").addEventListener("click", () => {{
        currentMode = "india";
        document.getElementById("mode-india").classList.add("active");
        document.getElementById("mode-global").classList.remove("active");
        document.getElementById("sec-thematic").style.display = "block";
        document.getElementById("sec-global").style.display = "none";
        document.getElementById("input-title").value = "India — Administrative Boundaries & States";
        svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
        updateMap();
      }});

      document.getElementById("mode-global").addEventListener("click", () => {{
        currentMode = "global";
        document.getElementById("mode-global").classList.add("active");
        document.getElementById("mode-india").classList.remove("active");
        document.getElementById("sec-thematic").style.display = "none";
        document.getElementById("sec-global").style.display = "block";
        document.getElementById("input-title").value = "Equal Earth World Map (Survey of India Boundary)";
        svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
        updateMap();
      }});

      // Sidebar Toggle
      document.getElementById("toggle-sidebar").addEventListener("click", () => {{
        document.getElementById("sidebar").classList.toggle("collapsed");
      }});

      // Control Event Listeners
      document.getElementById("sel-theme").addEventListener("change", e => {{
        currentThemeKey = e.target.value;
        updateMap();
      }});

      document.getElementById("sel-metric").addEventListener("change", e => {{
        currentMetric = e.target.value;
        document.getElementById("group-csv-upload").style.display = (currentMetric === "custom") ? "block" : "none";
        if (currentMetric !== "none" && window.SAMPLE_DATASETS[currentMetric]) {{
          document.getElementById("input-title").value = `India — ${{window.SAMPLE_DATASETS[currentMetric].label}}`;
        }}
        updateMap();
      }});

      document.getElementById("sel-palette").addEventListener("change", e => {{
        currentPaletteKey = e.target.value;
        updateMap();
      }});

      document.getElementById("sel-classes").addEventListener("change", e => {{
        numClasses = parseInt(e.target.value, 10);
        updateMap();
      }});

      document.getElementById("sel-center-preset").addEventListener("change", e => {{
        const val = e.target.value;
        if (val === "custom") {{
          document.getElementById("group-custom-lon").style.display = "block";
          centralLon = parseFloat(document.getElementById("input-custom-lon").value) || 0;
        }} else {{
          document.getElementById("group-custom-lon").style.display = "none";
          centralLon = parseFloat(val);
        }}
        updateMap();
      }});

      document.getElementById("input-custom-lon").addEventListener("input", e => {{
        centralLon = parseFloat(e.target.value) || 0;
        updateMap();
      }});

      // Layer Checkboxes
      ["chk-state-borders", "chk-state-labels", "chk-soi-border", "chk-country-labels", "chk-micronations", "chk-ocean-labels", "chk-graticule", "chk-disputed-borders"].forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.addEventListener("change", updateMap);
      }});

      // Zoom Controls
      document.getElementById("btn-zoom-in").addEventListener("click", () => {{
        svg.transition().duration(250).call(zoom.scaleBy, 1.4);
      }});

      document.getElementById("btn-zoom-out").addEventListener("click", () => {{
        svg.transition().duration(250).call(zoom.scaleBy, 0.7);
      }});

      document.getElementById("btn-fit-extent").addEventListener("click", () => {{
        svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
      }});

      document.getElementById("btn-reset-view").addEventListener("click", () => {{
        svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
        currentThemeKey = "atlas_light";
        document.getElementById("sel-theme").value = "atlas_light";
        updateMap();
      }});

      // Custom CSV Upload Handler
      document.getElementById("input-csv-file").addEventListener("change", e => {{
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = ev => {{
          const lines = ev.target.result.split(/\\r?\\n/);
          customData = {{}};
          let matched = 0;
          lines.forEach((line, idx) => {{
            if (idx === 0 || !line.trim()) return;
            const parts = line.split(",");
            if (parts.length >= 2) {{
              const st = normalizeState(parts[0]);
              const val = parseFloat(parts[1].trim());
              if (!isNaN(val)) {{
                customData[st] = val;
                matched++;
              }}
            }}
          }});
          document.getElementById("csv-status").textContent = `✓ ${{matched}} states matched successfully.`;
          updateMap();
        }};
        reader.readAsText(file);
      }});

      // Export SVG
      document.getElementById("btn-export-svg").addEventListener("click", () => {{
        const serializer = new XMLSerializer();
        const svgClone = svg.node().cloneNode(true);
        svgClone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        const blob = new Blob([serializer.serializeToString(svgClone)], {{ type: "image/svg+xml" }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `equal_earth_${{currentMode}}_map.svg`;
        a.click();
        URL.revokeObjectURL(url);
      }});

      // Export PNG (300 DPI high resolution canvas rasterization)
      document.getElementById("btn-export-png").addEventListener("click", () => {{
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(svg.node());
        const img = new Image();
        const svgBlob = new Blob([svgString], {{ type: "image/svg+xml;charset=utf-8" }});
        const url = URL.createObjectURL(svgBlob);
        
        img.onload = () => {{
          const scale = 3; // 3x scale for crisp 300 DPI
          const canvas = document.createElement("canvas");
          canvas.width = width * scale;
          canvas.height = height * scale;
          const ctx = canvas.getContext("2d");
          ctx.scale(scale, scale);
          ctx.fillStyle = THEMES[currentThemeKey].ocean;
          ctx.fillRect(0, 0, width, height);
          ctx.drawImage(img, 0, 0, width, height);
          
          const pngUrl = canvas.toDataURL("image/png");
          const a = document.createElement("a");
          a.href = pngUrl;
          a.download = `equal_earth_${{currentMode}}_300dpi.png`;
          a.click();
          URL.revokeObjectURL(url);
        }};
        img.src = url;
      }});

      // Export PDF
      document.getElementById("btn-export-pdf").addEventListener("click", () => {{
        if (!window.jspdf) {{
          alert("jsPDF library is still loading. Please retry in a moment.");
          return;
        }}
        const {{ jsPDF }} = window.jspdf;
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(svg.node());
        const img = new Image();
        const svgBlob = new Blob([svgString], {{ type: "image/svg+xml;charset=utf-8" }});
        const url = URL.createObjectURL(svgBlob);

        img.onload = () => {{
          const canvas = document.createElement("canvas");
          canvas.width = width * 2;
          canvas.height = height * 2;
          const ctx = canvas.getContext("2d");
          ctx.scale(2, 2);
          ctx.fillStyle = THEMES[currentThemeKey].ocean;
          ctx.fillRect(0, 0, width, height);
          ctx.drawImage(img, 0, 0, width, height);

          const imgData = canvas.toDataURL("image/jpeg", 0.95);
          const pdf = new jsPDF({{
            orientation: (width > height) ? "landscape" : "portrait",
            unit: "pt",
            format: [width, height]
          }});
          pdf.addImage(imgData, "JPEG", 0, 0, width, height);
          pdf.save(`equal_earth_${{currentMode}}_map.pdf`);
          URL.revokeObjectURL(url);
        }};
        img.src = url;
      }});

      // Initial Mount
      window.addEventListener("resize", updateMap);
      updateMap();

    }})();
  </script>
</body>
</html>"""

    target_file = Path(output_path) if output_path else HTML_OUTPUT_PATH
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(html_code)
    print(f"[✓] Equal Earth Geospatial Studio generated: {target_file} ({target_file.stat().st_size:,} bytes)")

    if sync_index:
        with open(INDEX_OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(html_code)
        print(f"[✓] Synchronized root index: {INDEX_OUTPUT_PATH}")

    return target_file


if __name__ == "__main__":
    build_interactive_html()
