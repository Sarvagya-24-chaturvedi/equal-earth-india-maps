"""Tests for Equal Earth projection mathematics, reference benchmarks, and inverse convergence."""

import math
import pytest
from equal_earth.projection import (
    forward,
    inverse,
    verify_equal_area_preservation,
    get_cartopy_crs,
    REFERENCE_BENCHMARKS,
    DEFAULT_RADIUS,
)
from equal_earth.exceptions import ProjectionError


def test_reference_benchmarks_forward():
    """Verify forward projection matches authoritative PROJ 9 benchmarks to millimeter precision."""
    for (lon, lat), (exp_x, exp_y) in REFERENCE_BENCHMARKS.items():
        calc_x, calc_y = forward(lon, lat, lon_0_deg=0.0)
        assert abs(calc_x - exp_x) < 0.01, f"Forward X failed at ({lon}, {lat}): {calc_x} vs {exp_x}"
        assert abs(calc_y - exp_y) < 0.01, f"Forward Y failed at ({lon}, {lat}): {calc_y} vs {exp_y}"


def test_roundtrip_forward_inverse():
    """Verify forward -> inverse coordinate roundtrip across diverse global coordinates."""
    test_points = [
        (0.0, 0.0),
        (78.0, 20.0),       # Central India
        (77.2090, 28.6139), # New Delhi
        (88.3639, 22.5726), # Kolkata
        (72.8777, 19.0760), # Mumbai
        (80.2707, 13.0827), # Chennai
        (-74.006, 40.7128), # New York
        (139.6917, 35.6895),# Tokyo
        (151.2093, -33.8688),# Sydney
        (-43.1729, -22.9068),# Rio de Janeiro
        (0.0, 89.9),        # Near North Pole
        (0.0, -89.9),       # Near South Pole
    ]

    for lon, lat in test_points:
        x, y = forward(lon, lat, lon_0_deg=78.0)
        inv_lon, inv_lat = inverse(x, y, lon_0_deg=78.0)
        lon_diff = abs((inv_lon - lon + 180.0) % 360.0 - 180.0)
        lat_diff = abs(inv_lat - lat)
        assert lon_diff < 1e-4, f"Longitude roundtrip failed for ({lon}, {lat}): {inv_lon}"
        assert lat_diff < 1e-4, f"Latitude roundtrip failed for ({lon}, {lat}): {inv_lat}"


def test_equal_area_preservation():
    """Verify that the areal distortion factor s_A equals 1.0 (true equal-area)."""
    sample_coords = [
        (0.0, 0.0),
        (78.0, 20.0),
        (45.0, 60.0),
        (-100.0, -45.0),
        (120.0, 10.0),
    ]
    for lon, lat in sample_coords:
        s_a = verify_equal_area_preservation(lon, lat)
        assert abs(s_a - 1.0) < 0.002, f"Areal scale not equal to 1.0 at ({lon}, {lat}): {s_a}"


def test_invalid_coordinates():
    """Verify that ProjectionError is raised for out-of-bounds coordinates."""
    with pytest.raises(ProjectionError):
        forward(0.0, 95.0)  # Latitude > 90

    with pytest.raises(ProjectionError):
        forward(0.0, -95.0) # Latitude < -90

    with pytest.raises(ProjectionError):
        forward("invalid", 20.0)

    with pytest.raises(ProjectionError):
        inverse(1e9, 1e9)   # Beyond Earth bounds


def test_central_meridian_shift():
    """Verify that shifting central meridian translates X coordinate linearly."""
    x0, y0 = forward(78.0, 20.0, lon_0_deg=0.0)
    x1, y1 = forward(78.0, 20.0, lon_0_deg=78.0)
    assert abs(x1) < 1e-6, "Point on central meridian must have X=0"
    assert abs(y0 - y1) < 1e-6, "Y coordinate is independent of central meridian"


def test_cartopy_crs_creation():
    """Verify Cartopy CRS wrapper creation."""
    crs = get_cartopy_crs(central_longitude=78.0)
    assert crs is not None
    assert hasattr(crs, "proj4_params") or hasattr(crs, "to_proj4")
