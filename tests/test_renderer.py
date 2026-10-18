"""Tests for Cartopy rendering, themes, labels, legends, and multi-format export (PNG, SVG, PDF)."""

import os
import pytest
from pathlib import Path

from equal_earth.renderer import render_india_map, render_global_map
from equal_earth.data import load_sample_dataset
from equal_earth.thematic import generate_choropleth
from equal_earth.styling import get_theme, THEMES


def test_render_india_map_png(tmp_path):
    """Test generating standard India administrative PNG."""
    out_file = tmp_path / "india_test.png"
    result = render_india_map(output_path=out_file, dpi=100)
    assert result.exists()
    assert result.stat().st_size > 50000  # At least 50 KB


def test_render_india_map_svg_and_pdf(tmp_path):
    """Test vector format exports: SVG and PDF."""
    svg_file = tmp_path / "india_test.svg"
    pdf_file = tmp_path / "india_test.pdf"

    res_svg = render_india_map(output_path=svg_file, show_labels=False)
    assert res_svg.exists()
    assert res_svg.stat().st_size > 10000

    res_pdf = render_india_map(output_path=pdf_file, show_labels=False)
    assert res_pdf.exists()
    assert res_pdf.stat().st_size > 10000


def test_render_india_choropleth(tmp_path):
    """Test rendering data-driven choropleth map with legend."""
    data = load_sample_dataset("literacy")
    choro = generate_choropleth(data, palette="YlGnBu")

    out_file = tmp_path / "india_literacy.png"
    result = render_india_map(
        choropleth=choro,
        title="India — Literacy Rate (Census 2011)",
        legend_title="Literacy (%)",
        unit="%",
        output_path=out_file,
        dpi=100
    )
    assert result.exists()
    assert result.stat().st_size > 50000


def test_render_with_themes(tmp_path):
    """Test rendering with different theme presets."""
    for theme_key in ["academic_clean", "carto_dark"]:
        out_file = tmp_path / f"india_{theme_key}.png"
        result = render_india_map(theme=theme_key, output_path=out_file, dpi=80)
        assert result.exists()
        assert result.stat().st_size > 30000


def test_render_global_map_india_centered(tmp_path):
    """Test rendering global Equal Earth map centered on India (78°E)."""
    out_file = tmp_path / "global_78E.png"
    result = render_global_map(central_longitude=78.0, output_path=out_file, dpi=80)
    assert result.exists()
    assert result.stat().st_size > 40000


def test_render_global_map_prime_meridian(tmp_path):
    """Test rendering global Equal Earth map centered on 0°."""
    out_file = tmp_path / "global_0E.png"
    result = render_global_map(central_longitude=0.0, output_path=out_file, dpi=80)
    assert result.exists()
    assert result.stat().st_size > 40000
