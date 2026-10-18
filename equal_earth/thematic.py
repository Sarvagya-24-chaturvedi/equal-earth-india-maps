"""Thematic mapping engine for data-driven choropleths across Indian states and union territories."""

import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Union

from equal_earth.data import normalize_state_name, STATE_ISO_CODES
from equal_earth.styling import COLOR_PALETTES
from equal_earth.exceptions import DataValidationError


@dataclass
class LegendBin:
    label: str
    color: str
    min_val: float
    max_val: float


@dataclass
class ChoroplethResult:
    state_colors: Dict[str, str]
    state_values: Dict[str, Optional[float]]
    legend_bins: List[LegendBin]
    min_value: float
    max_value: float
    matched_count: int
    unmatched_keys: List[str]
    missing_regions: List[str]


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def interpolate_color(color_a: str, color_b: str, t: float) -> str:
    """Linearly interpolate between two hex colors by factor t in [0, 1]."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = hex_to_rgb(color_a)
    r2, g2, b2 = hex_to_rgb(color_b)
    r = int(round(r1 + (r2 - r1) * t))
    g = int(round(g1 + (g2 - g1) * t))
    b = int(round(b1 + (b2 - b1) * t))
    return rgb_to_hex((r, g, b))


def match_data_to_states(
    data_records: List[Dict[str, Any]],
    state_key: str = "state",
    value_key: str = "value"
) -> Tuple[Dict[str, float], List[str], List[str]]:
    """Match external tabular records to canonical 36 Indian states and union territories.

    Parameters
    ----------
    data_records : List[Dict[str, Any]]
        List of data rows (e.g. from CSV or API).
    state_key : str, optional
        Name of state column, by default "state".
    value_key : str, optional
        Name of numeric value column, by default "value".

    Returns
    -------
    Tuple[Dict[str, float], List[str], List[str]]
        (matched_dict, unmatched_input_keys, missing_region_keys)
    """
    if not isinstance(data_records, list):
        raise DataValidationError("data_records must be a list of dictionaries.")

    matched: Dict[str, float] = {}
    unmatched_keys: List[str] = []

    for row in data_records:
        raw_state = str(row.get(state_key, "")).strip()
        val_raw = row.get(value_key)
        if not raw_state:
            continue

        canonical = normalize_state_name(raw_state)
        if canonical in STATE_ISO_CODES:
            try:
                numeric_val = float(val_raw) if val_raw is not None else float("nan")
            except (ValueError, TypeError):
                numeric_val = float("nan")
            matched[canonical] = numeric_val
        else:
            unmatched_keys.append(raw_state)

    missing_regions = [canonical for canonical in STATE_ISO_CODES.keys() if canonical not in matched]
    return matched, unmatched_keys, missing_regions


def generate_choropleth(
    data_records: List[Dict[str, Any]],
    state_key: str = "state",
    value_key: str = "value",
    palette: str = "YlGnBu",
    num_classes: int = 5,
    no_data_color: str = "#e2e8f0"
) -> ChoroplethResult:
    """Generate state fill colors and legend intervals for a data-driven choropleth map.

    Parameters
    ----------
    data_records : List[Dict[str, Any]]
        Tabular data records.
    state_key : str, optional
        Column name for states, by default "state".
    value_key : str, optional
        Column name for numeric values, by default "value".
    palette : str, optional
        Color palette name, by default "YlGnBu".
    num_classes : int, optional
        Number of classification bins, by default 5.
    no_data_color : str, optional
        Color for regions without data, by default "#e2e8f0".

    Returns
    -------
    ChoroplethResult
        Color mapping, legend intervals, and validation metrics.
    """
    matched, unmatched, missing = match_data_to_states(data_records, state_key, value_key)

    valid_values = [v for v in matched.values() if not math.isnan(v)]
    if not valid_values:
        # No numeric data
        state_colors = {st: no_data_color for st in STATE_ISO_CODES.keys()}
        state_values = {st: None for st in STATE_ISO_CODES.keys()}
        return ChoroplethResult(
            state_colors=state_colors,
            state_values=state_values,
            legend_bins=[],
            min_value=0.0,
            max_value=0.0,
            matched_count=0,
            unmatched_keys=unmatched,
            missing_regions=missing
        )

    min_v = min(valid_values)
    max_v = max(valid_values)

    # If min == max, handle degenerate case
    if abs(max_v - min_v) < 1e-9:
        max_v = min_v + 1.0

    colors = COLOR_PALETTES.get(palette, COLOR_PALETTES["YlGnBu"])
    # Sample palette at evenly spaced intervals for bins
    bin_colors = []
    for i in range(num_classes):
        t = i / max(1, num_classes - 1)
        idx_float = t * (len(colors) - 1)
        idx_low = int(idx_float)
        idx_high = min(len(colors) - 1, idx_low + 1)
        frac = idx_float - idx_low
        bin_colors.append(interpolate_color(colors[idx_low], colors[idx_high], frac))

    # Equal interval bins
    step = (max_v - min_v) / num_classes
    legend_bins = []
    for i in range(num_classes):
        b_min = min_v + i * step
        b_max = min_v + (i + 1) * step
        if max_v > 100:
            label = f"{b_min:,.0f} – {b_max:,.0f}"
        else:
            label = f"{b_min:.1f} – {b_max:.1f}"
        legend_bins.append(LegendBin(
            label=label,
            color=bin_colors[i],
            min_val=b_min,
            max_val=b_max
        ))

    state_colors = {}
    state_values = {}
    for canonical in STATE_ISO_CODES.keys():
        if canonical in matched and not math.isnan(matched[canonical]):
            val = matched[canonical]
            state_values[canonical] = val
            # Determine bin index
            bin_idx = int((val - min_v) / step)
            bin_idx = max(0, min(num_classes - 1, bin_idx))
            state_colors[canonical] = bin_colors[bin_idx]
        else:
            state_values[canonical] = None
            state_colors[canonical] = no_data_color

    return ChoroplethResult(
        state_colors=state_colors,
        state_values=state_values,
        legend_bins=legend_bins,
        min_value=min_v,
        max_value=max_v,
        matched_count=len(valid_values),
        unmatched_keys=unmatched,
        missing_regions=missing
    )
