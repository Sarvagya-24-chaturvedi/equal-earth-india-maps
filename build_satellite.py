"""
Builder script to generate the standalone satellite_day_night.html portal.
Embeds world_data.json for 100% offline & local file:// compatibility,
linking with local leaflet.js and leaflet.css.
Includes:
- NASA Blue Marble (Topography & Bathymetry)
- NASA MODIS Terra TrueColor (Daily Real-Time Satellite Pass)
- NASA Black Marble (VIIRS Earth at Night)
- Real-time Solar Terminator (Astronomical GMST & Subsolar Declination)
- Survey of India 100% sovereign boundary (J&K, Ladakh, Aksai Chin, Siachen, Arunachal Pradesh)
- Disputed borders in light dashed lines (Serbia-Kosovo, Morocco-SADR, Bir Tawil)
- Latitude/Longitude graticule grid
- 24h interactive solar scrubber & simulation playback
- Live UTC and IST clocks
"""

import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "world_data.json"
HTML_OUTPUT = BASE_DIR / "satellite_day_night.html"

def generate_satellite_html():
    print("[*] Reading world_data.json...")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        geojson_str = f.read()

    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Topographic Satellite & Real-Time Day/Night Map · Survey of India Boundary</title>

  <!-- Local Leaflet CSS & JS with CDN Fallback -->
  <link rel="stylesheet" href="leaflet.css" />
  <script src="leaflet.js"></script>
  <script>
    if (typeof L === 'undefined') {{
      document.write('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />');
      document.write('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"><\\/script>');
    }}
  </script>

  <style>
    :root {{
      --bg-dark: #0a0f1d;
      --card-bg: rgba(15, 23, 42, 0.90);
      --card-border: rgba(148, 163, 184, 0.25);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --accent-gold: #f59e0b;
      --accent-gold-hover: #d97706;
      --accent-green: #10b981;
      --accent-cyan: #38bdf8;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg-dark);
      color: var(--text-main);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
    }}

    #map {{
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      width: 100%;
      height: 100%;
      background: #030712;
      z-index: 1;
    }}

    /* Top Floating Controls Bar */
    .top-bar {{
      position: absolute;
      top: 14px;
      left: 14px;
      right: 14px;
      z-index: 1000;
      display: flex;
      gap: 10px;
      pointer-events: none;
      align-items: flex-start;
      justify-content: space-between;
    }}

    .card {{
      background: var(--card-bg);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
      pointer-events: auto;
    }}

    .header-card {{
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }}

    .title-area h1 {{
      font-size: 15px;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
      letter-spacing: -0.2px;
    }}

    .title-area p {{
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 7px;
      border-radius: 20px;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.3px;
    }}

    .badge-soi {{
      background: rgba(245, 158, 11, 0.18);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.45);
    }}

    .badge-live {{
      background: rgba(16, 185, 129, 0.18);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.45);
    }}

    .badge-pulse {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
      animation: pulse 1.6s infinite;
    }}

    @keyframes pulse {{
      0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
      70% {{ transform: scale(1.1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }}
      100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    /* Navigation button to switch to Equal Earth Political map */
    .nav-switch-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 13px;
      background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
      border: 1px solid #60a5fa;
      border-radius: 8px;
      color: #ffffff;
      font-size: 12px;
      font-weight: 700;
      text-decoration: none;
      transition: all 0.2s ease;
      white-space: nowrap;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35);
    }}

    .nav-switch-btn:hover {{
      background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.55);
      transform: translateY(-1px);
    }}

    /* Control Panel Drawer */
    .controls-panel {{
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-width: 500px;
    }}

    .ctrl-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .ctrl-label {{
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      min-width: 52px;
    }}

    /* Base Layer Selector Pills */
    .pill-group {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }}

    .pill-btn {{
      padding: 5px 10px;
      background: rgba(30, 41, 59, 0.85);
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 6px;
      color: #cbd5e1;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .pill-btn:hover {{
      background: rgba(51, 65, 85, 0.95);
      color: #fff;
      border-color: rgba(148, 163, 184, 0.5);
    }}

    .pill-btn.active {{
      background: #2563eb;
      color: #ffffff;
      border-color: #3b82f6;
      box-shadow: 0 0 10px rgba(37, 99, 235, 0.4);
    }}

    /* Checkbox Toggles */
    .toggle-chip {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 8px;
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 6px;
      font-size: 11px;
      color: #cbd5e1;
      cursor: pointer;
      user-select: none;
      transition: all 0.15s ease;
    }}

    .toggle-chip input {{
      cursor: pointer;
      accent-color: #2563eb;
    }}

    .toggle-chip:hover {{
      background: rgba(51, 65, 85, 0.8);
      color: #fff;
    }}

    /* Time Scrubber & Digital Clock */
    .clock-display-card {{
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 8px;
      padding: 8px 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .clock-times {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .clock-val {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      font-weight: 700;
      color: var(--accent-cyan);
    }}

    .clock-ist {{
      color: #fbbf24;
    }}

    .subsolar-info {{
      font-size: 10.5px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .scrubber-controls {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .scrubber-slider {{
      flex: 1;
      accent-color: var(--accent-cyan);
      cursor: pointer;
    }}

    .btn-sm {{
      padding: 4px 8px;
      background: #334155;
      border: 1px solid #475569;
      border-radius: 6px;
      color: #fff;
      font-size: 10.5px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s ease;
      white-space: nowrap;
    }}

    .btn-sm:hover {{
      background: #475569;
    }}

    .btn-sm.live-btn {{
      background: rgba(16, 185, 129, 0.25);
      border-color: rgba(16, 185, 129, 0.6);
      color: #34d399;
    }}

    .btn-sm.live-btn:hover {{
      background: rgba(16, 185, 129, 0.4);
      color: #fff;
    }}

    /* Search Input */
    .search-input {{
      padding: 5px 9px;
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid rgba(148, 163, 184, 0.3);
      border-radius: 6px;
      color: #fff;
      font-size: 11.5px;
      outline: none;
      width: 140px;
    }}

    .search-input:focus {{
      border-color: #3b82f6;
      box-shadow: 0 0 8px rgba(59, 130, 246, 0.4);
    }}

    /* Mobile Controls Toggle */
    .mobile-controls-toggle {{
      display: none;
      padding: 6px 10px;
      background: rgba(30, 41, 59, 0.95);
      border: 1px solid rgba(148, 163, 184, 0.3);
      border-radius: 8px;
      color: #fff;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      pointer-events: auto;
    }}

    /* Bottom Quick-Action Dock */
    .bottom-dock {{
      position: absolute;
      bottom: 14px;
      left: 14px;
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 6px;
      pointer-events: none;
      flex-wrap: wrap;
    }}

    .dock-pill {{
      pointer-events: auto;
      padding: 5px 10px;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(148, 163, 184, 0.3);
      border-radius: 20px;
      color: #e2e8f0;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .dock-pill:hover {{
      background: #2563eb;
      color: #fff;
      border-color: #3b82f6;
      transform: translateY(-1px);
    }}

    .dock-pill.active {{
      background: #f59e0b;
      color: #000;
      font-weight: 700;
      border-color: #f59e0b;
    }}

    /* Leaflet Overrides */
    .leaflet-bar {{
      border: 1px solid rgba(148, 163, 184, 0.3) !important;
      border-radius: 8px !important;
      overflow: hidden;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
    }}

    .leaflet-bar a {{
      background: rgba(15, 23, 42, 0.9) !important;
      color: #e2e8f0 !important;
      border-bottom: 1px solid rgba(148, 163, 184, 0.2) !important;
    }}

    .leaflet-bar a:hover {{
      background: #2563eb !important;
      color: #fff !important;
    }}

    .leaflet-control-attribution {{
      background: rgba(15, 23, 42, 0.85) !important;
      color: #94a3b8 !important;
      font-size: 9.5px !important;
      backdrop-filter: blur(4px);
      padding: 2px 7px !important;
      border-top-left-radius: 6px;
    }}

    .leaflet-control-attribution a {{
      color: #60a5fa !important;
    }}

    /* Leaflet Popup Styling */
    .leaflet-popup-content-wrapper {{
      background: rgba(15, 23, 42, 0.95) !important;
      backdrop-filter: blur(10px);
      color: #f8fafc !important;
      border: 1px solid rgba(148, 163, 184, 0.3) !important;
      border-radius: 10px !important;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important;
    }}

    .leaflet-popup-tip {{
      background: rgba(15, 23, 42, 0.95) !important;
    }}

    /* Subsolar Marker Icon */
    .subsolar-marker {{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: radial-gradient(circle, #fde047 30%, #f59e0b 70%, rgba(245, 158, 11, 0) 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      filter: drop-shadow(0 0 12px rgba(250, 204, 21, 0.95));
      animation: sun-pulse 2s infinite ease-in-out;
    }}

    @keyframes sun-pulse {{
      0% {{ transform: scale(0.92); opacity: 0.9; }}
      50% {{ transform: scale(1.12); opacity: 1; }}
      100% {{ transform: scale(0.92); opacity: 0.9; }}
    }}

    /* Country Label Marker */
    .country-label-marker {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 10px;
      font-weight: 700;
      color: #ffffff;
      text-shadow: 0 0 3px #000, 0 0 5px #000, 1px 1px 2px #000;
      white-space: nowrap;
      pointer-events: none;
      transform: translate(-50%, -50%);
    }}

    /* Graticule Lat/Lon Labels */
    .graticule-label {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 9px;
      font-weight: 600;
      color: #94a3b8;
      background: rgba(15, 23, 42, 0.7);
      padding: 1px 4px;
      border-radius: 3px;
      pointer-events: none;
    }}

    /* Responsive Mobile Layout */
    @media (max-width: 768px) {{
      .top-bar {{
        top: 8px;
        left: 8px;
        right: 8px;
        flex-direction: column;
        gap: 6px;
      }}

      .header-card {{
        width: 100%;
        justify-content: space-between;
        padding: 8px 12px;
      }}

      .title-area h1 {{
        font-size: 13px;
      }}

      .title-area p {{
        display: none;
      }}

      .nav-switch-btn {{
        font-size: 10.5px;
        padding: 5px 9px;
      }}

      .mobile-controls-toggle {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }}

      .controls-panel {{
        display: none;
        width: 100%;
        max-width: none;
        max-height: 75vh;
        overflow-y: auto;
        padding: 12px;
      }}

      .controls-panel.open {{
        display: flex;
      }}

      .bottom-dock {{
        bottom: 8px;
        left: 8px;
        right: 8px;
        overflow-x: auto;
        white-space: nowrap;
        padding-bottom: 4px;
      }}

      .search-input {{
        width: 110px;
      }}
    }}
  </style>
</head>
<body>

  <!-- Map Canvas -->
  <div id="map"></div>

  <!-- Top Floating Header & Controls -->
  <div class="top-bar">
    <div class="card header-card">
      <div class="title-area">
        <h1>
          <span>🛰️ Topographic & Live Day/Night Map</span>
          <span class="badge badge-soi">SOI Sovereign Boundary</span>
          <span class="badge badge-live"><span class="badge-pulse"></span> NASA Live Feeds</span>
        </h1>
        <p>Real-Time Solar Terminator · NASA Blue Marble & Black Marble · Survey of India Compliant</p>
      </div>

      <div style="display: flex; align-items: center; gap: 8px;">
        <a href="index.html" class="nav-switch-btn" title="Switch to Political Equal Earth Projection">
          🗺️ Equal Earth Map ↗
        </a>
        <button id="mobile-toggle-btn" class="mobile-controls-toggle" aria-label="Toggle Controls Menu">
          <span>⚙️ Layers</span>
          <span id="chevron">▾</span>
        </button>
      </div>
    </div>

    <!-- Collapsible Controls Panel -->
    <div class="card controls-panel" id="controls-panel">
      <!-- Base Layers -->
      <div class="ctrl-row">
        <span class="ctrl-label">Basemap:</span>
        <div class="pill-group">
          <button class="pill-btn active" data-layer="daynight">🌓 Live Day/Night</button>
          <button class="pill-btn" data-layer="bluemarble">🌍 Blue Marble</button>
          <button class="pill-btn" data-layer="modis">🛰️ MODIS Pass</button>
          <button class="pill-btn" data-layer="blackmarble">🌃 Black Marble</button>
          <button class="pill-btn" data-layer="opentopo">🏔️ Topo Terrain</button>
          <button class="pill-btn" data-layer="esri">🛰️ 50cm Satellite</button>
        </div>
      </div>

      <!-- Vector Overlays -->
      <div class="ctrl-row">
        <span class="ctrl-label">Overlays:</span>
        <label class="toggle-chip">
          <input type="checkbox" id="chk-soi" checked>
          <span>🇮🇳 SOI Official Border</span>
        </label>
        <label class="toggle-chip">
          <input type="checkbox" id="chk-disputed" checked>
          <span>⚠️ Disputed Borders</span>
        </label>
        <label class="toggle-chip">
          <input type="checkbox" id="chk-borders" checked>
          <span>🌐 World Borders</span>
        </label>
        <label class="toggle-chip">
          <input type="checkbox" id="chk-labels" checked>
          <span>🏷️ Country Labels</span>
        </label>
        <label class="toggle-chip">
          <input type="checkbox" id="chk-graticule" checked>
          <span>📐 Lat/Lon Grid</span>
        </label>
        <label class="toggle-chip">
          <input type="checkbox" id="chk-sun" checked>
          <span>☀️ Sun Overhead</span>
        </label>
      </div>

      <!-- Live Clock & Solar Scrubber -->
      <div class="clock-display-card">
        <div class="clock-times">
          <div>
            <span style="font-size: 10px; color: var(--text-muted);">UTC:</span>
            <span class="clock-val" id="time-utc">--:--:-- UTC</span>
          </div>
          <div>
            <span style="font-size: 10px; color: var(--text-muted);">IST (India):</span>
            <span class="clock-val clock-ist" id="time-ist">--:--:-- IST</span>
          </div>
          <button class="btn-sm live-btn" id="btn-live">⚡ Jump to Live</button>
        </div>

        <div class="subsolar-info">
          <span>☀️ <strong>Subsolar Zenith:</strong></span>
          <span id="subsolar-coords">Lat: 0.0°, Lon: 0.0°</span>
        </div>

        <div class="scrubber-controls">
          <button class="btn-sm" id="btn-play">▶ Play 24h</button>
          <input type="range" id="time-scrubber" class="scrubber-slider" min="-720" max="720" step="10" value="0" title="Scrub time -12h to +12h">
          <span id="scrub-offset-label" style="font-size: 10.5px; min-width: 48px; text-align: right; font-family: monospace;">Live</span>
        </div>
      </div>

      <!-- Country Search & Fly To -->
      <div class="ctrl-row">
        <span class="ctrl-label">Search:</span>
        <input type="text" id="country-search" class="search-input" list="country-list" placeholder="Search country...">
        <datalist id="country-list"></datalist>
        <button class="btn-sm" id="btn-fly-india">🇮🇳 Fly India</button>
        <button class="btn-sm" id="btn-fly-global">🌐 Global (0°)</button>
      </div>
    </div>
  </div>

  <!-- Bottom Quick Fly Dock -->
  <div class="bottom-dock">
    <button class="dock-pill active" id="dock-india">🇮🇳 India (Official SOI)</button>
    <button class="dock-pill" id="dock-sun">☀️ Subsolar Zenith</button>
    <button class="dock-pill" id="dock-himalayas">🏔️ Himalayas & Siachen</button>
    <button class="dock-pill" id="dock-global">🌐 Prime Meridian (0°)</button>
    <button class="dock-pill" id="dock-americas">🌎 Americas</button>
    <button class="dock-pill" id="dock-asia">🌏 Asia-Pacific</button>
    <button class="dock-pill" id="dock-europe">🌍 Europe / Africa</button>
  </div>

  <!-- Embedded Survey of India & World Data -->
  <script>
    const WORLD_DATA = {geojson_str};
  </script>

  <!-- Core Map Controller Script -->
  <script>
    (function() {{
      const MODIS_DATE = "{today_utc}";

      // 1. Initialize Leaflet Map
      // Centered on India with SOI boundary view
      const map = L.map('map', {{
        center: [22.0, 78.5],
        zoom: 4,
        minZoom: 2,
        maxZoom: 18,
        worldCopyJump: true,
        zoomControl: false
      }});

      L.control.zoom({{ position: 'topright' }}).addTo(map);

      // Create Custom Panes for Layer Stacking & Blending
      // 1) nightShadowPane (z-index 405) for terminator shading
      map.createPane('nightShadowPane');
      map.getPane('nightShadowPane').style.zIndex = 405;
      map.getPane('nightShadowPane').style.pointerEvents = 'none';

      // 2) nightLightsPane (z-index 410) with screen blend mode for glowing city lights
      map.createPane('nightLightsPane');
      map.getPane('nightLightsPane').style.zIndex = 410;
      map.getPane('nightLightsPane').style.pointerEvents = 'none';
      map.getPane('nightLightsPane').style.mixBlendMode = 'screen';

      // 2. Base Tile Layers (NASA GIBS WMTS, ESRI, OpenTopoMap)
      const baseLayers = {{
        bluemarble: L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/default/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.jpeg', {{
          subdomains: 'abc',
          maxZoom: 8,
          attribution: 'Imagery © NASA Earthdata GIBS (Blue Marble)'
        }}),
        modis: L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/' + MODIS_DATE + '/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg', {{
          subdomains: 'abc',
          maxZoom: 9,
          attribution: 'Daily Satellite Pass © NASA Terra / MODIS (' + MODIS_DATE + ')'
        }}),
        blackmarble: L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/default/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.png', {{
          subdomains: 'abc',
          maxZoom: 8,
          attribution: 'Night Lights © NASA Suomi NPP / VIIRS Black Marble'
        }}),
        opentopo: L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
          maxZoom: 17,
          attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'
        }}),
        esri: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
          maxZoom: 19,
          attribution: 'High-Res Satellite © Esri, Maxar, Earthstar Geographics'
        }})
      }};

      // Active Base Layer State (Default: Live Day/Night)
      let currentBaseKey = 'daynight';
      let activeBaseLayer = baseLayers.bluemarble;
      activeBaseLayer.addTo(map);

      // Night Lights Screen Overlay for Day/Night Composite
      const nightLightsOverlay = L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/default/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.png', {{
        subdomains: 'abc',
        maxZoom: 8,
        pane: 'nightLightsPane',
        opacity: 0.85,
        attribution: 'Night Lights: NASA VIIRS'
      }});
      nightLightsOverlay.addTo(map);

      // 3. Astronomical Solar Terminator Calculations
      const rad = Math.PI / 180;

      function getSolarCoordinates(date) {{
        const jd = (date.getTime() / 86400000) + 2440587.5;
        const d = jd - 2451545.0;

        let g = (357.529 + 0.98560028 * d) % 360;
        if (g < 0) g += 360;

        let q = (280.459 + 0.98564736 * d) % 360;
        if (q < 0) q += 360;

        let L = (q + 1.915 * Math.sin(g * rad) + 0.020 * Math.sin(2 * g * rad)) % 360;
        if (L < 0) L += 360;

        let e = 23.439 - 0.00000036 * d;

        let sinDec = Math.sin(e * rad) * Math.sin(L * rad);
        let dec = Math.asin(sinDec) / rad;
        let ra = Math.atan2(Math.cos(e * rad) * Math.sin(L * rad), Math.cos(L * rad)) / rad;

        let gmst = (280.46061837 + 360.98564736629 * d) % 360;
        if (gmst < 0) gmst += 360;

        let lon0 = ((ra - gmst) % 360);
        if (lon0 < -180) lon0 += 360;
        if (lon0 > 180) lon0 -= 360;

        return {{ lat: dec, lon: lon0 }};
      }}

      function computeTerminatorPolygon(solar) {{
        const dec = solar.lat;
        const lon0 = solar.lon;
        const tanDec = Math.tan(dec * rad);

        const terminatorPoints = [];
        const step = 2; // degrees for smooth curve
        for (let lon = -180; lon <= 180; lon += step) {{
          let dLon = (lon - lon0) * rad;
          let lat = 0;
          if (Math.abs(tanDec) < 1e-6) {{
            lat = 0;
          }} else {{
            lat = Math.atan(-Math.cos(dLon) / tanDec) / rad;
          }}
          // Clamp latitude to Web Mercator bounds (85.05 deg)
          lat = Math.max(-85.05, Math.min(85.05, lat));
          terminatorPoints.push([lat, lon]);
        }}

        // Determine which pole is in darkness
        // If dec > 0 (Northern summer), North pole is in daylight, South pole is in night.
        // If dec < 0 (Northern winter), South pole is in daylight, North pole is in night.
        const darkPoleLat = dec >= 0 ? -85.05 : 85.05;

        const polyCoords = [...terminatorPoints];
        polyCoords.push([darkPoleLat, 180]);
        polyCoords.push([darkPoleLat, -180]);
        polyCoords.push(terminatorPoints[0]);

        return polyCoords;
      }}

      // Night Shadow Layer
      let nightPolygon = null;
      let subsolarMarker = null;

      function updateTerminator(date) {{
        const solar = getSolarCoordinates(date);
        const polyCoords = computeTerminatorPolygon(solar);

        // Update or create night polygon
        if (!nightPolygon) {{
          nightPolygon = L.polygon(polyCoords, {{
            pane: 'nightShadowPane',
            fillColor: '#050a18',
            fillOpacity: 0.65,
            stroke: true,
            color: '#f59e0b',
            weight: 1.5,
            opacity: 0.85,
            interactive: false
          }});
          if (currentBaseKey === 'daynight') {{
            nightPolygon.addTo(map);
          }}
        }} else {{
          nightPolygon.setLatLngs(polyCoords);
        }}

        // Update Subsolar Marker
        const sunLat = solar.lat;
        const sunLon = solar.lon;
        const sunIcon = L.divIcon({{
          className: 'subsolar-marker-wrap',
          html: '<div class="subsolar-marker">☀️</div>',
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        }});

        if (!subsolarMarker) {{
          subsolarMarker = L.marker([sunLat, sunLon], {{ icon: sunIcon, interactive: true }});
          subsolarMarker.bindPopup(`
            <div style="font-size: 12px; line-height: 1.5;">
              <strong style="color: #f59e0b;">☀️ Subsolar Point (Zenith)</strong><br>
              The Sun is directly overhead at 90° elevation.<br>
              <strong>Latitude:</strong> ${{sunLat.toFixed(2)}}° (${{sunLat >= 0 ? 'N' : 'S'}})<br>
              <strong>Longitude:</strong> ${{sunLon.toFixed(2)}}° (${{sunLon >= 0 ? 'E' : 'W'}})<br>
              <em style="color: #94a3b8; font-size: 10.5px;">Local Solar Noon</em>
            </div>
          `);
          if (document.getElementById('chk-sun').checked) {{
            subsolarMarker.addTo(map);
          }}
        }} else {{
          subsolarMarker.setLatLng([sunLat, sunLon]);
        }}

        // Update Clock Display & Coordinates
        const pad = (n) => String(n).padStart(2, '0');
        const utcStr = `${{pad(date.getUTCHours())}}:${{pad(date.getUTCMinutes())}}:${{pad(date.getUTCSeconds())}} UTC`;

        // IST is UTC + 5h 30m
        const istDate = new Date(date.getTime() + (5.5 * 3600 * 1000));
        const istStr = `${{pad(istDate.getUTCHours())}}:${{pad(istDate.getUTCMinutes())}}:${{pad(istDate.getUTCSeconds())}} IST`;

        document.getElementById('time-utc').textContent = utcStr;
        document.getElementById('time-ist').textContent = istStr;
        document.getElementById('subsolar-coords').textContent =
          `Lat: ${{Math.abs(sunLat).toFixed(1)}}°${{sunLat >= 0 ? 'N' : 'S'}}, Lon: ${{Math.abs(sunLon).toFixed(1)}}°${{sunLon >= 0 ? 'E' : 'W'}}`;
      }}

      // 4. Live Clock & Scrubber Loop
      let isPlaying = false;
      let playTimer = null;
      let scrubOffsetMinutes = 0;

      function getCurrentSimDate() {{
        const now = new Date();
        return new Date(now.getTime() + (scrubOffsetMinutes * 60 * 1000));
      }}

      function tick() {{
        if (!isPlaying) {{
          const simDate = getCurrentSimDate();
          updateTerminator(simDate);
        }}
      }}

      setInterval(tick, 1000);
      tick();

      // Scrubber Interaction
      const scrubber = document.getElementById('time-scrubber');
      const scrubLabel = document.getElementById('scrub-offset-label');

      scrubber.addEventListener('input', (e) => {{
        scrubOffsetMinutes = parseInt(e.target.value, 10);
        if (scrubOffsetMinutes === 0) {{
          scrubLabel.textContent = 'Live';
        }} else {{
          const hrs = (scrubOffsetMinutes / 60).toFixed(1);
          scrubLabel.textContent = `${{scrubOffsetMinutes > 0 ? '+' : ''}}${{hrs}}h`;
        }}
        updateTerminator(getCurrentSimDate());
      }});

      document.getElementById('btn-live').addEventListener('click', () => {{
        scrubOffsetMinutes = 0;
        scrubber.value = 0;
        scrubLabel.textContent = 'Live';
        if (isPlaying) togglePlay();
        updateTerminator(getCurrentSimDate());
      }});

      const btnPlay = document.getElementById('btn-play');
      function togglePlay() {{
        isPlaying = !isPlaying;
        if (isPlaying) {{
          btnPlay.textContent = '⏸ Pause';
          playTimer = setInterval(() => {{
            scrubOffsetMinutes = (scrubOffsetMinutes + 15);
            if (scrubOffsetMinutes > 720) scrubOffsetMinutes = -720;
            scrubber.value = scrubOffsetMinutes;
            const hrs = (scrubOffsetMinutes / 60).toFixed(1);
            scrubLabel.textContent = `${{scrubOffsetMinutes > 0 ? '+' : ''}}${{hrs}}h`;
            updateTerminator(getCurrentSimDate());
          }}, 120);
        }} else {{
          btnPlay.textContent = '▶ Play 24h';
          clearInterval(playTimer);
        }}
      }}
      btnPlay.addEventListener('click', togglePlay);

      // 5. Basemap Switcher
      const pillButtons = document.querySelectorAll('.pill-btn');
      pillButtons.forEach(btn => {{
        btn.addEventListener('click', () => {{
          pillButtons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          const layerKey = btn.dataset.layer;
          currentBaseKey = layerKey;

          // Remove existing base layer
          if (activeBaseLayer && map.hasLayer(activeBaseLayer)) {{
            map.removeLayer(activeBaseLayer);
          }}

          if (layerKey === 'daynight') {{
            activeBaseLayer = baseLayers.bluemarble;
            activeBaseLayer.addTo(map);
            if (nightPolygon && !map.hasLayer(nightPolygon)) {{
              nightPolygon.addTo(map);
            }}
            if (!map.hasLayer(nightLightsOverlay)) {{
              nightLightsOverlay.addTo(map);
            }}
          }} else {{
            activeBaseLayer = baseLayers[layerKey];
            activeBaseLayer.addTo(map);
            if (nightPolygon && map.hasLayer(nightPolygon)) {{
              map.removeLayer(nightPolygon);
            }}
            if (map.hasLayer(nightLightsOverlay)) {{
              map.removeLayer(nightLightsOverlay);
            }}
          }}
        }});
      }});

      // 6. Vector Layers: Survey of India, World Borders & Disputed Borders
      let soiLayer = null;
      let worldBordersLayer = null;
      let disputedLayer = null;
      let graticuleLayer = null;
      let labelMarkers = [];

      // Find India Feature in WORLD_DATA
      const indiaFeature = WORLD_DATA.features.find(f => f.properties && f.properties.name === 'India');

      // 6a. Survey of India (SOI) Layer
      if (indiaFeature) {{
        soiLayer = L.geoJSON(indiaFeature, {{
          style: {{
            color: '#f59e0b',
            weight: 2.6,
            opacity: 1,
            fillColor: '#f59e0b',
            fillOpacity: 0.08
          }},
          onEachFeature: (feature, layer) => {{
            layer.bindPopup(`
              <div style="font-size: 12px; line-height: 1.5;">
                <strong style="color: #f59e0b; font-size: 13px;">🇮🇳 Republic of India</strong><br>
                <strong>Boundary:</strong> 100% Official Survey of India (SOI)<br>
                <strong>Status:</strong> Authoritative Sovereign Territory<br>
                <em>Includes Jammu & Kashmir, Ladakh, Aksai Chin, Siachen, Arunachal Pradesh, Andaman & Nicobar, Lakshadweep</em><br>
                <a href="${{feature.properties.wiki || 'https://en.wikipedia.org/wiki/India'}}" target="_blank" style="color: #38bdf8;">Wikipedia Article ↗</a>
              </div>
            `);
          }}
        }}).addTo(map);
      }}

      // 6b. Disputed Borders (Light Dashed Line: Serbia-Kosovo, Morocco-SADR, Bir Tawil)
      if (WORLD_DATA.dashed_borders) {{
        disputedLayer = L.geoJSON(WORLD_DATA.dashed_borders, {{
          style: {{
            color: '#e2e8f0',
            weight: 1.6,
            dashArray: '4, 4',
            opacity: 0.95
          }},
          onEachFeature: (feature, layer) => {{
            layer.bindPopup(`
              <div style="font-size: 11.5px;">
                <strong style="color: #e2e8f0;">⚠️ Disputed Border Line</strong><br>
                ${{feature.properties.name || 'Disputed Territory'}}<br>
                <em style="color: #94a3b8;">Google Maps format light dashed line</em>
              </div>
            `);
          }}
        }}).addTo(map);
      }}

      // 6c. World Country Boundaries
      const otherCountries = WORLD_DATA.features.filter(f => f.properties && f.properties.name !== 'India');
      worldBordersLayer = L.geoJSON(otherCountries, {{
        style: {{
          color: '#cbd5e1',
          weight: 0.8,
          opacity: 0.6,
          fillColor: '#ffffff',
          fillOpacity: 0.0
        }},
        onEachFeature: (feature, layer) => {{
          const props = feature.properties;
          layer.bindPopup(`
            <div style="font-size: 12px; line-height: 1.5;">
              <strong style="font-size: 13px; color: #fff;">${{props.name}}</strong><br>
              <strong>ISO Code:</strong> ${{props.iso_a2 || props.iso_a3 || 'N/A'}}<br>
              <strong>Centroid:</strong> ${{props.centroid ? props.centroid[1].toFixed(2) + '°N, ' + props.centroid[0].toFixed(2) + '°E' : 'N/A'}}<br>
              <a href="${{props.wiki || '#'}}" target="_blank" style="color: #38bdf8;">Wikipedia Information ↗</a>
            </div>
          `);
        }}
      }}).addTo(map);

      // 6d. Graticule Lines (Parallels & Meridians)
      function createGraticuleLayer() {{
        const gratGroup = L.layerGroup();
        const gratStyle = {{ color: '#94a3b8', weight: 0.65, opacity: 0.45, dashArray: '2, 3' }};
        const majorGratStyle = {{ color: '#38bdf8', weight: 1.0, opacity: 0.65 }};

        // Parallels (-80 to 80 step 20)
        for (let lat = -80; lat <= 80; lat += 20) {{
          const isEquator = (lat === 0);
          L.polyline([[lat, -180], [lat, 180]], isEquator ? majorGratStyle : gratStyle).addTo(gratGroup);
        }}

        // Meridians (-180 to 180 step 30)
        for (let lon = -180; lon <= 180; lon += 30) {{
          const isPrime = (lon === 0);
          L.polyline([[-85, lon], [85, lon]], isPrime ? majorGratStyle : gratStyle).addTo(gratGroup);
        }}

        return gratGroup;
      }}

      graticuleLayer = createGraticuleLayer();
      graticuleLayer.addTo(map);

      // 6e. Country Labels (Bold, Google Maps Format)
      function updateLabels() {{
        labelMarkers.forEach(m => map.removeLayer(m));
        labelMarkers = [];

        if (!document.getElementById('chk-labels').checked) return;

        const currentZoom = map.getZoom();

        WORLD_DATA.features.forEach(feat => {{
          const props = feat.properties;
          if (!props || !props.centroid) return;

          const isIndia = props.name === 'India';
          const isMajor = ['United States', 'China', 'Russia', 'Brazil', 'Canada', 'Australia', 'India'].includes(props.name);

          if (currentZoom <= 3 && !isMajor && !isIndia) return;
          if (currentZoom <= 4 && props.is_dependency) return;

          const lat = props.centroid[1];
          const lon = props.centroid[0];

          const fontSize = isIndia ? '12px' : (isMajor ? '11px' : '9.5px');
          const fontWeight = isIndia ? '800' : '700';
          const fontColor = isIndia ? '#f59e0b' : '#ffffff';

          const labelIcon = L.divIcon({{
            className: 'country-label-wrapper',
            html: `<div class="country-label-marker" style="font-size: ${{fontSize}}; font-weight: ${{fontWeight}}; color: ${{fontColor}};">${{props.name}}</div>`,
            iconSize: [100, 20],
            iconAnchor: [50, 10]
          }});

          const marker = L.marker([lat, lon], {{ icon: labelIcon, interactive: false }});
          marker.addTo(map);
          labelMarkers.push(marker);
        }});
      }}

      map.on('zoomend', updateLabels);
      updateLabels();

      // Checkbox Toggles
      document.getElementById('chk-soi').addEventListener('change', (e) => {{
        if (e.target.checked) {{
          if (soiLayer) soiLayer.addTo(map);
        }} else {{
          if (soiLayer) map.removeLayer(soiLayer);
        }}
      }});

      document.getElementById('chk-disputed').addEventListener('change', (e) => {{
        if (e.target.checked) {{
          if (disputedLayer) disputedLayer.addTo(map);
        }} else {{
          if (disputedLayer) map.removeLayer(disputedLayer);
        }}
      }});

      document.getElementById('chk-borders').addEventListener('change', (e) => {{
        if (e.target.checked) {{
          if (worldBordersLayer) worldBordersLayer.addTo(map);
        }} else {{
          if (worldBordersLayer) map.removeLayer(worldBordersLayer);
        }}
      }});

      document.getElementById('chk-graticule').addEventListener('change', (e) => {{
        if (e.target.checked) {{
          if (graticuleLayer) graticuleLayer.addTo(map);
        }} else {{
          if (graticuleLayer) map.removeLayer(graticuleLayer);
        }}
      }});

      document.getElementById('chk-labels').addEventListener('change', updateLabels);

      document.getElementById('chk-sun').addEventListener('change', (e) => {{
        if (e.target.checked) {{
          if (subsolarMarker) subsolarMarker.addTo(map);
        }} else {{
          if (subsolarMarker) map.removeLayer(subsolarMarker);
        }}
      }});

      // 7. Search & Auto-complete
      const searchInput = document.getElementById('country-search');
      const dataList = document.getElementById('country-list');

      WORLD_DATA.features.forEach(f => {{
        const opt = document.createElement('option');
        opt.value = f.properties.name;
        dataList.appendChild(opt);
      }});

      searchInput.addEventListener('change', () => {{
        const query = searchInput.value.trim().toLowerCase();
        const feat = WORLD_DATA.features.find(f => f.properties.name.toLowerCase() === query);
        if (feat && feat.properties.centroid) {{
          const lat = feat.properties.centroid[1];
          const lon = feat.properties.centroid[0];
          map.flyTo([lat, lon], 5, {{ duration: 1.5 }});
        }}
      }});

      // 8. Dock & Quick Navigation Shortcuts
      document.getElementById('dock-india').addEventListener('click', () => {{
        map.flyTo([22.0, 78.5], 5, {{ duration: 1.2 }});
      }});
      document.getElementById('btn-fly-india').addEventListener('click', () => {{
        map.flyTo([22.0, 78.5], 5, {{ duration: 1.2 }});
      }});

      document.getElementById('dock-sun').addEventListener('click', () => {{
        const solar = getSolarCoordinates(getCurrentSimDate());
        map.flyTo([solar.lat, solar.lon], 4, {{ duration: 1.5 }});
      }});

      document.getElementById('dock-himalayas').addEventListener('click', () => {{
        map.flyTo([32.5, 77.5], 6, {{ duration: 1.4 }});
      }});

      document.getElementById('dock-global').addEventListener('click', () => {{
        map.flyTo([15.0, 0.0], 2, {{ duration: 1.2 }});
      }});
      document.getElementById('btn-fly-global').addEventListener('click', () => {{
        map.flyTo([15.0, 0.0], 2, {{ duration: 1.2 }});
      }});

      document.getElementById('dock-americas').addEventListener('click', () => {{
        map.flyTo([15.0, -85.0], 3, {{ duration: 1.2 }});
      }});

      document.getElementById('dock-asia').addEventListener('click', () => {{
        map.flyTo([15.0, 115.0], 3, {{ duration: 1.2 }});
      }});

      document.getElementById('dock-europe').addEventListener('click', () => {{
        map.flyTo([25.0, 20.0], 3, {{ duration: 1.2 }});
      }});

      // 9. Mobile Controls Toggle
      const mobileToggleBtn = document.getElementById('mobile-toggle-btn');
      const controlsPanel = document.getElementById('controls-panel');
      const chevron = document.getElementById('chevron');

      mobileToggleBtn.addEventListener('click', () => {{
        controlsPanel.classList.toggle('open');
        chevron.textContent = controlsPanel.classList.contains('open') ? '▴' : '▾';
      }});

    }})();
  </script>
</body>
</html>
"""

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"[✓] Successfully generated {HTML_OUTPUT} ({HTML_OUTPUT.stat().st_size:,} bytes)")

if __name__ == "__main__":
    generate_satellite_html()
