"""High-resolution publication cartographic rendering engine for Equal Earth maps.

Supports:
  - India State & UT administrative and thematic maps
  - Global Equal Earth maps centered on India (78°E), Prime Meridian (0°), or custom meridians
  - Publication-ready exports: 300+ DPI PNG, lossless vector SVG, and vector PDF.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".mpl_cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
import cartopy.crs as ccrs
from shapely.geometry import shape

from equal_earth.data import load_india_states, load_world_data, validate_and_repair_geometry
from equal_earth.styling import MapTheme, get_theme
from equal_earth.thematic import ChoroplethResult
from equal_earth.exceptions import RenderError, ExportError


def render_india_map(
    states_data: Optional[Dict[str, Any]] = None,
    theme: Union[str, MapTheme] = "atlas_light",
    choropleth: Optional[ChoroplethResult] = None,
    show_labels: bool = True,
    highlight_state: Optional[str] = None,
    title: str = "India — Administrative Boundaries & States",
    subtitle: Optional[str] = "Equal Earth Projection · Survey of India Sovereign Boundary",
    source_note: str = "Source: Survey of India Official Administrative Delineations",
    figsize: Tuple[float, float] = (10.0, 11.5),
    dpi: int = 300,
    output_path: Optional[Union[str, Path]] = None,
    legend_title: Optional[str] = None,
    unit: str = ""
) -> Path:
    """Render a publication-grade India map in the Equal Earth projection.

    Parameters
    ----------
    states_data : Dict[str, Any], optional
        States GeoJSON FeatureCollection, loaded automatically if None.
    theme : Union[str, MapTheme], optional
        MapTheme object or name ('atlas_light', 'academic_clean', 'carto_dark', etc.).
    choropleth : ChoroplethResult, optional
        Choropleth classification result for data-driven state coloring.
    show_labels : bool, optional
        Whether to draw state names at centroids, by default True.
    highlight_state : str, optional
        Canonical name of specific state/UT to highlight in accent color.
    title : str, optional
        Main map title.
    subtitle : str, optional
        Secondary subtitle.
    source_note : str, optional
        Attribution text displayed at the bottom of the map.
    figsize : Tuple[float, float], optional
        Figure dimensions (width, height) in inches, by default (10.0, 11.5).
    dpi : int, optional
        Resolution for raster outputs, by default 300.
    output_path : str or Path, optional
        Path to save output (format inferred from .png, .svg, or .pdf).
    legend_title : str, optional
        Title for the choropleth legend.
    unit : str, optional
        Measurement unit suffix for legend labels.

    Returns
    -------
    Path
        Absolute path to the rendered map file.

    Raises
    ------
    RenderError, ExportError
        If rendering or file saving fails.
    """
    map_theme = get_theme(theme) if isinstance(theme, str) else theme

    if states_data is None:
        states_data = load_india_states()

    # Projection centered on India's median longitude (78.0°E)
    proj = ccrs.EqualEarth(central_longitude=78.0)
    data_crs = ccrs.PlateCarree()

    fig = plt.figure(figsize=figsize, facecolor=map_theme.bg, dpi=dpi)
    ax = fig.add_axes([0.05, 0.08, 0.90, 0.82], projection=proj)
    ax.set_facecolor(map_theme.ocean)

    # India geographical bounding box with safe padding
    # Lon: 68.0°E to 98.0°E, Lat: 6.5°N to 37.5°N
    ax.set_extent([67.0, 98.5, 6.0, 37.8], crs=data_crs)

    # 1. Draw each State and Union Territory
    for feat in states_data.get("features", []):
        props = feat.get("properties", {})
        name = props.get("st_nm", "")
        geom = shape(feat.get("geometry"))

        # Determine fill color
        if highlight_state and name.lower() == highlight_state.lower():
            fill_color = map_theme.state_highlight_fill
            edge_color = map_theme.state_highlight_edge
            line_width = 1.4
        elif choropleth and name in choropleth.state_colors:
            fill_color = choropleth.state_colors[name]
            edge_color = map_theme.state_edge
            line_width = 0.6
        else:
            fill_color = map_theme.state_fill
            edge_color = map_theme.state_edge
            line_width = 0.6

        ax.add_geometries(
            [geom],
            crs=data_crs,
            facecolor=fill_color,
            edgecolor=edge_color,
            linewidth=line_width,
            zorder=2
        )

        # 2. Draw State Labels
        if show_labels and name:
            centroid = props.get("centroid")
            if centroid:
                # Selective font size based on territory size
                is_small_ut = name in ["Chandigarh", "Delhi", "Puducherry", "Goa", "Lakshadweep", "Dadra and Nagar Haveli and Daman and Diu"]
                f_size = 6.0 if is_small_ut else 7.5
                f_weight = "bold" if not is_small_ut else "normal"

                ax.text(
                    centroid[0], centroid[1], name,
                    transform=data_crs,
                    fontsize=f_size,
                    fontweight=f_weight,
                    color=map_theme.text,
                    ha="center", va="center",
                    zorder=4,
                    bbox=dict(
                        boxstyle="round,pad=0.15",
                        facecolor=map_theme.bg,
                        alpha=0.75,
                        edgecolor="none"
                    )
                )

    # 3. Outer Sovereign Boundary Highlight
    # Draw an enhanced outline for the complete Indian exterior boundary
    try:
        from shapely.ops import unary_union
        all_geoms = [shape(f["geometry"]) for f in states_data["features"]]
        india_outer = unary_union(all_geoms)
        ax.add_geometries(
            [india_outer],
            crs=data_crs,
            facecolor="none",
            edgecolor=map_theme.india_edge,
            linewidth=1.2,
            zorder=3
        )
    except Exception:
        pass

    # 4. Graticules
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color=map_theme.graticule, alpha=0.7, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 8, "color": map_theme.ocean_text}
    gl.ylabel_style = {"size": 8, "color": map_theme.ocean_text}

    # 5. Titles
    title_text = title
    if subtitle:
        title_text += f"\n{subtitle}"
    fig.text(0.08, 0.94, title, fontsize=14, fontweight="bold", color=map_theme.text, ha="left")
    if subtitle:
        fig.text(0.08, 0.915, subtitle, fontsize=9.5, color=map_theme.ocean_text, ha="left")

    # Source & Disclaimer
    fig.text(0.08, 0.03, source_note, fontsize=7.5, color="#64748b", ha="left")

    # 6. Choropleth Legend (if applicable)
    if choropleth and choropleth.legend_bins:
        legend_patches = []
        for b in choropleth.legend_bins:
            label_text = f"{b.label} {unit}".strip()
            patch = mpatches.Patch(facecolor=b.color, edgecolor="#64748b", linewidth=0.5, label=label_text)
            legend_patches.append(patch)

        leg = ax.legend(
            handles=legend_patches,
            loc="lower left",
            frameon=True,
            facecolor=map_theme.bg,
            edgecolor=map_theme.graticule,
            framealpha=0.9,
            title=legend_title or "Legend",
            fontsize=8,
            title_fontsize=8.5
        )
        leg.get_title().set_fontweight("bold")
        leg.get_title().set_color(map_theme.text)
        for t in leg.get_texts():
            t.set_color(map_theme.text)

    # 7. Output saving
    if not output_path:
        output_path = Path.cwd() / "india_equal_earth.png"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor=map_theme.bg)
    except Exception as e:
        plt.close(fig)
        raise ExportError(f"Failed to export map to {output_path}: {e}") from e

    plt.close(fig)
    return output_path


def render_global_map(
    world_data: Optional[Dict[str, Any]] = None,
    central_longitude: float = 78.0,
    theme: Union[str, MapTheme] = "atlas_light",
    highlight_country: Optional[str] = None,
    show_labels: bool = True,
    title: str = "Equal Earth World Map",
    subtitle: Optional[str] = "Survey of India Sovereign Boundaries",
    figsize: Tuple[float, float] = (15.0, 7.5),
    dpi: int = 300,
    output_path: Optional[Union[str, Path]] = None
) -> Path:
    """Render an authoritative global Equal Earth world map.

    Parameters
    ----------
    world_data : Dict[str, Any], optional
        World GeoJSON data, loaded automatically if None.
    central_longitude : float, optional
        Central meridian in degrees, by default 78.0 (centered on India).
    theme : Union[str, MapTheme], optional
        Theme configuration.
    highlight_country : str, optional
        Name of country to highlight (e.g. 'India').
    show_labels : bool, optional
        Whether country labels are drawn.
    title : str, optional
        Main title.
    subtitle : str, optional
        Subtitle.
    figsize : Tuple[float, float], optional
        Figure size in inches, by default (15.0, 7.5).
    dpi : int, optional
        Resolution for raster outputs, by default 300.
    output_path : str or Path, optional
        Output file path.

    Returns
    -------
    Path
        Absolute path to generated map.
    """
    map_theme = get_theme(theme) if isinstance(theme, str) else theme

    if world_data is None:
        world_data = load_world_data()

    proj = ccrs.EqualEarth(central_longitude=central_longitude)
    data_crs = ccrs.PlateCarree()

    fig = plt.figure(figsize=figsize, facecolor=map_theme.bg, dpi=dpi)
    ax = fig.add_axes([0.03, 0.05, 0.94, 0.88], projection=proj)
    ax.set_facecolor(map_theme.ocean)

    # 1. Countries
    for feat in world_data.get("features", []):
        props = feat.get("properties", {})
        name = props.get("name", "")
        geom = shape(feat.get("geometry"))

        is_target = highlight_country and name.lower() == highlight_country.lower()
        if is_target:
            fill_color = map_theme.state_highlight_fill
            edge_color = map_theme.state_highlight_edge
            line_width = 1.0
        elif name.lower() == "india":
            fill_color = map_theme.india_fill
            edge_color = map_theme.india_edge
            line_width = 0.8
        else:
            fill_color = map_theme.land
            edge_color = map_theme.land_edge
            line_width = 0.4

        ax.add_geometries([geom], crs=data_crs, facecolor=fill_color, edgecolor=edge_color, linewidth=line_width, zorder=2)

        if show_labels and name and not props.get("is_micronation", False):
            centroid = props.get("centroid")
            if centroid and (is_target or name == "India"):
                ax.text(
                    centroid[0], centroid[1], name,
                    transform=data_crs,
                    fontsize=8.5, fontweight="bold",
                    color=map_theme.text, ha="center", va="center",
                    bbox=dict(boxstyle="square,pad=0.15", facecolor=map_theme.bg, alpha=0.8, edgecolor="none")
                )

    # 2. Dashed Disputed Borders (Google Maps style)
    for dashed in world_data.get("dashed_borders", []):
        try:
            line_geom = shape(dashed.get("geometry"))
            ax.add_geometries([line_geom], crs=data_crs, facecolor="none", edgecolor=map_theme.disputed_edge, linewidth=0.75, linestyle="--", zorder=3)
        except Exception:
            pass

    # 3. Graticule
    gl = ax.gridlines(draw_labels=True, linewidth=0.4, color=map_theme.graticule, alpha=0.7, linestyle="--")
    gl.xlabel_style = {"size": 7.5, "color": map_theme.ocean_text}
    gl.ylabel_style = {"size": 7.5, "color": map_theme.ocean_text}

    # 4. Title
    title_suffix = f" · Centered at Lon {central_longitude:+.1f}°"
    full_title = f"{title}{title_suffix}"
    if subtitle:
        full_title += f"\n({subtitle})"
    ax.set_title(full_title, fontsize=11.5, fontweight="bold", color=map_theme.text, pad=12)

    if not output_path:
        output_path = Path.cwd() / f"equal_earth_lon_{int(central_longitude)}.png"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor=map_theme.bg)
    except Exception as e:
        plt.close(fig)
        raise ExportError(f"Failed to export map to {output_path}: {e}") from e

    plt.close(fig)
    return output_path
