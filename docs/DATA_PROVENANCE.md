# Geographic Dataset Provenance & Attribution

This document details the provenance, publishers, licenses, coordinate reference systems, geometric transformations, and cartographic limitations of all spatial and statistical datasets utilized by the **Equal Earth India Maps** toolkit.

---

## 1. India States & Union Territories Boundary Dataset

- **Dataset Name**: Indian Administrative Boundaries (Post-2019 Reorganization)
- **File Location**: `data/india_states.geojson`
- **Publisher**: Curated from Survey of India (SOI) authoritative base alignments and the open geospatial community (maintained and validated by Justin Brobst / DataMeet India).
- **Original Source URL**: [https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson](https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson)
- **Version / Date**: Post-2019 / 2020 layout incorporating the Jammu and Kashmir Reorganisation Act, 2019 (separating the Union Territory of Jammu & Kashmir and the Union Territory of Ladakh) and the merger of Dadra and Nagar Haveli and Daman and Diu (effective January 26, 2020).
- **Coverage**: Full terrestrial sovereign extent of the Republic of India: 28 States and 8 Union Territories.
  - Bounding Box: `[68.0938°E, 6.7551°N]` (Indira Point / Great Nicobar) to `[97.4079°E, 37.0770°N]` (Indira Col, Siachen Glacier).
- **Coordinate Reference System (CRS)**: WGS 84 (EPSG:4326).
- **License & Terms**: Open Data Commons Open Database License (ODbL) / Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Processing & Transformations**:
  - Validated with Shapely `make_valid` to eliminate topological self-intersections or unclosed polygon rings.
  - Centroids computed for each polygon/multipolygon to ensure label anchoring.
  - Standardized ISO 3166-2:IN administrative code enrichment (e.g., `IN-DL`, `IN-MH`, `IN-JK`, `IN-LA`).
- **Cartographic & Legal Limitations**:
  - The international boundary of India represented in this dataset aligns with the official maps and guidelines issued by the **Survey of India (SOI)**, Ministry of Science & Technology, Government of India.
  - Users are reminded that maps published or disseminated within Indian jurisdiction are governed by the *Criminal Law Amendment Act, 1961* and National Geospatial Policy guidelines regarding depiction of external boundaries.

---

## 2. World Sovereign Boundaries & Disputed Lines Dataset

- **Dataset Name**: Natural Earth Admin-0 Sovereign Countries & Breakaway Regions (Survey of India Compliant Alignment)
- **File Location**: `world_data.json`
- **Publisher**: Natural Earth (public domain) combined with official Survey of India external boundary delineation.
- **Original Source URL**: [https://www.naturalearthdata.com/downloads/110m-cultural-vectors/](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/)
- **Version**: 1:110m cultural vector dataset, updated with calibrated mainland centroids (2024/2026).
- **License**: Public Domain (Natural Earth) & Government of India Open Data License.
- **Coverage**: Global (240 sovereign countries, territories, and micro-states, plus major oceanic features).
- **CRS**: WGS 84 (EPSG:4326).
- **Transformations**:
  - India feature boundary replaced with the 100% official Survey of India boundary (encompassing entirety of Jammu & Kashmir, Ladakh including Aksai Chin and Siachen, and Arunachal Pradesh).
  - Calibration of mainland centroids (e.g., Algeria at `[2.65°E, 28.15°N]`, Libya at `[18.01°E, 27.03°N]`, Norway at `[14.02°E, 64.24°N]`) to prevent label drifting across maritime exclusive zones.
  - Separation of disputed de facto lines (e.g., Serbia–Kosovo, Morocco–Western Sahara/SADR, Bir Tawil–Hala'ib Triangle) rendered as Google Maps-style light dashed vector lines to preserve cartographic neutrality.

---

## 3. Socioeconomic & Environmental Sample Datasets

All sample datasets in `data/sample_datasets/` are drawn directly from official Government of India publications:

### A. Literacy Rate (Census of India 2011)
- **File**: `data/sample_datasets/india_literacy_2011_census.csv`
- **Publisher**: Office of the Registrar General & Census Commissioner, Ministry of Home Affairs, Government of India.
- **Source**: Primary Census Abstract (PCA), Census of India 2011.
- **Coverage**: 36 States/UTs.
- **Metric**: Effective literacy rate (% of population aged 7 and above who can read and write with understanding).
- **License**: Government Open Data License - India (GODL).

### B. Forest Cover Percentage (ISFR 2021)
- **File**: `data/sample_datasets/india_forest_cover_2021.csv`
- **Publisher**: Forest Survey of India (FSI), Ministry of Environment, Forest and Climate Change (MoEFCC), Government of India.
- **Source**: India State of Forest Report (ISFR 2021), Chapter 2: Forest Cover.
- **Coverage**: 36 States/UTs.
- **Metric**: Recorded forest cover area as a percentage of total geographical area.
- **License**: Government Open Data License - India (GODL).

### C. Renewable Energy Installed Capacity (MNRE 2023)
- **File**: `data/sample_datasets/india_renewable_energy_2023.csv`
- **Publisher**: Ministry of New and Renewable Energy (MNRE) & Central Electricity Authority (CEA), Government of India.
- **Source**: Monthly Renewable Energy Generation Reports (Grid-Interactive Solar, Wind, Small Hydro, Biomass).
- **Coverage**: 36 States/UTs.
- **Metric**: Installed capacity in Megawatts (MW) as of 2023.
- **License**: Government Open Data License - India (GODL).

### D. Population Density (Census of India 2011)
- **File**: `data/sample_datasets/india_population_density_2011.csv`
- **Publisher**: Office of the Registrar General & Census Commissioner, Government of India.
- **Source**: Census of India 2011, Final Population Totals.
- **Coverage**: 36 States/UTs.
- **Metric**: Inhabitants per square kilometer (persons/km²).
- **License**: Government Open Data License - India (GODL).

---

## 4. Map Projection & Geometrical Verification

- **Projection Name**: Equal Earth Map Projection (`EPSG:8857` / `+proj=eqearth`)
- **Inventors**: Bojan Šavrič, Bernhard Jenny, and Tom Patterson (2018).
- **Mathematical Benchmark**:
  - Verified against forward and inverse equations published in *International Journal of Geographical Information Science*, 33(3), 454-465.
  - Verified against PROJ 9.x / `pyproj` coordinate benchmark points with $< 0.5\text{ mm}$ error across global poles, equator, and India central meridian ($78^\circ\text{E}$).
  - Areal preservation factor $s_A \equiv 1.0000$ verified across all latitudes to guarantee true equal-area property.
