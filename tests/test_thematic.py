"""Tests for choropleth matching, color interpolation, and classification bins."""

import pytest
from equal_earth.thematic import (
    match_data_to_states,
    generate_choropleth,
    interpolate_color,
    hex_to_rgb,
    rgb_to_hex,
)
from equal_earth.data import load_sample_dataset, STATE_ISO_CODES
from equal_earth.exceptions import DataValidationError


def test_color_utilities():
    """Verify hex to rgb and linear color interpolation."""
    assert hex_to_rgb("#ffffff") == (255, 255, 255)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert rgb_to_hex((255, 0, 0)) == "#ff0000"

    # Midpoint between black and white
    mid = interpolate_color("#000000", "#ffffff", 0.5)
    assert mid == "#808080"


def test_match_data_to_states_full():
    """Verify 100% match rate with official sample dataset."""
    data = load_sample_dataset("literacy")
    matched, unmatched, missing = match_data_to_states(data)
    assert len(matched) == 36
    assert len(unmatched) == 0
    assert len(missing) == 0


def test_match_data_with_unmatched_and_missing():
    """Verify detection of unmatched and missing entries."""
    partial_data = [
        {"state": "Maharashtra", "value": 82.3},
        {"state": "Karnataka", "value": 75.4},
        {"state": "Narnia", "value": 99.9},  # Unmatched
    ]
    matched, unmatched, missing = match_data_to_states(partial_data)
    assert "Maharashtra" in matched
    assert "Karnataka" in matched
    assert "Narnia" in unmatched
    assert len(missing) == 34


def test_generate_choropleth():
    """Verify complete choropleth generation, legend intervals, and color assignment."""
    data = load_sample_dataset("forest_cover")
    res = generate_choropleth(data, palette="Greens", num_classes=5)

    assert res.matched_count == 36
    assert len(res.legend_bins) == 5
    assert res.min_value >= 0.0
    assert res.max_value <= 100.0

    # Ensure every state received a valid hex color
    for canonical in STATE_ISO_CODES.keys():
        col = res.state_colors[canonical]
        assert col.startswith("#")
        assert len(col) == 7


def test_empty_data_choropleth():
    """Verify fallback behavior when data is empty."""
    res = generate_choropleth([])
    assert res.matched_count == 0
    assert len(res.legend_bins) == 0
    for col in res.state_colors.values():
        assert col == "#e2e8f0"  # default no-data color


def test_invalid_input_type():
    """Verify exception on invalid data types."""
    with pytest.raises(DataValidationError):
        match_data_to_states("not a list")
