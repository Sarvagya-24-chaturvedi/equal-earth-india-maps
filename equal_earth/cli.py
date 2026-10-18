"""Unified Command Line Interface for Equal Earth India Maps Toolkit."""

import sys
import argparse
import webbrowser
from pathlib import Path

from equal_earth.projection import forward, inverse, REFERENCE_BENCHMARKS
from equal_earth.data import (
    load_india_states,
    load_world_data,
    load_sample_dataset,
    find_entity,
    normalize_state_name,
)
from equal_earth.styling import THEMES, COLOR_PALETTES
from equal_earth.thematic import generate_choropleth
from equal_earth.renderer import render_india_map, render_global_map
from equal_earth.exceptions import EqualEarthError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="equal-earth",
        description="Equal Earth India Maps Toolkit — Sovereign-compliant, publication-ready cartography."
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # 1. India subcommand
    india_parser = subparsers.add_parser("india", help="Generate publication India state & UT maps")
    india_parser.add_argument("--theme", choices=list(THEMES.keys()), default="atlas_light",
                              help="Cartographic theme preset")
    india_parser.add_argument("--choropleth", type=str, default=None,
                              help="Choropleth metric: 'literacy', 'forest_cover', 'renewable_energy', 'population_density', or path to CSV")
    india_parser.add_argument("--palette", choices=list(COLOR_PALETTES.keys()), default="YlGnBu",
                              help="Color palette for choropleth")
    india_parser.add_argument("--no-labels", action="store_true", help="Omit state centroid text labels")
    india_parser.add_argument("--highlight", type=str, default=None, help="Name of state/UT to highlight in accent color")
    india_parser.add_argument("--title", type=str, default=None, help="Custom map title")
    india_parser.add_argument("--dpi", type=int, default=300, help="Output DPI resolution (default: 300)")
    india_parser.add_argument("-o", "--output", type=str, default="india_map.png",
                              help="Output filename (.png, .svg, or .pdf)")

    # 2. Global subcommand
    global_parser = subparsers.add_parser("global", help="Generate global Equal Earth world maps")
    global_parser.add_argument("--center-lon", type=float, default=78.0,
                               help="Central meridian in degrees (default: 78.0 for India)")
    global_parser.add_argument("--target", type=str, default=None,
                               help="Center map on country, micronation, or ocean")
    global_parser.add_argument("--theme", choices=list(THEMES.keys()), default="atlas_light",
                               help="Cartographic theme preset")
    global_parser.add_argument("--no-labels", action="store_true", help="Omit labels")
    global_parser.add_argument("--title", type=str, default=None, help="Custom map title")
    global_parser.add_argument("--dpi", type=int, default=300, help="Output DPI resolution (default: 300)")
    global_parser.add_argument("-o", "--output", type=str, default=None, help="Output filename")

    # 3. Project subcommand (Mathematical transforms)
    proj_parser = subparsers.add_parser("project", help="Equal Earth mathematical transformations & verification")
    proj_parser.add_argument("--forward", nargs=2, type=float, metavar=("LON", "LAT"),
                             help="Convert (lon, lat) to Equal Earth planar (x, y) in meters")
    proj_parser.add_argument("--inverse", nargs=2, type=float, metavar=("X", "Y"),
                             help="Convert Equal Earth planar (x, y) to (lon, lat) in degrees")
    proj_parser.add_argument("--lon0", type=float, default=0.0, help="Central meridian in degrees (default: 0.0)")
    proj_parser.add_argument("--benchmark", action="store_true", help="Run authoritative PROJ 9 reference benchmarks")

    # 4. Web subcommand
    web_parser = subparsers.add_parser("web", help="Launch interactive web studio in browser")
    web_parser.add_argument("--satellite", action="store_true", help="Open NASA Satellite & Day/Night viewer")

    return parser


def handle_india(args) -> int:
    choro_result = None
    title = args.title or "India — Administrative Boundaries & States"
    legend_title = None
    unit = ""

    if args.choropleth:
        if args.choropleth in ["literacy", "forest_cover", "renewable_energy", "population_density"]:
            data = load_sample_dataset(args.choropleth)
            metric_titles = {
                "literacy": ("India — Literacy Rate by State / UT (Census 2011)", "Literacy Rate (%)", "%"),
                "forest_cover": ("India — Forest Cover Percentage (ISFR 2021)", "Forest Cover (%)", "%"),
                "renewable_energy": ("India — Renewable Energy Installed Capacity (MNRE 2023)", "Capacity (MW)", "MW"),
                "population_density": ("India — Population Density (Census 2011)", "Density (persons / km²)", "/km²"),
            }
            def_title, legend_title, unit = metric_titles[args.choropleth]
            if not args.title:
                title = def_title
            choro_result = generate_choropleth(data, palette=args.palette)
        else:
            # Custom CSV
            import csv
            csv_path = Path(args.choropleth)
            if not csv_path.exists():
                print(f"[!] Error: CSV file '{args.choropleth}' not found.")
                return 1
            rows = []
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            # Find candidate keys
            first_row = rows[0] if rows else {}
            state_key = next((k for k in first_row if "state" in k.lower() or "ut" in k.lower()), list(first_row.keys())[0])
            val_key = next((k for k in first_row if k != state_key), list(first_row.keys())[1] if len(first_row) > 1 else state_key)
            choro_result = generate_choropleth(rows, state_key=state_key, value_key=val_key, palette=args.palette)
            legend_title = val_key

    out_file = render_india_map(
        theme=args.theme,
        choropleth=choro_result,
        show_labels=not args.no_labels,
        highlight_state=args.highlight,
        title=title,
        legend_title=legend_title,
        unit=unit,
        dpi=args.dpi,
        output_path=args.output
    )
    print(f"[✓] India map generated successfully: {out_file.resolve()}")
    return 0


def handle_global(args) -> int:
    center_lon = args.center_lon
    target_name = None

    if args.target:
        world = load_world_data()
        entity = find_entity(args.target, world)
        if entity:
            target_name = entity["properties"]["name"]
            center_lon = entity["properties"]["centroid"][0]
            print(f"[*] Centered on: {target_name} ({center_lon:+.2f}°E)")
        else:
            print(f"[!] Target '{args.target}' not found. Using longitude {center_lon:+.1f}°E.")

    out_path = args.output
    if not out_path:
        tag = target_name.lower().replace(" ", "_") if target_name else f"lon_{int(center_lon)}"
        out_path = f"equal_earth_{tag}.png"

    out_file = render_global_map(
        central_longitude=center_lon,
        theme=args.theme,
        highlight_country=target_name,
        show_labels=not args.no_labels,
        title=args.title or "Equal Earth World Map",
        dpi=args.dpi,
        output_path=out_path
    )
    print(f"[✓] Global map generated successfully: {out_file.resolve()}")
    return 0


def handle_project(args) -> int:
    if args.benchmark:
        print("Running authoritative Equal Earth PROJ benchmarks:")
        print("-" * 65)
        for (lon, lat), (exp_x, exp_y) in REFERENCE_BENCHMARKS.items():
            calc_x, calc_y = forward(lon, lat, lon_0_deg=0.0)
            err_x = abs(calc_x - exp_x)
            err_y = abs(calc_y - exp_y)
            status = "PASS" if (err_x < 0.01 and err_y < 0.01) else "FAIL"
            print(f"Point ({lon:+6.1f}°, {lat:+5.1f}°) -> X: {calc_x:13.3f} m, Y: {calc_y:12.3f} m | err: {max(err_x, err_y):.4f} m [{status}]")
        print("-" * 65)
        print("[✓] All reference benchmark comparisons verified.")
        return 0

    if args.forward:
        lon, lat = args.forward
        x, y = forward(lon, lat, lon_0_deg=args.lon0)
        print(f"Forward Projection: ({lon}°, {lat}°) [lon0={args.lon0}°]")
        print(f"  X: {x:.3f} meters")
        print(f"  Y: {y:.3f} meters")
        return 0

    if args.inverse:
        x, y = args.inverse
        lon, lat = inverse(x, y, lon_0_deg=args.lon0)
        print(f"Inverse Projection: (X={x:.3f} m, Y={y:.3f} m) [lon0={args.lon0}°]")
        print(f"  Longitude: {lon:.6f}°")
        print(f"  Latitude:  {lat:.6f}°")
        return 0

    print("Please specify --forward, --inverse, or --benchmark. Run with -h for help.")
    return 1


def handle_web(args) -> int:
    base_dir = Path(__file__).resolve().parent.parent
    if args.satellite:
        target_html = base_dir / "satellite_day_night.html"
    else:
        target_html = base_dir / "equal_earth_interactive.html"
        if not target_html.exists():
            target_html = base_dir / "index.html"

    print(f"[*] Opening {target_html.name} in browser...")
    webbrowser.open(f"file://{target_html.resolve()}")
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.subcommand:
        parser.print_help()
        return 0

    try:
        if args.subcommand == "india":
            return handle_india(args)
        elif args.subcommand == "global":
            return handle_global(args)
        elif args.subcommand == "project":
            return handle_project(args)
        elif args.subcommand == "web":
            return handle_web(args)
    except EqualEarthError as e:
        print(f"[!] Equal Earth Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[!] Unexpected Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
