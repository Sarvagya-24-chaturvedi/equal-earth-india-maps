"""
Builder script to generate the standalone satellite_day_night.html portal.
Embeds world_data.json for 100% offline & local file:// compatibility,
linking with local leaflet.js and leaflet.css.
Includes:
- Integrated Time & Live Climate Dashboard (reflects real-time temperature of the visited place)
- NASA Blue Marble (Topography & Bathymetry)
- NASA MODIS Terra TrueColor (Daily Real-Time Satellite Pass)
- NASA Black Marble (VIIRS Earth at Night)
- NASA NDSI Daily Snow & Ice Cover Layer (visualizes snow-covered regions across Earth)
- Real-time Solar Terminator (Astronomical GMST & Subsolar Declination)
- Survey of India 100% sovereign boundary (J&K, Ladakh, Aksai Chin, Siachen, Arunachal Pradesh)
- Disputed borders in light dashed lines (Serbia-Kosovo, Morocco-SADR, Bir Tawil)
- Latitude/Longitude graticule grid
- 24h interactive solar scrubber & simulation playback
- Live UTC and IST clocks + Visited Location Local Time & Weather
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

    # Compact ISO-A2 -> IANA timezone. MULTI:* is resolved from lat/lon in JS.
    iana_by_iso = {
        "AF": "Asia/Kabul", "AX": "Europe/Helsinki", "AL": "Europe/Tirane", "DZ": "Africa/Algiers",
        "AS": "Pacific/Pago_Pago", "AD": "Europe/Andorra", "AO": "Africa/Luanda", "AI": "America/Anguilla",
        "AQ": "MULTI:AQ", "AG": "America/Antigua", "AR": "America/Argentina/Buenos_Aires", "AM": "Asia/Yerevan",
        "AW": "America/Aruba", "AU": "MULTI:AU", "AT": "Europe/Vienna", "AZ": "Asia/Baku",
        "BH": "Asia/Bahrain", "BD": "Asia/Dhaka", "BB": "America/Barbados", "BY": "Europe/Minsk",
        "BE": "Europe/Brussels", "BZ": "America/Belize", "BJ": "Africa/Porto-Novo", "BM": "Atlantic/Bermuda",
        "BT": "Asia/Thimphu", "BO": "America/La_Paz", "BA": "Europe/Sarajevo", "BW": "Africa/Gaborone",
        "BR": "MULTI:BR", "IO": "Indian/Chagos", "VG": "America/Tortola", "BN": "Asia/Brunei",
        "BG": "Europe/Sofia", "BF": "Africa/Ouagadougou", "BI": "Africa/Bujumbura", "CF": "Africa/Bangui",
        "CV": "Atlantic/Cape_Verde", "KH": "Asia/Phnom_Penh", "CM": "Africa/Douala", "CA": "MULTI:CA",
        "KY": "America/Cayman", "TD": "Africa/Ndjamena", "CL": "MULTI:CL", "CN": "Asia/Shanghai",
        "CO": "America/Bogota", "KM": "Indian/Comoro", "CG": "Africa/Brazzaville", "CK": "Pacific/Rarotonga",
        "CR": "America/Costa_Rica", "HR": "Europe/Zagreb", "CU": "America/Havana", "CW": "America/Curacao",
        "CY": "Asia/Nicosia", "CZ": "Europe/Prague", "CD": "MULTI:CD", "DK": "Europe/Copenhagen",
        "DJ": "Africa/Djibouti", "DM": "America/Dominica", "DO": "America/Santo_Domingo", "TL": "Asia/Dili",
        "EC": "MULTI:EC", "EG": "Africa/Cairo", "SV": "America/El_Salvador", "GQ": "Africa/Malabo",
        "ER": "Africa/Asmara", "EE": "Europe/Tallinn", "ET": "Africa/Addis_Ababa", "FK": "Atlantic/Stanley",
        "FO": "Atlantic/Faroe", "FJ": "Pacific/Fiji", "FI": "Europe/Helsinki", "PF": "MULTI:PF",
        "TF": "Indian/Kerguelen", "GA": "Africa/Libreville", "GM": "Africa/Banjul", "GE": "Asia/Tbilisi",
        "DE": "Europe/Berlin", "GH": "Africa/Accra", "GI": "Europe/Gibraltar", "GR": "Europe/Athens",
        "GL": "MULTI:GL", "GD": "America/Grenada", "GU": "Pacific/Guam", "GT": "America/Guatemala",
        "GG": "Europe/Guernsey", "GN": "Africa/Conakry", "GW": "Africa/Bissau", "GY": "America/Guyana",
        "HT": "America/Port-au-Prince", "HN": "America/Tegucigalpa", "HK": "Asia/Hong_Kong", "HU": "Europe/Budapest",
        "IS": "Atlantic/Reykjavik", "IN": "Asia/Kolkata", "ID": "MULTI:ID", "IR": "Asia/Tehran",
        "IQ": "Asia/Baghdad", "IE": "Europe/Dublin", "IM": "Europe/Isle_of_Man", "IL": "Asia/Jerusalem",
        "IT": "Europe/Rome", "CI": "Africa/Abidjan", "JM": "America/Jamaica", "JP": "Asia/Tokyo",
        "JE": "Europe/Jersey", "JO": "Asia/Amman", "KZ": "MULTI:KZ", "KE": "Africa/Nairobi",
        "KI": "MULTI:KI", "KW": "Asia/Kuwait", "KG": "Asia/Bishkek", "LA": "Asia/Vientiane",
        "LV": "Europe/Riga", "LB": "Asia/Beirut", "LS": "Africa/Maseru", "LR": "Africa/Monrovia",
        "LY": "Africa/Tripoli", "LI": "Europe/Vaduz", "LT": "Europe/Vilnius", "LU": "Europe/Luxembourg",
        "MO": "Asia/Macau", "MG": "Indian/Antananarivo", "MW": "Africa/Blantyre", "MY": "Asia/Kuala_Lumpur",
        "MV": "Indian/Maldives", "ML": "Africa/Bamako", "MT": "Europe/Malta", "MH": "Pacific/Majuro",
        "MR": "Africa/Nouakchott", "MU": "Indian/Mauritius", "MX": "MULTI:MX", "FM": "MULTI:FM",
        "MD": "Europe/Chisinau", "MC": "Europe/Monaco", "MN": "Asia/Ulaanbaatar", "ME": "Europe/Podgorica",
        "MS": "America/Montserrat", "MA": "Africa/Casablanca", "MZ": "Africa/Maputo", "MM": "Asia/Yangon",
        "NA": "Africa/Windhoek", "NR": "Pacific/Nauru", "NP": "Asia/Kathmandu", "NL": "Europe/Amsterdam",
        "NC": "Pacific/Noumea", "NZ": "MULTI:NZ", "NI": "America/Managua", "NE": "Africa/Niamey",
        "NG": "Africa/Lagos", "NU": "Pacific/Niue", "NF": "Pacific/Norfolk", "KP": "Asia/Pyongyang",
        "MK": "Europe/Skopje", "MP": "Pacific/Saipan", "OM": "Asia/Muscat", "PK": "Asia/Karachi",
        "PW": "Pacific/Palau", "PS": "Asia/Gaza", "PA": "America/Panama", "PG": "Pacific/Port_Moresby",
        "PY": "America/Asuncion", "PE": "America/Lima", "PH": "Asia/Manila", "PN": "Pacific/Pitcairn",
        "PL": "Europe/Warsaw", "PT": "MULTI:PT", "PR": "America/Puerto_Rico", "QA": "Asia/Qatar",
        "RO": "Europe/Bucharest", "RU": "MULTI:RU", "RW": "Africa/Kigali", "BL": "America/St_Barthelemy",
        "SH": "Atlantic/St_Helena", "LC": "America/St_Lucia", "MF": "America/Marigot", "PM": "America/Miquelon",
        "WS": "Pacific/Apia", "SM": "Europe/San_Marino", "SA": "Asia/Riyadh", "SN": "Africa/Dakar",
        "RS": "Europe/Belgrade", "SC": "Indian/Mahe", "SL": "Africa/Freetown", "SG": "Asia/Singapore",
        "SX": "America/Lower_Princes", "SK": "Europe/Bratislava", "SI": "Europe/Ljubljana", "SB": "Pacific/Guadalcanal",
        "SO": "Africa/Mogadishu", "ZA": "Africa/Johannesburg", "GS": "Atlantic/South_Georgia", "KR": "Asia/Seoul",
        "SS": "Africa/Juba", "ES": "MULTI:ES", "LK": "Asia/Colombo", "KN": "America/St_Kitts",
        "VC": "America/St_Vincent", "SD": "Africa/Khartoum", "SR": "America/Paramaribo", "SE": "Europe/Stockholm",
        "CH": "Europe/Zurich", "SY": "Asia/Damascus", "ST": "Africa/Sao_Tome", "CN-TW": "Asia/Taipei",
        "TJ": "Asia/Dushanbe", "TZ": "Africa/Dar_es_Salaam", "TH": "Asia/Bangkok", "BS": "America/Nassau",
        "TG": "Africa/Lome", "TO": "Pacific/Tongatapu", "TT": "America/Port_of_Spain", "TN": "Africa/Tunis",
        "TR": "Europe/Istanbul", "TM": "Asia/Ashgabat", "TC": "America/Grand_Turk", "TV": "Pacific/Funafuti",
        "AE": "Asia/Dubai", "UG": "Africa/Kampala", "UA": "Europe/Kyiv", "GB": "Europe/London",
        "US": "MULTI:US", "VI": "America/St_Thomas", "UY": "America/Montevideo", "UZ": "Asia/Tashkent",
        "VU": "Pacific/Efate", "VA": "Europe/Vatican", "VE": "America/Caracas", "VN": "Asia/Ho_Chi_Minh",
        "WF": "Pacific/Wallis", "EH": "Africa/El_Aaiun", "YE": "Asia/Aden", "ZM": "Africa/Lusaka",
        "ZW": "Africa/Harare", "SZ": "Africa/Mbabane"
    }
    iana_json = json.dumps(iana_by_iso, separators=(",", ":"))

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

    .badge-weather {{
      background: rgba(56, 189, 248, 0.2);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.5);
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
      max-width: 520px;
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
      min-width: 60px;
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

    .toggle-chip.highlight-snow {{
      border-color: rgba(56, 189, 248, 0.45);
      background: rgba(14, 116, 144, 0.25);
    }}

    /* Integrated Time & Live Climate Card */
    .clock-display-card {{
      background: rgba(15, 23, 42, 0.82);
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 9px;
      padding: 9px 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
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

    /* Integrated Visited Place Live Climate Row */
    .visited-climate-row {{
      background: rgba(30, 41, 59, 0.75);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 8px;
      padding: 7px 11px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      transition: all 0.2s ease;
    }}

    .visited-top-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}

    .visited-loc-badge {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #f8fafc;
    }}

    .visited-time-val {{
      font-size: 11px;
      font-weight: 700;
      color: #fbbf24;
      font-family: ui-monospace, SFMono-Regular, monospace;
    }}

    .visited-climate-details {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 1px;
    }}

    .visited-temp-val {{
      font-size: 17px;
      font-weight: 900;
      color: #38bdf8;
      font-variant-numeric: tabular-nums;
    }}

    .visited-desc {{
      font-size: 11px;
      color: #e2e8f0;
      font-weight: 600;
    }}

    .visited-meta {{
      font-size: 10.5px;
      color: #94a3b8;
      display: flex;
      align-items: center;
      gap: 6px;
      margin-left: auto;
    }}

    .w-snow-pill {{
      background: rgba(56, 189, 248, 0.22);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.5);
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 800;
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
      background: rgba(15, 23, 42, 0.96) !important;
      backdrop-filter: blur(12px);
      color: #f8fafc !important;
      border: 1px solid rgba(148, 163, 184, 0.3) !important;
      border-radius: 10px !important;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important;
    }}

    .leaflet-popup-tip {{
      background: rgba(15, 23, 42, 0.96) !important;
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
    .country-label-wrapper {{
      background: transparent !important;
      border: none !important;
    }}

    .country-label-marker {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 10.5px;
      font-weight: 700;
      color: #ffffff;
      text-shadow: 0 0 3px #000, 0 0 6px #000, 1px 1px 2px #000;
      white-space: nowrap;
      pointer-events: none;
      transform: translate(-50%, -50%);
      text-align: center;
      line-height: 1;
      letter-spacing: -0.15px;
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

    /* Weather Popup Card */
    .weather-popup-card {{
      padding: 4px;
      min-width: 210px;
    }}

    .weather-popup-card .w-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(148, 163, 184, 0.25);
      padding-bottom: 6px;
      margin-bottom: 6px;
    }}

    .weather-popup-card .w-city-title {{
      font-size: 13.5px;
      font-weight: 800;
      color: #f8fafc;
    }}

    .weather-popup-card .w-main-temp {{
      font-size: 26px;
      font-weight: 900;
      color: #38bdf8;
      line-height: 1;
      display: flex;
      align-items: baseline;
      gap: 6px;
      margin: 8px 0;
    }}

    .weather-popup-card .w-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      font-size: 11px;
      color: #cbd5e1;
      margin-top: 8px;
    }}

    .weather-popup-card .w-grid-item {{
      background: rgba(30, 41, 59, 0.65);
      padding: 4px 6px;
      border-radius: 5px;
      border: 1px solid rgba(148, 163, 184, 0.15);
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
          <span>🛰️ Topographic Satellite & Real-Time Day/Night Map</span>
          <span class="badge badge-soi">SOI Sovereign Boundary</span>
          <span class="badge badge-weather">🌡️ Live Climate & Time</span>
          <span class="badge badge-live"><span class="badge-pulse"></span> NASA & Open-Meteo</span>
        </h1>
        <p>Live Climate & Local Time of Visited Place · NASA Snow Cover · Real-Time Solar Terminator</p>
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

      <!-- Overlays (Snow, Sovereign Borders, Grid) -->
      <div class="ctrl-row">
        <span class="ctrl-label">Overlays:</span>
        <label class="toggle-chip highlight-snow">
          <input type="checkbox" id="chk-snow" checked>
          <span>❄️ NASA Snow & Ice Cover</span>
        </label>
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

      <!-- Live Clock & Solar Scrubber WITH INTEGRATED VISITED PLACE LIVE CLIMATE -->
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

        <!-- Integrated Visited Location Time & Live Climate Display -->
        <div class="visited-climate-row" id="visited-climate-row">
          <div class="visited-top-bar">
            <div class="visited-loc-badge">
              <span id="visited-flag">🇮🇳</span>
              <strong id="visited-name">India (New Delhi)</strong>
            </div>
            <span class="visited-time-val" id="visited-local-time">--:-- Local Time</span>
          </div>
          <div class="visited-climate-details">
            <span class="visited-temp-val" id="visited-temp">--°C</span>
            <span id="visited-icon">☀️</span>
            <span class="visited-desc" id="visited-desc">Fetching live climate...</span>
            <div class="visited-meta">
              <span id="visited-humidity-wind">💧 --% · 💨 -- km/h</span>
              <span id="visited-snow-tag" class="w-snow-pill" style="display:none;">❄️ Snow: -- cm</span>
            </div>
          </div>
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
        <button class="btn-sm" id="btn-fly-istanbul">🇹🇷 Fly Istanbul</button>
        <button class="btn-sm" id="btn-fly-global">🌐 Global (0°)</button>
      </div>
    </div>
  </div>

  <!-- Bottom Quick Fly Dock -->
  <div class="bottom-dock">
    <button class="dock-pill active" id="dock-india">🇮🇳 India (Official SOI)</button>
    <button class="dock-pill" id="dock-istanbul">🇹🇷 Istanbul (Visited)</button>
    <button class="dock-pill" id="dock-himalayas">🏔️ Himalayas & Siachen</button>
    <button class="dock-pill" id="dock-sun">☀️ Subsolar Zenith</button>
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
      const IANA_BY_ISO = {iana_json};
      const IANA_BY_NAME = {{
        'France': 'Europe/Paris',
        'Norway': 'Europe/Oslo',
        'Kosovo': 'Europe/Belgrade',
        'Turkey': 'Europe/Istanbul',
        'Indian Ocean Territories': 'Indian/Chagos'
      }};

      // 1. Initialize Leaflet Map
      // Centered on India with SOI boundary view
      const map = L.map('map', {{
        center: [22.0, 78.5],
        zoom: 4,
        minZoom: 2,
        maxZoom: 19,
        worldCopyJump: true,
        zoomControl: false,
        bounceAtZoomLimits: false
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

      // 3) snowCoverPane (z-index 415) for NASA NDSI Snow Cover
      map.createPane('snowCoverPane');
      map.getPane('snowCoverPane').style.zIndex = 415;
      map.getPane('snowCoverPane').style.pointerEvents = 'none';

      const tileOpts = {{ noWrap: false, keepBuffer: 6, crossOrigin: false }};

      // 2. Base Tile Layers (NASA GIBS WMTS, ESRI, OpenTopoMap)
      const baseLayers = {{
        bluemarble: L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/default/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.jpeg', {{
          subdomains: 'abc',
          maxNativeZoom: 8,
          maxZoom: 19,
          attribution: 'Imagery © NASA Earthdata GIBS (Blue Marble)',
          ...tileOpts
        }}),
        modis: L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/' + MODIS_DATE + '/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg', {{
          subdomains: 'abc',
          maxNativeZoom: 9,
          maxZoom: 19,
          attribution: 'Daily Satellite Pass © NASA Terra / MODIS (' + MODIS_DATE + ')',
          ...tileOpts
        }}),
        blackmarble: L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/default/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.png', {{
          subdomains: 'abc',
          maxNativeZoom: 8,
          maxZoom: 19,
          attribution: 'Night Lights © NASA Suomi NPP / VIIRS Black Marble',
          ...tileOpts
        }}),
        opentopo: L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
          maxZoom: 17,
          attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)',
          ...tileOpts
        }}),
        esri: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
          maxZoom: 19,
          attribution: 'High-Res Satellite © Esri, Maxar, Earthstar Geographics',
          ...tileOpts
        }})
      }};

      // Active Base Layer State (Default: Live Day/Night)
      let currentBaseKey = 'daynight';
      let activeBaseLayer = baseLayers.bluemarble;
      activeBaseLayer.addTo(map);

      // Night Lights Screen Overlay for Day/Night Composite
      const nightLightsOverlay = L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/default/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.png', {{
        subdomains: 'abc',
        maxNativeZoom: 8,
        maxZoom: 19,
        pane: 'nightLightsPane',
        opacity: 0.85,
        attribution: 'Night Lights: NASA VIIRS',
        ...tileOpts
      }});
      nightLightsOverlay.addTo(map);

      // 3. NASA NDSI Daily Snow & Ice Cover Layer
      const snowCoverLayer = L.tileLayer('https://gibs-{{s}}.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_NDSI_Snow_Cover/default/' + MODIS_DATE + '/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.png', {{
        subdomains: 'abc',
        maxNativeZoom: 8,
        maxZoom: 19,
        pane: 'snowCoverPane',
        opacity: 0.75,
        attribution: 'Snow & Ice Cover © NASA Terra / MODIS NDSI (' + MODIS_DATE + ')',
        ...tileOpts
      }});
      snowCoverLayer.addTo(map);

      // 4. Astronomical Solar Terminator Calculations
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

      function terminatorLatAt(solar, lon) {{
        const tanDec = Math.tan(solar.lat * rad);
        if (Math.abs(tanDec) < 1e-6) return 0;
        const lat = Math.atan(-Math.cos((lon - solar.lon) * rad) / tanDec) / rad;
        return Math.max(-85.05, Math.min(85.05, lat));
      }}

      function computeMultiWorldTerminator(solar, westLon, eastLon) {{
        const step = 2;
        const startLon = Math.floor(westLon / step) * step;
        const endLon = Math.ceil(eastLon / step) * step;
        const terminatorPoints = [];

        for (let lon = startLon; lon <= endLon; lon += step) {{
          terminatorPoints.push([terminatorLatAt(solar, lon), lon]);
        }}

        const darkPoleLat = solar.lat >= 0 ? -85.05 : 85.05;
        const polyCoords = [...terminatorPoints];
        polyCoords.push([darkPoleLat, endLon]);
        polyCoords.push([darkPoleLat, startLon]);
        polyCoords.push(terminatorPoints[0]);

        return polyCoords;
      }}

      // Night Shadow Layer
      let nightPolygon = null;
      let subsolarMarker = null;

      function updateTerminator(date) {{
        const solar = getSolarCoordinates(date);
        const bounds = map.getBounds();
        const west = Math.min(-180, bounds.getWest() - 360);
        const east = Math.max(180, bounds.getEast() + 360);
        const polyCoords = computeMultiWorldTerminator(solar, west, east);

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
        let mapCenterLon = map.getCenter().lng;
        let sunLon = ((solar.lon - mapCenterLon) % 360);
        if (sunLon < -180) sunLon += 360;
        if (sunLon > 180) sunLon -= 360;
        sunLon += mapCenterLon;

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
              <strong>Longitude:</strong> ${{solar.lon.toFixed(2)}}° (${{solar.lon >= 0 ? 'E' : 'W'}})<br>
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

        const istDate = new Date(date.getTime() + (5.5 * 3600 * 1000));
        const istStr = `${{pad(istDate.getUTCHours())}}:${{pad(istDate.getUTCMinutes())}}:${{pad(istDate.getUTCSeconds())}} IST`;

        document.getElementById('time-utc').textContent = utcStr;
        document.getElementById('time-ist').textContent = istStr;
        document.getElementById('subsolar-coords').textContent =
          `Lat: ${{Math.abs(sunLat).toFixed(1)}}°${{sunLat >= 0 ? 'N' : 'S'}}, Lon: ${{Math.abs(solar.lon).toFixed(1)}}°${{solar.lon >= 0 ? 'E' : 'W'}}`;

        // Also update visited place local time
        updateVisitedLocalTimeDisplay(date);
      }}

      // 5. Visited Place State & Climate Integration
      let currentVisitedPlace = {{
        name: 'India (New Delhi)',
        flag: '🇮🇳',
        lat: 28.6139,
        lon: 77.2090,
        tz: 'Asia/Kolkata',
        temp: null,
        desc: 'Loading...',
        icon: '☀️',
        humidity: null,
        wind: null,
        snowCm: null
      }};

      const weatherCache = new Map();

      function decodeWeather(code, isDay) {{
        switch (code) {{
          case 0: return {{ icon: isDay ? '☀️' : '🌙', desc: 'Clear sky' }};
          case 1: return {{ icon: isDay ? '🌤️' : '🌤️', desc: 'Mainly clear' }};
          case 2: return {{ icon: isDay ? '⛅' : '⛅', desc: 'Partly cloudy' }};
          case 3: return {{ icon: '☁️', desc: 'Overcast' }};
          case 45:
          case 48: return {{ icon: '🌫️', desc: 'Foggy' }};
          case 51:
          case 53:
          case 55: return {{ icon: '🌧️', desc: 'Drizzle' }};
          case 61:
          case 63:
          case 65: return {{ icon: '🌧️', desc: 'Rain' }};
          case 71:
          case 73:
          case 75: return {{ icon: '❄️', desc: 'Snowfall' }};
          case 77: return {{ icon: '❄️', desc: 'Snow grains' }};
          case 80:
          case 81:
          case 82: return {{ icon: '🌦️', desc: 'Rain showers' }};
          case 85:
          case 86: return {{ icon: '🌨️', desc: 'Snow showers' }};
          case 95:
          case 96:
          case 99: return {{ icon: '⛈️', desc: 'Thunderstorm' }};
          default: return {{ icon: isDay ? '☀️' : '🌙', desc: 'Fair' }};
        }}
      }}

      function resolveTimezoneForCoord(lat, lon, iso) {{
        if (iso && IANA_BY_ISO[iso] && !IANA_BY_ISO[iso].startsWith('MULTI:')) {{
          return IANA_BY_ISO[iso];
        }}
        // Known custom cities
        if (Math.abs(lat - 41.0) < 1.0 && Math.abs(lon - 29.0) < 1.5) return 'Europe/Istanbul';
        if (Math.abs(lat - 28.6) < 1.0 && Math.abs(lon - 77.2) < 1.5) return 'Asia/Kolkata';
        if (Math.abs(lat - 51.5) < 1.0 && Math.abs(lon - (-0.1)) < 1.5) return 'Europe/London';
        if (Math.abs(lat - 40.7) < 1.0 && Math.abs(lon - (-74.0)) < 1.5) return 'America/New_York';
        if (Math.abs(lat - 35.7) < 1.0 && Math.abs(lon - 139.7) < 1.5) return 'Asia/Tokyo';
        return null;
      }}

      function formatTimeForTz(date, tz, lon) {{
        const pad = (n) => String(n).padStart(2, '0');
        if (tz) {{
          try {{
            const fmt = new Intl.DateTimeFormat('en-GB', {{
              timeZone: tz,
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
            }});
            return fmt.format(date) + ' Local (' + tz.split('/').pop().replace('_', ' ') + ')';
          }} catch(e) {{}}
        }}
        // Solar time approximation from longitude
        const lonOffsetHours = lon / 15.0;
        const solarDate = new Date(date.getTime() + (lonOffsetHours * 3600 * 1000));
        const sign = lonOffsetHours >= 0 ? '+' : '';
        const offsetHours = Math.floor(Math.abs(lonOffsetHours));
        const offsetMins = Math.round((Math.abs(lonOffsetHours) - offsetHours) * 60);
        const offsetStr = `UTC${{sign}}${{Math.floor(lonOffsetHours)}}:${{String(offsetMins).padStart(2, '0')}}`;
        return `${{pad(solarDate.getUTCHours())}}:${{pad(solarDate.getUTCMinutes())}}:${{pad(solarDate.getUTCSeconds())}} (${{offsetStr}})`;
      }}

      function updateVisitedLocalTimeDisplay(simDate) {{
        const timeStr = formatTimeForTz(simDate, currentVisitedPlace.tz, currentVisitedPlace.lon);
        const el = document.getElementById('visited-local-time');
        if (el) el.textContent = timeStr;
      }}

      async function setVisitedPlace(name, flag, lat, lon, iso) {{
        currentVisitedPlace.name = name;
        currentVisitedPlace.flag = flag || '📍';
        currentVisitedPlace.lat = lat;
        currentVisitedPlace.lon = lon;
        currentVisitedPlace.tz = resolveTimezoneForCoord(lat, lon, iso);

        document.getElementById('visited-flag').textContent = currentVisitedPlace.flag;
        document.getElementById('visited-name').textContent = currentVisitedPlace.name;
        document.getElementById('visited-desc').textContent = 'Fetching live climate...';
        updateVisitedLocalTimeDisplay(getCurrentSimDate());

        const cacheKey = `${{lat.toFixed(2)}},${{lon.toFixed(2)}}`;
        if (weatherCache.has(cacheKey)) {{
          applyWeatherToUI(weatherCache.get(cacheKey));
          return;
        }}

        try {{
          let normLon = ((lon + 180) % 360) - 180;
          if (normLon < -180) normLon += 360;
          const url = `https://api.open-meteo.com/v1/forecast?latitude=${{lat.toFixed(4)}}&longitude=${{normLon.toFixed(4)}}&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,snow_depth,snowfall,wind_speed_10m,is_day`;
          const res = await fetch(url);
          const data = await res.json();
          if (data && data.current) {{
            weatherCache.set(cacheKey, data.current);
            applyWeatherToUI(data.current);
          }}
        }} catch(e) {{
          document.getElementById('visited-desc').textContent = 'Live climate unavailable';
        }}
      }}

      function applyWeatherToUI(curr) {{
        const temp = Math.round(curr.temperature_2m);
        const feels = Math.round(curr.apparent_temperature);
        const w = decodeWeather(curr.weather_code, curr.is_day);
        const hasSnow = curr.snow_depth > 0 || curr.snowfall > 0;
        const snowCm = (curr.snow_depth * 100).toFixed(0);

        document.getElementById('visited-temp').textContent = `${{temp}}°C`;
        document.getElementById('visited-icon').textContent = w.icon;
        document.getElementById('visited-desc').textContent = `${{w.desc}} · Feels ${{feels}}°C`;
        document.getElementById('visited-humidity-wind').textContent = `💧 ${{curr.relative_humidity_2m || 70}}% · 💨 ${{curr.wind_speed_10m || 10}} km/h`;

        const snowTag = document.getElementById('visited-snow-tag');
        if (hasSnow && snowTag) {{
          snowTag.style.display = 'inline-block';
          snowTag.textContent = `❄️ Snow: ${{snowCm > 0 ? snowCm + 'cm' : 'Active'}}`;
        }} else if (snowTag) {{
          snowTag.style.display = 'none';
        }}
      }}

      // Set initial visited place to India (New Delhi)
      setVisitedPlace('India (New Delhi)', '🇮🇳', 28.6139, 77.2090, 'IN');

      // 6. Live Clock & Scrubber Loop
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

      map.on('move', () => {{
        updateTerminator(getCurrentSimDate());
      }});

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

      // 7. Basemap Switcher
      const pillButtons = document.querySelectorAll('.pill-btn');
      pillButtons.forEach(btn => {{
        btn.addEventListener('click', () => {{
          pillButtons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          const layerKey = btn.dataset.layer;
          currentBaseKey = layerKey;

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

      // 8. Interactive Click-to-Inspect Live Climate & Time on Map Click
      map.on('click', async (e) => {{
        const lat = e.latlng.lat;
        let normLon = ((e.latlng.lng + 180) % 360) - 180;
        if (normLon < -180) normLon += 360;

        const coordLabel = `${{Math.abs(lat).toFixed(2)}}°${{lat >= 0 ? 'N' : 'S'}}, ${{Math.abs(normLon).toFixed(2)}}°${{normLon >= 0 ? 'E' : 'W'}}`;
        setVisitedPlace(coordLabel, '📍', lat, normLon, null);

        const popup = L.popup()
          .setLatLng(e.latlng)
          .setContent('<div style="font-size: 12px; color: #94a3b8; padding: 6px;">📡 Fetching live climate & local time...</div>')
          .openOn(map);

        try {{
          const url = `https://api.open-meteo.com/v1/forecast?latitude=${{lat.toFixed(4)}}&longitude=${{normLon.toFixed(4)}}&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,snow_depth,snowfall,wind_speed_10m,is_day`;
          const res = await fetch(url);
          const data = await res.json();
          const curr = data.current;
          const temp = Math.round(curr.temperature_2m);
          const feels = Math.round(curr.apparent_temperature);
          const w = decodeWeather(curr.weather_code, curr.is_day);
          const hasSnow = curr.snow_depth > 0 || curr.snowfall > 0;
          const snowCm = (curr.snow_depth * 100).toFixed(1);
          const localTimeStr = formatTimeForTz(getCurrentSimDate(), null, normLon);

          popup.setContent(`
            <div class="weather-popup-card">
              <div class="w-header">
                <span class="w-city-title">📍 ${{coordLabel}}</span>
                <span style="font-size: 10px; color: var(--text-muted);">${{w.desc}}</span>
              </div>
              <div style="font-size: 11px; color: #fbbf24; font-weight: 700; margin-bottom: 4px;">🕒 ${{localTimeStr}}</div>
              <div class="w-main-temp">
                <span>${{w.icon}}</span>
                <span>${{temp}}°C</span>
                <span style="font-size: 12px; font-weight: 500; color: #94a3b8; margin-left: 6px;">Feels ${{feels}}°C</span>
              </div>
              ${{hasSnow ? `<div style="background: rgba(56, 189, 248, 0.2); border: 1px solid #38bdf8; border-radius: 6px; padding: 4px 8px; font-size: 11px; color: #e0f2fe; margin: 4px 0;">❄️ Snow cover depth: <strong>${{snowCm}} cm</strong></div>` : ''}}
              <div class="w-grid">
                <div class="w-grid-item">💧 Humidity: <strong>${{curr.relative_humidity_2m}}%</strong></div>
                <div class="w-grid-item">💨 Wind: <strong>${{curr.wind_speed_10m}} km/h</strong></div>
                <div class="w-grid-item">🌧️ Rain: <strong>${{curr.precipitation}} mm</strong></div>
                <div class="w-grid-item">❄️ Snowfall: <strong>${{curr.snowfall}} cm</strong></div>
              </div>
            </div>
          `);
        }} catch(e) {{
          popup.setContent('<div style="font-size: 11px; color: #ef4444; padding: 4px;">Weather data currently unavailable for this point.</div>');
        }}
      }});

      // 9. Vector Layers: Survey of India, World Borders & Disputed Borders
      let soiLayer = null;
      let worldBordersLayer = null;
      let disputedLayer = null;
      let graticuleLayer = null;
      let labelMarkers = [];

      const indiaFeature = WORLD_DATA.features.find(f => f.properties && f.properties.name === 'India');

      // 9a. Survey of India (SOI) Layer
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
            layer.on('click', () => {{
              setVisitedPlace('India', '🇮🇳', 28.6139, 77.2090, 'IN');
            }});
          }}
        }}).addTo(map);
      }}

      // 9b. Disputed Borders (Light Dashed Line: Serbia-Kosovo, Morocco-SADR, Bir Tawil)
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

      // 9c. World Country Boundaries
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
          layer.on('click', () => {{
            if (props.centroid) {{
              setVisitedPlace(props.name, '📍', props.centroid[1], props.centroid[0], props.iso_a2);
            }}
          }});
        }}
      }}).addTo(map);

      // 9d. Graticule Lines (Parallels & Meridians)
      function createGraticuleLayer() {{
        const gratGroup = L.layerGroup();
        const gratStyle = {{ color: '#94a3b8', weight: 0.65, opacity: 0.45, dashArray: '2, 3' }};
        const majorGratStyle = {{ color: '#38bdf8', weight: 1.0, opacity: 0.65 }};

        for (let lat = -80; lat <= 80; lat += 20) {{
          const isEquator = (lat === 0);
          L.polyline([[lat, -540], [lat, 540]], isEquator ? majorGratStyle : gratStyle).addTo(gratGroup);
        }}

        for (let lon = -540; lon <= 540; lon += 30) {{
          const isPrime = (((lon % 360) + 360) % 360 === 0);
          L.polyline([[-85, lon], [85, lon]], isPrime ? majorGratStyle : gratStyle).addTo(gratGroup);
        }}

        return gratGroup;
      }}

      graticuleLayer = createGraticuleLayer();
      graticuleLayer.addTo(map);

      // 9e. Country Labels (Bold, Google Maps Format)
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
            iconSize: [0, 0],
            iconAnchor: [0, 0]
          }});

          const marker = L.marker([lat, lon], {{ icon: labelIcon, interactive: false }});
          marker.addTo(map);
          labelMarkers.push(marker);
        }});
      }}

      map.on('zoomend', updateLabels);
      updateLabels();

      // Checkbox Toggles
      document.getElementById('chk-snow').addEventListener('change', (e) => {{
        if (e.target.checked) {{
          snowCoverLayer.addTo(map);
        }} else {{
          map.removeLayer(snowCoverLayer);
        }}
      }});

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

      // 10. Search & Auto-complete
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
          setVisitedPlace(feat.properties.name, '📍', lat, lon, feat.properties.iso_a2);
        }}
      }});

      // 11. Dock & Quick Navigation Shortcuts
      document.getElementById('dock-india').addEventListener('click', () => {{
        map.flyTo([22.0, 78.5], 5, {{ duration: 1.2 }});
        setVisitedPlace('India (New Delhi)', '🇮🇳', 28.6139, 77.2090, 'IN');
      }});
      document.getElementById('btn-fly-india').addEventListener('click', () => {{
        map.flyTo([22.0, 78.5], 5, {{ duration: 1.2 }});
        setVisitedPlace('India (New Delhi)', '🇮🇳', 28.6139, 77.2090, 'IN');
      }});

      document.getElementById('dock-istanbul').addEventListener('click', () => {{
        map.flyTo([41.0082, 28.9784], 7, {{ duration: 1.5 }});
        setVisitedPlace('Istanbul (Turkey)', '🇹🇷', 41.0082, 28.9784, 'TR');
      }});
      document.getElementById('btn-fly-istanbul').addEventListener('click', () => {{
        map.flyTo([41.0082, 28.9784], 7, {{ duration: 1.5 }});
        setVisitedPlace('Istanbul (Turkey)', '🇹🇷', 41.0082, 28.9784, 'TR');
      }});

      document.getElementById('dock-himalayas').addEventListener('click', () => {{
        map.flyTo([32.5, 77.5], 6, {{ duration: 1.4 }});
        setVisitedPlace('Himalayas (Siachen & Kashmir)', '🏔️', 34.0837, 74.7973, 'IN');
      }});

      document.getElementById('dock-sun').addEventListener('click', () => {{
        const solar = getSolarCoordinates(getCurrentSimDate());
        map.flyTo([solar.lat, solar.lon], 4, {{ duration: 1.5 }});
        setVisitedPlace('Subsolar Point (Zenith)', '☀️', solar.lat, solar.lon, null);
      }});

      document.getElementById('dock-global').addEventListener('click', () => {{
        map.flyTo([15.0, 0.0], 2, {{ duration: 1.2 }});
        setVisitedPlace('Prime Meridian (0°)', '🌐', 15.0, 0.0, null);
      }});
      document.getElementById('btn-fly-global').addEventListener('click', () => {{
        map.flyTo([15.0, 0.0], 2, {{ duration: 1.2 }});
        setVisitedPlace('Prime Meridian (0°)', '🌐', 15.0, 0.0, null);
      }});

      document.getElementById('dock-americas').addEventListener('click', () => {{
        map.flyTo([15.0, -85.0], 3, {{ duration: 1.2 }});
        setVisitedPlace('Americas', '🌎', 15.0, -85.0, null);
      }});

      document.getElementById('dock-asia').addEventListener('click', () => {{
        map.flyTo([15.0, 115.0], 3, {{ duration: 1.2 }});
        setVisitedPlace('East Asia & Pacific', '🌏', 15.0, 115.0, null);
      }});

      document.getElementById('dock-europe').addEventListener('click', () => {{
        map.flyTo([25.0, 20.0], 3, {{ duration: 1.2 }});
        setVisitedPlace('Europe & Africa', '🌍', 25.0, 20.0, null);
      }});

      // 12. Mobile Controls Toggle
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
