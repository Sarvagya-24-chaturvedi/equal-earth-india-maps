# Equal Earth India Maps

[![CI](https://github.com/Sarvagya-24-chaturvedi/equal-earth-india-maps/actions/workflows/ci.yml/badge.svg)](https://github.com/Sarvagya-24-chaturvedi/equal-earth-india-maps/actions)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Projection: Equal Earth](https://img.shields.io/badge/Projection-Equal_Earth_EPSG%3A8857-informational.svg)](https://en.wikipedia.org/wiki/Equal_Earth_projection)

A Python cartography toolkit, command-line interface, and interactive web application for generating Equal Earth (`EPSG:8857`) maps of India and the world, incorporating Survey of India administrative boundary delineations.

---

## Live Demos

- **Main Map & Thematic Studio**: [sarvagya-24-chaturvedi.github.io/equal-earth-india-maps/index.html](https://sarvagya-24-chaturvedi.github.io/equal-earth-india-maps/index.html)
- **Satellite & Day/Night Viewer**: [sarvagya-24-chaturvedi.github.io/equal-earth-india-maps/satellite_day_night.html](https://sarvagya-24-chaturvedi.github.io/equal-earth-india-maps/satellite_day_night.html)

---

## Visual Previews

| India Administrative & State Labels | Census 2011 Literacy Rate Choropleth |
| :---: | :---: |
| ![India Administrative Map](examples/outputs/02_india_publication_labeled.png) | ![India Literacy Choropleth](examples/outputs/03_india_literacy_choropleth.png) |

| Global Equal Earth Map (Centered on India, 78°E) | Renewable Energy Installed Capacity (MNRE 2023) |
| :---: | :---: |
| ![Global Equal Earth India Centered](equal_earth_india.png) | ![India Renewable Energy Map](examples/outputs/04_india_renewable_energy.png) |

---

## Key Features

### 1. Equal Earth Projection & Centering
- **True Equal-Area Projection**: Implements the Equal Earth pseudocylindrical formulation (`EPSG:8857`) by Šavrič, Jenny, and Patterson (2018), preserving relative geographic areas without the high-latitude distortion of Mercator.
- **Configurable Central Meridian**: Default centering on India (78°E), the Prime Meridian (0°), or any specified country or ocean coordinate.
- **Verified Math Pipeline**: Forward and inverse polynomial coordinate transformations benchmarked against PROJ 9 reference points.

### 2. India Boundary Data & Attribution
- **Survey of India Alignment**: Depicts official administrative boundaries as specified by the Survey of India (Department of Science & Technology), including the Union Territories of Jammu & Kashmir and Ladakh, as well as Arunachal Pradesh.
- **Post-2019 Reorganization**: Reflects the current 28 states and 8 union territories, including the bifurcation of Jammu & Kashmir and Ladakh, and the merger of Dadra & Nagar Haveli and Daman & Diu.
- **Geometry Validation**: GeoJSON boundaries cleaned, repaired, and validated for topological consistency using Shapely.

### 3. Satellite Imagery & Day/Night Visualization
- **NASA GIBS Tile Layers**: Connects to NASA Global Imagery Browse Services for Blue Marble (bathymetry/topography), MODIS Terra TrueColor, and Black Marble (night lights).
- **Daily Snow & Ice Cover**: Integrates NASA Terra/MODIS daily snow cover imagery.
- **Astronomical Solar Terminator**: Calculates real-time subsolar position and twilight boundaries using Greenwich Mean Sidereal Time (GMST) and solar declination algorithms.
- **Coordinate-Aware Timezones**: Dynamic IANA timezone detection based on clicked map coordinates across multi-timezone nations.

### 4. Map Export & Publishing Workflow
- **Multi-Format Output**: High-resolution raster PNG (150, 300, and 600 DPI), scalable vector SVG, and vector PDF.
- **Data-Driven Thematic Mapping**: Built-in state-name normalizer matching Government of India datasets (Census 2011, ISFR 2021, MNRE 2023) and user-supplied CSV files.
- **Cartographic Themes**: Preconfigured styles including `atlas_light`, `academic_clean`, `carto_dark`, `emerald_nature`, and `sunset_warm`.

---

## Requirements & Offline / Online Scope

### Software Requirements
- **Python**: 3.9, 3.10, 3.11, or 3.12
- **Core Dependencies**: `matplotlib>=3.8.0`, `cartopy>=0.22.0`, `shapely>=2.0.0`, `numpy>=1.24.0`, `pyproj>=3.6.0`
- **Optional / Dev**: `pytest>=8.0.0`, `pytest-cov>=4.0.0`

### Offline vs. Online Capabilities
- **Local / Fully Offline**:
  - Python CLI and SDK (`equal_earth` package).
  - Administrative boundary rendering, choropleth generation, and projection math.
  - Interactive D3 studio (`index.html` / `equal_earth_interactive.html`) using bundled `world_data.json`.
- **Requires Network Access**:
  - External satellite tile services in `satellite_day_night.html` (NASA GIBS tiles, ESRI satellite imagery).

---

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Sarvagya-24-chaturvedi/equal-earth-india-maps.git
cd equal-earth-india-maps

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and the package
pip install -r requirements.txt
pip install -e .
```

### 2. Command-Line Interface (CLI)

The package provides the `equal-earth` executable:

```bash
# Generate a standard publication-ready India map (PNG, 300 DPI)
equal-earth india --theme atlas_light -o india_admin.png

# Generate a choropleth using built-in Census 2011 literacy data
equal-earth india --choropleth literacy --palette YlGnBu -o india_literacy.png

# Generate a choropleth from a custom CSV file
equal-earth india --choropleth path/to/data.csv --palette Oranges -o custom_choro.png

# Export as vector PDF or SVG
equal-earth india --theme academic_clean -o india_vector.pdf
equal-earth india --theme academic_clean -o india_vector.svg

# Generate a global Equal Earth map centered on India (78°E)
equal-earth global --center-lon 78.0 -o world_india.png

# Verify projection math against PROJ reference values
equal-earth project --benchmark

# Launch the interactive web studio in your default browser
equal-earth web
```

### 3. Python API Quickstart

```python
from equal_earth import (
    render_india_map,
    render_global_map,
    load_sample_dataset,
    generate_choropleth,
    forward,
    inverse,
)

# 1. Render an administrative map of India
render_india_map(
    theme="academic_clean",
    show_labels=True,
    title="Republic of India",
    output_path="india_map.png",
    dpi=300,
)

# 2. Render a data-driven choropleth map
data = load_sample_dataset("literacy")
choro = generate_choropleth(data, palette="YlGnBu", num_classes=5)

render_india_map(
    choropleth=choro,
    title="India — Literacy Rate (Census 2011)",
    legend_title="Literacy (%)",
    unit="%",
    output_path="india_literacy.png",
)

# 3. Direct Equal Earth coordinate projection
x, y = forward(lon_deg=78.0, lat_deg=20.0)
lon, lat = inverse(x=x, y=y)
```

### 4. Rebuilding Standalone Web Pages

```bash
# Rebuild the D3-based interactive studio (index.html)
python3 map.py

# Rebuild the Leaflet-based NASA satellite & day/night viewer
python3 build_satellite.py
```

---

## Project Structure

```
equal-earth-india-maps/
├── equal_earth/                  # Core Python mapping package
│   ├── projection.py             # Equal Earth math (forward/inverse & PROJ benchmarks)
│   ├── data.py                   # Boundary loader, geometry validation & name normalizer
│   ├── styling.py                # Color palettes and cartographic themes
│   ├── thematic.py               # Choropleth classification & data joins
│   ├── renderer.py               # Matplotlib & Cartopy rendering pipeline
│   ├── web_builder.py            # Web studio page builder
│   ├── cli.py                    # Command-line interface implementation
│   └── exceptions.py             # Custom toolkit exception classes
├── data/
│   ├── india_states.geojson      # India 28 states & 8 UTs (Survey of India alignment)
│   └── sample_datasets/          # Built-in CSV datasets (Census 2011, ISFR, MNRE)
├── docs/
│   └── DATA_PROVENANCE.md        # Comprehensive dataset documentation & sources
├── examples/
│   ├── 01_india_states.py        # Example: Clean administrative boundaries
│   ├── 02_publication_labeled_map.py
│   ├── 03_india_choropleth.py    # Example: Thematic mapping
│   ├── 04_renewable_energy_choropleth.py
│   ├── 05_high_res_export.py     # Example: 600 DPI, SVG, PDF export
│   └── outputs/                  # Generated sample maps
├── tests/                        # Automated test suite (pytest)
├── world_data.json               # Global country geometries with SOI India border
├── index.html                    # Interactive web studio (Equal Earth / D3)
├── satellite_day_night.html      # NASA satellite & day/night viewer (Leaflet)
├── map.py                        # Standalone studio builder script
├── build_satellite.py            # Standalone satellite portal builder script
├── pyproject.toml                # Package configuration & entry points
└── requirements.txt              # Core Python dependencies
```

---

## Testing

The automated test suite verifies coordinate transformation benchmarks, geometry loading, state name normalization, choropleth generation, theme styling, multi-format exports, and CLI execution.

Run the test suite with:

```bash
pytest tests/ -v
```

---

## Data Sources, Attribution & Limitations

- **Territorial Boundaries**: Administrative boundaries for India follow delineations published by the **Survey of India (Department of Science & Technology, Government of India)**.
  - *Cartographic Note*: Boundaries reflect official Indian cartographic specifications. Third-party international basemaps and tile providers may display differing boundary lines or lines of control. This project is an independent open-source toolkit and does not imply official government endorsement or certification.
- **Statistical Datasets**:
  - *Census of India (2011)*: Office of the Registrar General & Census Commissioner.
  - *India State of Forest Report (ISFR 2021)*: Forest Survey of India.
  - *Renewable Energy Capacity (2023)*: Ministry of New and Renewable Energy & Central Electricity Authority.
- **Equal Earth Projection**: Developed by Bojan Šavrič, Bernhard Jenny, and Tom Patterson (2018). Reference: *A polynomial equation for the Equal Earth map projection*, International Journal of Geographical Information Science, 33(3), 454–465.
- **Satellite Imagery**: NASA Global Imagery Browse Services (GIBS), part of the NASA Earth Observing System Data and Information System (EOSDIS).
- For complete provenance details, refer to [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md).

---

## Contributing

Contributions and feedback are welcome:
1. Ensure territorial boundary geometry conforms to official Survey of India delineations.
2. Maintain mathematical consistency with the Equal Earth projection specification.
3. Add unit tests for any new features or bug fixes under `tests/`.
4. Open an issue or submit a pull request on GitHub.

---

## License

- **Source Code**: [MIT License](LICENSE).
- **Documentation & Data**: Dataset sources retain their respective original licenses (see [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md)).
