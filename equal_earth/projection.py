"""Equal Earth Map Projection Mathematical Engine.

Authoritative Implementation based on:
    Šavrič, B., Jenny, B., & Patterson, T. (2019).
    A polynomial equation for the Equal Earth map projection.
    International Journal of Geographical Information Science, 33(3), 454-465.
    DOI: 10.1080/13658816.2018.1504949
"""

import math
from typing import Tuple, List, Dict, Any, Union
from equal_earth.exceptions import ProjectionError

# Exact polynomial coefficients from Šavrič, Jenny, Patterson (2019)
A1: float = 1.340264
A2: float = -0.081106
A3: float = 0.000893
A4: float = 0.003796
SQRT3: float = math.sqrt(3.0)

# WGS84 authalic / mean Earth radius in meters
DEFAULT_RADIUS: float = 6378137.0

# Authoritative benchmark test points (lon, lat) -> (x, y) with lon_0=0, R=6378137
# Verified against PROJ 9.x libproj reference output
REFERENCE_BENCHMARKS: Dict[Tuple[float, float], Tuple[float, float]] = {
    (0.0, 0.0): (0.0, 0.0),
    (78.0, 20.0): (7264273.592, 2556518.151),
    (90.0, 45.0): (7397710.895, 5486671.715),
    (-120.0, -30.0): (-10765026.754, -3781821.427),
    (180.0, 0.0): (17263256.844, 0.0),
    (0.0, 90.0): (0.0, 8402320.157),
}


def forward(
    lon_deg: float,
    lat_deg: float,
    lon_0_deg: float = 0.0,
    radius: float = DEFAULT_RADIUS
) -> Tuple[float, float]:
    """Calculate forward projection from geographic coordinates (WGS84 lon, lat in degrees)
    to projected Equal Earth planar coordinates (x, y in meters).

    Parameters
    ----------
    lon_deg : float
        Longitude in degrees [-180, 180] (or wrapped equivalent).
    lat_deg : float
        Latitude in degrees [-90, 90].
    lon_0_deg : float, optional
        Central meridian in degrees, by default 0.0.
    radius : float, optional
        Spherical radius of the Earth, by default 6378137.0 m.

    Returns
    -------
    Tuple[float, float]
        Projected coordinates (x, y) in meters.

    Raises
    ------
    ProjectionError
        If coordinates are out of physical bounds.
    """
    if not isinstance(lon_deg, (int, float)) or not isinstance(lat_deg, (int, float)):
        raise ProjectionError(f"Coordinates must be numeric, got lon={lon_deg!r}, lat={lat_deg!r}")

    if not (-90.0 <= lat_deg <= 90.0):
        raise ProjectionError(f"Latitude must be between -90 and +90 degrees, got {lat_deg}")

    # Standardize longitude difference preserving boundary signs
    dlon = lon_deg - lon_0_deg
    while dlon > 180.0:
        dlon -= 360.0
    while dlon < -180.0:
        dlon += 360.0
    lam = math.radians(dlon)
    phi = math.radians(lat_deg)

    # Parametric latitude theta: sin(theta) = (sqrt(3)/2) * sin(phi)
    sin_theta = (SQRT3 / 2.0) * math.sin(phi)
    sin_theta = max(-1.0, min(1.0, sin_theta))
    theta = math.asin(sin_theta)

    theta2 = theta * theta
    theta6 = theta2 * theta2 * theta2

    # Denominator for x
    denom = 3.0 * (9.0 * A4 * theta6 * theta2 + 7.0 * A3 * theta6 + 3.0 * A2 * theta2 + A1)

    x = radius * (2.0 * SQRT3 * lam * math.cos(theta)) / denom
    y = radius * (A4 * theta6 * theta2 * theta + A3 * theta6 * theta + A2 * theta2 * theta + A1 * theta)

    return (x, y)


def inverse(
    x: float,
    y: float,
    lon_0_deg: float = 0.0,
    radius: float = DEFAULT_RADIUS,
    tolerance: float = 1e-11,
    max_iter: int = 15
) -> Tuple[float, float]:
    """Calculate inverse projection from Equal Earth planar coordinates (x, y in meters)
    to geographic coordinates (lon, lat in degrees).

    Uses Newton-Raphson iteration on the y(theta) polynomial to solve for theta,
    then evaluates latitude phi and longitude lambda analytically.

    Parameters
    ----------
    x : float
        Projected x coordinate in meters.
    y : float
        Projected y coordinate in meters.
    lon_0_deg : float, optional
        Central meridian in degrees, by default 0.0.
    radius : float, optional
        Spherical radius of the Earth, by default 6378137.0 m.
    tolerance : float, optional
        Convergence tolerance for Newton-Raphson, by default 1e-11.
    max_iter : int, optional
        Maximum iterations, by default 15.

    Returns
    -------
    Tuple[float, float]
        Geographic coordinates (lon_deg, lat_deg).

    Raises
    ------
    ProjectionError
        If coordinates cannot be inverted or exceed Earth projection bounds.
    """
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ProjectionError(f"Planar coordinates must be numeric, got x={x!r}, y={y!r}")

    y_norm = y / radius
    y_max = A4 * (math.pi/3)**9 + A3 * (math.pi/3)**7 + A2 * (math.pi/3)**3 + A1 * (math.pi/3)
    if abs(y_norm) > y_max * 1.0001:
        raise ProjectionError(f"Y coordinate {y} m exceeds polar limit ({y_max * radius:.1f} m)")

    # Newton-Raphson for theta: f(theta) = y_norm - (A4*theta^9 + A3*theta^7 + A2*theta^3 + A1*theta) = 0
    # Initial estimate
    theta = y_norm / A1
    for _ in range(max_iter):
        theta2 = theta * theta
        theta6 = theta2 * theta2 * theta2
        f = (A4 * theta6 * theta2 * theta + A3 * theta6 * theta + A2 * theta2 * theta + A1 * theta) - y_norm
        f_prime = 9.0 * A4 * theta6 * theta2 + 7.0 * A3 * theta6 + 3.0 * A2 * theta2 + A1
        if abs(f_prime) < 1e-12:
            break
        delta = f / f_prime
        theta -= delta
        if abs(delta) < tolerance:
            break
    else:
        # If loop completes without break, check convergence
        if abs(f) > 1e-6:
            raise ProjectionError(f"Newton-Raphson failed to converge for y={y}")

    # Solve for phi: sin(phi) = (2 / sqrt(3)) * sin(theta)
    sin_phi = (2.0 / SQRT3) * math.sin(theta)
    sin_phi = max(-1.0, min(1.0, sin_phi))
    phi = math.asin(sin_phi)

    # Solve for lambda: lam = x * denom / (2 * sqrt(3) * radius * cos(theta))
    theta2 = theta * theta
    theta6 = theta2 * theta2 * theta2
    denom = 3.0 * (9.0 * A4 * theta6 * theta2 + 7.0 * A3 * theta6 + 3.0 * A2 * theta2 + A1)
    cos_theta = math.cos(theta)
    if abs(cos_theta) < 1e-12:
        lam = 0.0
    else:
        lam = (x / radius) * denom / (2.0 * SQRT3 * cos_theta)

    lon_deg = math.degrees(lam) + lon_0_deg
    lat_deg = math.degrees(phi)

    # Wrap lon to [-180, 180]
    lon_deg = ((lon_deg + 180.0) % 360.0) - 180.0
    return (lon_deg, lat_deg)


def verify_equal_area_preservation(
    lon_deg: float,
    lat_deg: float,
    delta_deg: float = 0.01,
    radius: float = DEFAULT_RADIUS
) -> float:
    """Compute local areal scale factor s_A at (lon, lat) using finite differences.
    An authentic equal-area projection must yield s_A == 1.0 everywhere.

    Parameters
    ----------
    lon_deg : float
        Center test longitude.
    lat_deg : float
        Center test latitude.
    delta_deg : float, optional
        Step size in degrees for numerical Jacobian, by default 0.01.
    radius : float, optional
        Radius in meters, by default DEFAULT_RADIUS.

    Returns
    -------
    float
        Areal scale factor s_A (should be 1.0 within numerical precision).
    """
    # Avoid antimeridian wrap and polar singularity for finite difference test patch
    if abs(lat_deg) > 85.0:
        lat_deg = math.copysign(80.0, lat_deg)
    if abs(lon_deg) > 179.0:
        lon_deg = math.copysign(175.0, lon_deg)

    dlon = math.radians(delta_deg)
    dlat = math.radians(delta_deg)

    # Spherical patch area
    phi1 = math.radians(lat_deg - delta_deg / 2.0)
    phi2 = math.radians(lat_deg + delta_deg / 2.0)
    sphere_area = (radius ** 2) * dlon * (math.sin(phi2) - math.sin(phi1))

    # Planar mapped polygon: 4 corners
    p_bl = forward(lon_deg - delta_deg / 2.0, lat_deg - delta_deg / 2.0, radius=radius)
    p_br = forward(lon_deg + delta_deg / 2.0, lat_deg - delta_deg / 2.0, radius=radius)
    p_tr = forward(lon_deg + delta_deg / 2.0, lat_deg + delta_deg / 2.0, radius=radius)
    p_tl = forward(lon_deg - delta_deg / 2.0, lat_deg + delta_deg / 2.0, radius=radius)

    # Shoelace formula for polygon area
    pts = [p_bl, p_br, p_tr, p_tl]
    n = len(pts)
    planar_area = 0.5 * abs(sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)))

    if sphere_area <= 0:
        return 1.0
    return planar_area / sphere_area


def get_cartopy_crs(central_longitude: float = 78.0):
    """Instantiate a Cartopy EqualEarth projection object with the specified central meridian.

    Parameters
    ----------
    central_longitude : float, optional
        Central meridian in degrees, by default 78.0 (centered on India).

    Returns
    -------
    cartopy.crs.EqualEarth
        Configured Cartopy Coordinate Reference System.
    """
    try:
        import cartopy.crs as ccrs
        return ccrs.EqualEarth(central_longitude=central_longitude)
    except ImportError as e:
        raise ProjectionError("Cartopy is not installed or unavailable in the environment.") from e
