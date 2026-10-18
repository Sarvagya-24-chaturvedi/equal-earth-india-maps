"""Data loading, geometry validation, topological repair, and state name reconciliation."""

import os
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

try:
    import shapely.geometry
    from shapely.validation import make_valid
except ImportError:
    shapely = None
    make_valid = None

from equal_earth.exceptions import DataValidationError

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
WORLD_DATA_PATH = BASE_DIR / "world_data.json"
INDIA_STATES_PATH = DATA_DIR / "india_states.geojson"
SAMPLE_DATASETS_DIR = DATA_DIR / "sample_datasets"

# Canonical state name normalization aliases
STATE_NAME_ALIASES: Dict[str, str] = {
    "andaman and nicobar islands": "Andaman & Nicobar",
    "andaman & nicobar islands": "Andaman & Nicobar",
    "andaman and nicobar": "Andaman & Nicobar",
    "andaman & nicobar island": "Andaman & Nicobar",
    "jammu and kashmir": "Jammu & Kashmir",
    "j&k": "Jammu & Kashmir",
    "ladakh (ut)": "Ladakh",
    "ut of ladakh": "Ladakh",
    "nct of delhi": "Delhi",
    "national capital territory of delhi": "Delhi",
    "delhi ut": "Delhi",
    "dadra & nagar haveli and daman & diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra and nagar haveli & daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "daman & diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra and nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra & nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "dnh and dd": "Dadra and Nagar Haveli and Daman and Diu",
    "orissa": "Odisha",
    "uttaranchal": "Uttarakhand",
    "pondicherry": "Puducherry",
    "pondicherry (puducherry)": "Puducherry",
    "chhatisgarh": "Chhattisgarh",
}

# ISO 3166-2:IN codes mapping for all 28 states and 8 union territories
STATE_ISO_CODES: Dict[str, str] = {
    "Andaman & Nicobar": "IN-AN",
    "Andhra Pradesh": "IN-AP",
    "Arunachal Pradesh": "IN-AR",
    "Assam": "IN-AS",
    "Bihar": "IN-BR",
    "Chandigarh": "IN-CH",
    "Chhattisgarh": "IN-CT",
    "Dadra and Nagar Haveli and Daman and Diu": "IN-DH",
    "Delhi": "IN-DL",
    "Goa": "IN-GA",
    "Gujarat": "IN-GJ",
    "Haryana": "IN-HR",
    "Himachal Pradesh": "IN-HP",
    "Jammu & Kashmir": "IN-JK",
    "Jharkhand": "IN-JH",
    "Karnataka": "IN-KA",
    "Kerala": "IN-KL",
    "Ladakh": "IN-LA",
    "Lakshadweep": "IN-LD",
    "Madhya Pradesh": "IN-MP",
    "Maharashtra": "IN-MH",
    "Manipur": "IN-MN",
    "Meghalaya": "IN-ML",
    "Mizoram": "IN-MZ",
    "Nagaland": "IN-NL",
    "Odisha": "IN-OR",
    "Puducherry": "IN-PY",
    "Punjab": "IN-PB",
    "Rajasthan": "IN-RJ",
    "Sikkim": "IN-SK",
    "Tamil Nadu": "IN-TN",
    "Telangana": "IN-TG",
    "Tripura": "IN-TR",
    "Uttar Pradesh": "IN-UP",
    "Uttarakhand": "IN-UT",
    "West Bengal": "IN-WB",
}


def normalize_state_name(name: str) -> str:
    """Normalize state or UT name against canonical list and known variations."""
    if not name or not isinstance(name, str):
        return ""
    clean = name.strip()
    lower = clean.lower()
    if lower in STATE_NAME_ALIASES:
        return STATE_NAME_ALIASES[lower]
    # Check exact case-insensitive match against canonical names
    for canonical in STATE_ISO_CODES.keys():
        if lower == canonical.lower():
            return canonical
    return clean


def validate_and_repair_geometry(geom_dict_or_shape):
    """Validate and automatically repair geometries using Shapely.

    Parameters
    ----------
    geom_dict_or_shape : dict or shapely.geometry.base.BaseGeometry
        GeoJSON geometry mapping or Shapely geometry object.

    Returns
    -------
    shapely.geometry.base.BaseGeometry
        Valid Shapely geometry.

    Raises
    ------
    DataValidationError
        If geometry cannot be validated or is completely empty.
    """
    try:
        import shapely.geometry
        from shapely.validation import make_valid
    except ImportError as e:
        raise DataValidationError("Shapely is required for geometry processing.") from e

    if geom_dict_or_shape is None:
        raise DataValidationError("Geometry cannot be None.")

    if isinstance(geom_dict_or_shape, dict):
        if not geom_dict_or_shape.get("coordinates"):
            raise DataValidationError("Empty coordinates in GeoJSON geometry.")
        try:
            geom = shapely.geometry.shape(geom_dict_or_shape)
        except Exception as e:
            raise DataValidationError(f"Invalid GeoJSON geometry structure: {e}") from e
    else:
        geom = geom_dict_or_shape

    if geom.is_empty:
        raise DataValidationError("Geometry is empty.")

    if not geom.is_valid:
        geom = make_valid(geom)

    return geom


def load_world_data(path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load and validate the global sovereign country and ocean dataset.

    Parameters
    ----------
    path : str or Path, optional
        Custom path to world_data.json, by default uses package default.

    Returns
    -------
    Dict[str, Any]
        GeoJSON FeatureCollection dictionary.

    Raises
    ------
    DataValidationError
        If file is missing, corrupted, or has invalid schema.
    """
    data_file = Path(path) if path else WORLD_DATA_PATH
    if not data_file.exists():
        raise DataValidationError(f"World dataset not found at {data_file}")

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataValidationError(f"Malformed JSON in world dataset: {e}") from e

    if not isinstance(data, dict) or "features" not in data:
        raise DataValidationError("World dataset must be a GeoJSON FeatureCollection with 'features'.")

    return data


def load_india_states(path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load, validate, and enrich the 36 Indian states and union territories dataset.

    Parameters
    ----------
    path : str or Path, optional
        Custom path to india_states.geojson, by default uses package default.

    Returns
    -------
    Dict[str, Any]
        Enriched GeoJSON FeatureCollection dictionary with canonical names, ISO codes,
        and validated centroids.

    Raises
    ------
    DataValidationError
        If dataset cannot be loaded or validated.
    """
    data_file = Path(path) if path else INDIA_STATES_PATH
    if not data_file.exists():
        # Fallback check in current directory
        alt_path = BASE_DIR / "india_states.geojson"
        if alt_path.exists():
            data_file = alt_path
        else:
            raise DataValidationError(f"India states dataset not found at {data_file}")

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataValidationError(f"Malformed JSON in states dataset: {e}") from e

    if not isinstance(data, dict) or "features" not in data or not data["features"]:
        raise DataValidationError("States dataset must contain non-empty 'features' list.")

    enriched_features = []
    for feat in data["features"]:
        props = dict(feat.get("properties", {}))
        raw_name = props.get("ST_NM") or props.get("NAME_1") or props.get("name") or ""
        canonical_name = normalize_state_name(raw_name)
        iso_code = STATE_ISO_CODES.get(canonical_name, props.get("ST_ID", f"IN-{canonical_name[:2].upper()}"))

        # Validate geometry
        geom = validate_and_repair_geometry(feat.get("geometry"))
        centroid = [round(geom.centroid.x, 4), round(geom.centroid.y, 4)]

        props["st_nm"] = canonical_name
        props["st_code"] = iso_code
        props["centroid"] = centroid

        enriched_features.append({
            "type": "Feature",
            "properties": props,
            "geometry": shapely.geometry.mapping(geom)
        })

    return {
        "type": "FeatureCollection",
        "name": "india_states_official",
        "features": enriched_features
    }


def load_sample_dataset(dataset_key: str) -> List[Dict[str, Any]]:
    """Load an authentic Government of India sample dataset for choropleth mapping.

    Parameters
    ----------
    dataset_key : str
        One of 'literacy', 'forest_cover', 'renewable_energy', 'population_density'.

    Returns
    -------
    List[Dict[str, Any]]
        List of row dicts containing 'State_or_UT', 'State_Code', numeric value, and 'Source'.

    Raises
    ------
    DataValidationError
        If dataset key is unknown or CSV file is missing.
    """
    mapping = {
        "literacy": ("india_literacy_2011_census.csv", "Literacy_Rate_Pct"),
        "forest_cover": ("india_forest_cover_2021.csv", "Forest_Cover_Pct"),
        "renewable_energy": ("india_renewable_energy_2023.csv", "Renewable_Capacity_MW"),
        "population_density": ("india_population_density_2011.csv", "Density_per_sq_km"),
    }

    key_clean = dataset_key.strip().lower()
    if key_clean not in mapping:
        valid_keys = ", ".join(mapping.keys())
        raise DataValidationError(f"Unknown sample dataset '{dataset_key}'. Choose from: {valid_keys}")

    filename, val_col = mapping[key_clean]
    csv_path = SAMPLE_DATASETS_DIR / filename
    if not csv_path.exists():
        raise DataValidationError(f"Sample dataset file not found at {csv_path}")

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            val_raw = r.get(val_col)
            try:
                numeric_val = float(val_raw) if val_raw is not None else 0.0
            except ValueError:
                numeric_val = 0.0
            rows.append({
                "state": normalize_state_name(r.get("State_or_UT", "")),
                "state_code": r.get("State_Code", ""),
                "value": numeric_val,
                "metric_name": val_col,
                "source": r.get("Source", "Government of India"),
            })

    return rows


def find_entity(query: str, world_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Search for country, ocean, or micronation with exact and substring match priority."""
    if not query or not isinstance(query, str):
        return None
    query_clean = query.strip().lower()

    # Exact match check (Country / Micronation)
    for feat in world_data.get("features", []):
        props = feat.get("properties", {})
        if query_clean == props.get("name", "").lower() or query_clean in (props.get("iso_a2", "").lower(), props.get("iso_a3", "").lower()):
            return feat

    # Exact match check (Ocean)
    for ocean in world_data.get("oceans", []):
        if query_clean == ocean.get("name", "").lower():
            return {
                "type": "Ocean",
                "properties": {
                    "name": ocean["name"],
                    "centroid": ocean["centroid"],
                    "wiki": ocean.get("wiki", ""),
                    "is_ocean": True
                }
            }

    # Substring match (Ocean)
    for ocean in world_data.get("oceans", []):
        if query_clean in ocean.get("name", "").lower():
            return {
                "type": "Ocean",
                "properties": {
                    "name": ocean["name"],
                    "centroid": ocean["centroid"],
                    "wiki": ocean.get("wiki", ""),
                    "is_ocean": True
                }
            }

    # Substring match (Country)
    for feat in world_data.get("features", []):
        if query_clean in feat.get("properties", {}).get("name", "").lower():
            return feat

    return None
