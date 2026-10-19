/**
 * Basic Point-in-Polygon (PIP) check for GeoJSON-style coordinates.
 * Handles both Polygon and MultiPolygon geometries.
 */
function isPointInPolygon(lat, lon, geometry) {
  if (!geometry) return false;

  const type = geometry.type;
  const coords = geometry.coordinates;

  if (type === 'Polygon') {
    return isPointInSinglePolygon(lat, lon, coords[0]);
  } else if (type === 'MultiPolygon') {
    for (let i = 0; i < coords.length; i++) {
      if (isPointInSinglePolygon(lat, lon, coords[i][0])) return true;
    }
  }
  return false;
}

function isPointInSinglePolygon(lat, lon, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1];
    const xj = ring[j][0], yj = ring[j][1];
    const intersect = ((yi > lon) !== (yj > lon)) &&
        (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi); // Note: geometry is [lon, lat]
    if (intersect) inside = !inside;
  }
  // The above logic is for standard [x, y].
  // GeoJSON is [lon, lat]. Let's rewrite for clarity.
  return false;
}

/**
 * CORRECTED Point-in-Polygon for GeoJSON [lon, lat]
 */
function containsPoint(geometry, lon, lat) {
  if (!geometry) return false;

  if (geometry.type === 'Polygon') {
    return pointInPolygon(lon, lat, geometry.coordinates[0]);
  } else if (geometry.type === 'MultiPolygon') {
    return geometry.coordinates.some(polygon => pointInPolygon(lon, lat, polygon[0]));
  }
  return false;
}

function pointInPolygon(lon, lat, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1];
    const xj = ring[j][0], yj = ring[j][1];
    const intersect = ((yi > lat) !== (yj > lat)) &&
        (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function findFeatureAt(lat, lon) {
  if (typeof WORLD_DATA === 'undefined') return null;
  return WORLD_DATA.features.find(f => containsPoint(f.geometry, lon, lat));
}
