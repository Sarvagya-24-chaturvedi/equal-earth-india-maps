"""Cartographic themes, color palettes, and typography styling for Equal Earth maps."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class MapTheme:
    """Configuration class for map styling and color hierarchy."""
    name: str = "Classic Atlas"
    ocean: str = "#d8ecf8"
    land: str = "#ffffff"
    land_edge: str = "#94a3b8"
    india_fill: str = "#fef3c7"
    india_edge: str = "#d97706"
    state_fill: str = "#ffffff"
    state_edge: str = "#cbd5e1"
    state_highlight_fill: str = "#fed7aa"
    state_highlight_edge: str = "#ea580c"
    graticule: str = "#c8deec"
    text: str = "#0f172a"
    ocean_text: str = "#3f7893"
    bg: str = "#ffffff"
    disputed_edge: str = "#94a3b8"

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "ocean": self.ocean,
            "land": self.land,
            "land_edge": self.land_edge,
            "india_fill": self.india_fill,
            "india_edge": self.india_edge,
            "state_fill": self.state_fill,
            "state_edge": self.state_edge,
            "state_highlight_fill": self.state_highlight_fill,
            "state_highlight_edge": self.state_highlight_edge,
            "graticule": self.graticule,
            "text": self.text,
            "ocean_text": self.ocean_text,
            "bg": self.bg,
            "disputed_edge": self.disputed_edge,
        }


THEMES: Dict[str, MapTheme] = {
    "atlas_light": MapTheme(
        name="Classic Atlas (Light)",
        ocean="#d8ecf8",
        land="#ffffff",
        land_edge="#94a3b8",
        india_fill="#fef3c7",
        india_edge="#d97706",
        state_fill="#f8fafc",
        state_edge="#cbd5e1",
        state_highlight_fill="#fde68a",
        state_highlight_edge="#b45309",
        graticule="#c8deec",
        text="#0f172a",
        ocean_text="#3f7893",
        bg="#ffffff",
        disputed_edge="#94a3b8"
    ),
    "academic_clean": MapTheme(
        name="Academic Publication (Clean)",
        ocean="#f8fafc",
        land="#ffffff",
        land_edge="#475569",
        india_fill="#ffedd5",
        india_edge="#c2410c",
        state_fill="#ffffff",
        state_edge="#64748b",
        state_highlight_fill="#fed7aa",
        state_highlight_edge="#9a3412",
        graticule="#e2e8f0",
        text="#0f172a",
        ocean_text="#64748b",
        bg="#ffffff",
        disputed_edge="#64748b"
    ),
    "carto_dark": MapTheme(
        name="Cartographic Dark",
        ocean="#090d16",
        land="#1e293b",
        land_edge="#334155",
        india_fill="#3b2507",
        india_edge="#f59e0b",
        state_fill="#1e293b",
        state_edge="#475569",
        state_highlight_fill="#78350f",
        state_highlight_edge="#fbbf24",
        graticule="#1e293b",
        text="#f8fafc",
        ocean_text="#38bdf8",
        bg="#090d16",
        disputed_edge="#64748b"
    ),
    "emerald_nature": MapTheme(
        name="Emerald Conservation",
        ocean="#e0f2fe",
        land="#f0fdf4",
        land_edge="#86efac",
        india_fill="#dcfce7",
        india_edge="#16a34a",
        state_fill="#f0fdf4",
        state_edge="#bbf7d0",
        state_highlight_fill="#bbf7d0",
        state_highlight_edge="#15803d",
        graticule="#bae6fd",
        text="#064e3b",
        ocean_text="#0284c7",
        bg="#ffffff",
        disputed_edge="#86efac"
    ),
    "sunset_warm": MapTheme(
        name="Warm Sunset Terracotta",
        ocean="#e0f2fe",
        land="#fffbeb",
        land_edge="#fde68a",
        india_fill="#ffedd5",
        india_edge="#ea580c",
        state_fill="#fffbeb",
        state_edge="#fed7aa",
        state_highlight_fill="#fdba74",
        state_highlight_edge="#c2410c",
        graticule="#cbd5e1",
        text="#451a03",
        ocean_text="#0369a1",
        bg="#ffffff",
        disputed_edge="#fb923c"
    )
}

# Standard sequential & diverging palettes for thematic choropleth maps
COLOR_PALETTES: Dict[str, List[str]] = {
    "YlGnBu": ["#ffffd9", "#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8", "#253494", "#081d58"],
    "Viridis": ["#440154", "#482878", "#3e4a89", "#31688e", "#26828e", "#1f9e89", "#35b779", "#6ece58", "#b5de2b", "#fde725"],
    "Blues": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"],
    "Greens": ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#006d2c", "#00441b"],
    "Oranges": ["#fff5eb", "#fee6ce", "#fdd0a2", "#fdae6b", "#fd8d3c", "#f16913", "#d94801", "#a63603", "#7f2704"],
    "Purples": ["#fcfbfd", "#efedf5", "#dadaeb", "#bcbddc", "#9e9ac8", "#807dba", "#6a51a3", "#54278f", "#3f007d"],
    "Spectral": ["#9e0142", "#d53e4f", "#f46d43", "#fdae61", "#fee08b", "#ffffbf", "#e6f598", "#abdda4", "#66c2a5", "#3288bd", "#5e4fa2"],
    "RdYlGn": ["#a50026", "#d73027", "#f46d43", "#fdae61", "#fee08b", "#ffffbf", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850", "#006837"]
}


def get_theme(name: str) -> MapTheme:
    """Retrieve theme by name or return default 'atlas_light'."""
    key = name.strip().lower()
    return THEMES.get(key, THEMES["atlas_light"])
