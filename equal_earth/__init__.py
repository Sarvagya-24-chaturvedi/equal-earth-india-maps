"""Equal Earth India Maps Toolkit.

An authoritative, publication-quality geospatial toolkit and interactive mapping engine
for India and the world using the Equal Earth projection and Survey of India official sovereign boundaries.
"""

__version__ = "1.0.0"
__author__ = "Sarvagya Chaturvedi"
__license__ = "MIT"

from equal_earth.exceptions import (
    EqualEarthError,
    ProjectionError,
    DataValidationError,
    RenderError,
    ExportError,
)
from equal_earth.projection import (
    forward,
    inverse,
    verify_equal_area_preservation,
    get_cartopy_crs,
    REFERENCE_BENCHMARKS,
)
from equal_earth.data import (
    load_india_states,
    load_world_data,
    load_sample_dataset,
    normalize_state_name,
    find_entity,
    STATE_ISO_CODES,
    STATE_NAME_ALIASES,
)
from equal_earth.styling import (
    MapTheme,
    get_theme,
    THEMES,
    COLOR_PALETTES,
)
from equal_earth.thematic import (
    match_data_to_states,
    generate_choropleth,
    ChoroplethResult,
    LegendBin,
)
from equal_earth.renderer import (
    render_india_map,
    render_global_map,
)

__all__ = [
    "forward",
    "inverse",
    "verify_equal_area_preservation",
    "get_cartopy_crs",
    "REFERENCE_BENCHMARKS",
    "load_india_states",
    "load_world_data",
    "load_sample_dataset",
    "normalize_state_name",
    "find_entity",
    "STATE_ISO_CODES",
    "STATE_NAME_ALIASES",
    "MapTheme",
    "get_theme",
    "THEMES",
    "COLOR_PALETTES",
    "match_data_to_states",
    "generate_choropleth",
    "ChoroplethResult",
    "LegendBin",
    "render_india_map",
    "render_global_map",
    "EqualEarthError",
    "ProjectionError",
    "DataValidationError",
    "RenderError",
    "ExportError",
]
