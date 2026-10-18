"""Tests for geographic data loading, geometry validation, topological repairs, and state aliases."""

import pytest
from pathlib import Path
from equal_earth.data import (
    load_world_data,
    load_india_states,
    load_sample_dataset,
    validate_and_repair_geometry,
    normalize_state_name,
    find_entity,
    STATE_ISO_CODES,
)
from equal_earth.exceptions import DataValidationError


def test_load_world_data():
    """Verify loading and properties of the global sovereign dataset."""
    world = load_world_data()
    assert world["type"] == "FeatureCollection"
    assert len(world["features"]) >= 200
    assert "oceans" in world
    assert "dashed_borders" in world

    india_feat = next((f for f in world["features"] if f["properties"].get("name") == "India"), None)
    assert india_feat is not None
    assert india_feat["properties"]["iso_a3"] == "IND"


def test_load_india_states():
    """Verify loading of the 36 Indian states and union territories with valid geometries."""
    states = load_india_states()
    assert states["type"] == "FeatureCollection"
    assert len(states["features"]) == 36

    names = {f["properties"]["st_nm"] for f in states["features"]}
    assert "Jammu & Kashmir" in names
    assert "Ladakh" in names
    assert "Dadra and Nagar Haveli and Daman and Diu" in names
    assert "Delhi" in names

    for feat in states["features"]:
        props = feat["properties"]
        assert "st_code" in props
        assert props["st_code"].startswith("IN-")
        assert "centroid" in props
        assert len(props["centroid"]) == 2
        # Check coordinate bounds
        lon, lat = props["centroid"]
        assert 68.0 <= lon <= 98.0
        assert 6.0 <= lat <= 38.0


def test_state_name_normalization():
    """Verify alias normalization across common variations."""
    assert normalize_state_name("J&K") == "Jammu & Kashmir"
    assert normalize_state_name("Jammu and Kashmir") == "Jammu & Kashmir"
    assert normalize_state_name("Orissa") == "Odisha"
    assert normalize_state_name("NCT of Delhi") == "Delhi"
    assert normalize_state_name("Delhi UT") == "Delhi"
    assert normalize_state_name("Pondicherry") == "Puducherry"
    assert normalize_state_name("Uttaranchal") == "Uttarakhand"
    assert normalize_state_name("Andaman & Nicobar Islands") == "Andaman & Nicobar"


def test_geometry_validation_and_repair():
    """Verify that invalid geometries are detected or repaired."""
    import shapely.geometry
    # Valid polygon
    poly = shapely.geometry.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    valid_poly = validate_and_repair_geometry(poly)
    assert valid_poly.is_valid

    # Bowtie self-intersecting polygon
    bowtie = shapely.geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])
    assert not bowtie.is_valid
    repaired = validate_and_repair_geometry(bowtie)
    assert repaired.is_valid

    # Empty geometry raises error
    empty = shapely.geometry.Polygon()
    with pytest.raises(DataValidationError):
        validate_and_repair_geometry(empty)

    with pytest.raises(DataValidationError):
        validate_and_repair_geometry(None)


def test_load_sample_datasets():
    """Verify all authentic Government of India sample datasets."""
    datasets = ["literacy", "forest_cover", "renewable_energy", "population_density"]
    for key in datasets:
        rows = load_sample_dataset(key)
        assert len(rows) == 36
        for r in rows:
            assert "state" in r
            assert "value" in r
            assert isinstance(r["value"], (int, float))
            assert "source" in r

    with pytest.raises(DataValidationError):
        load_sample_dataset("nonexistent_metric")


def test_find_entity():
    """Verify entity lookup by exact name, ISO code, ocean name, or substring."""
    world = load_world_data()

    # Exact country
    res1 = find_entity("India", world)
    assert res1 is not None and res1["properties"]["name"] == "India"

    # ISO code
    res2 = find_entity("IND", world)
    assert res2 is not None and res2["properties"]["name"] == "India"

    # Ocean
    res3 = find_entity("Indian Ocean", world)
    assert res3 is not None and res3["properties"]["is_ocean"] is True

    # Case-insensitive
    res4 = find_entity("brazil", world)
    assert res4 is not None and res4["properties"]["name"] == "Brazil"

    # Non-existent
    assert find_entity("Atlantis", world) is None
