"""Tests for web studio compilation."""

import pytest
from pathlib import Path
from equal_earth.web_builder import build_interactive_html, get_sample_datasets_json


def test_get_sample_datasets_json():
    """Verify sample datasets JSON serialization for web studio."""
    json_str = get_sample_datasets_json()
    assert "literacy" in json_str
    assert "forest_cover" in json_str
    assert "renewable_energy" in json_str
    assert "population_density" in json_str


def test_build_interactive_html(tmp_path):
    """Verify compilation of standalone interactive HTML web studio."""
    out_file = tmp_path / "studio_test.html"
    result = build_interactive_html(initial_mode="india", output_path=out_file, sync_index=False)
    assert result.exists()
    assert result.stat().st_size > 1000000  # Over 1MB with embedded data
    content = result.read_text(encoding="utf-8")
    assert "Equal Earth India Maps · Geospatial Studio" in content
    assert "d3.geoEqualEarth" in content
    assert "WORLD_DATA" in content
    assert "INDIA_STATES_DATA" in content
