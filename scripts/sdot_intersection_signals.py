#!/usr/bin/env python3
"""Query SDOT ArcGIS datasets for intersection signal changes.

Covers three complementary FeatureServer layers:

  1. Vision_Zero_Signals_LPI_NTOR  – LPI and No-Turn-On-Red status per signal
  2. Traffic_Signal_Assemblies_(Active) – full signal inventory with install /
     modification dates for pedestrian heads, audio devices, left-turn phases, etc.
  3. Bicycle_and_Pedestrian_Safety_Analysis_Intersections – safety analysis scores

All endpoints live under Seattle's ArcGIS org (ZOyb2t4B0UYuYNYH) and return JSON.
Pagination is handled automatically (ArcGIS caps results at ~2000 per request).

Usage:
    python3 scripts/sdot_intersection_signals.py [--action ACTION]

Actions:
    lpi_summary         Count of signals with/without LPI (default)
    lpi_list            List all intersections that have LPI installed
    ntor_list           List all intersections with No-Turn-On-Red
    recent_installs     Signals installed or modified in the last N years
    signal_details      Full detail for a specific signal by UNITID (e.g. SGL-100)
    search              Search intersections by street name
"""

import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# ArcGIS endpoint constants
# ---------------------------------------------------------------------------
_BASE = "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services"

ENDPOINTS = {
    "lpi_ntor": f"{_BASE}/Vision_Zero_Signals_LPI_NTOR/FeatureServer/0",
    "signals_active": f"{_BASE}/Traffic_Signal_Assemblies_(Active)/FeatureServer/0",
    "safety_analysis": f"{_BASE}/Bicycle_and_Pedestrian_Safety_Analysis_Intersections/FeatureServer/0",
}

PAGE_SIZE = 2000  # ArcGIS max per request


# ---------------------------------------------------------------------------
# Generic ArcGIS query helpers
# ---------------------------------------------------------------------------
def query_arcgis(endpoint: str, params: dict) -> dict:
    """Execute a single ArcGIS REST query and return the parsed JSON."""
    params.setdefault("f", "json")
    url = f"{endpoint}/query?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "sdot-intersection-tool/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def query_all_features(endpoint: str, params: dict) -> list[dict]:
    """Page through an ArcGIS endpoint and return all feature attribute dicts."""
    params = dict(params)  # copy
    params.setdefault("where", "1=1")
    params.setdefault("outFields", "*")
    params["resultRecordCount"] = PAGE_SIZE

    all_features: list[dict] = []
    offset = 0
    while True:
        params["resultOffset"] = offset
        data = query_arcgis(endpoint, params)
        features = data.get("features", [])
        all_features.extend(f["attributes"] for f in features)
        if len(features) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return all_features


def count_features(endpoint: str, where: str = "1=1") -> int:
    """Return the total feature count for a where clause."""
    data = query_arcgis(endpoint, {"where": where, "returnCountOnly": "true"})
    return data.get("count", 0)


def epoch_ms_to_date(epoch_ms: int | None) -> str | None:
    """Convert ArcGIS epoch-millisecond timestamp to YYYY-MM-DD string."""
    if epoch_ms is None:
        return None
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Action implementations
# ---------------------------------------------------------------------------
def lpi_summary() -> None:
    """Print summary counts of LPI and NTOR status across all signals."""
    ep = ENDPOINTS["lpi_ntor"]
    total = count_features(ep)
    lpi_ex = count_features(ep, "LPI_Status='Ex'")
    ntor_ex = count_features(ep, "NTOR_Status='Ex'")
    both = count_features(ep, "LPI_Status='Ex' AND NTOR_Status='Ex'")

    print("=== SDOT Vision Zero – Signal LPI & NTOR Summary ===\n")
    print(f"  Total signalised intersections:  {total:,}")
    print(f"  With Leading Pedestrian Interval: {lpi_ex:,}  ({100*lpi_ex/total:.1f}%)")
    print(f"  With No Turn On Red:              {ntor_ex:,}  ({100*ntor_ex/total:.1f}%)")
    print(f"  With both LPI and NTOR:           {both:,}  ({100*both/total:.1f}%)")
    print(f"\nSource: {ep}")


def lpi_list() -> None:
    """List every intersection that currently has LPI installed."""
    ep = ENDPOINTS["lpi_ntor"]
    rows = query_all_features(ep, {
        "where": "LPI_Status='Ex'",
        "outFields": "UNITID,Location,LPI_Approach,NTOR_Status,NTOR_Approach,SIGNAL_TYPE",
        "orderByFields": "Location ASC",
    })
    print(f"=== Intersections with Leading Pedestrian Interval ({len(rows)} total) ===\n")
    print(f"{'UNITID':<12} {'LPI Approach':<14} {'NTOR':<6} {'Type':<6} {'Location'}")
    print("-" * 90)
    for r in rows:
        loc = (r.get("Location") or "").strip()
        print(
            f"{r.get('UNITID',''):<12} "
            f"{r.get('LPI_Approach',''):<14} "
            f"{r.get('NTOR_Status',''):<6} "
            f"{r.get('SIGNAL_TYPE',''):<6} "
            f"{loc}"
        )


def ntor_list() -> None:
    """List every intersection that currently has No-Turn-On-Red."""
    ep = ENDPOINTS["lpi_ntor"]
    rows = query_all_features(ep, {
        "where": "NTOR_Status='Ex'",
        "outFields": "UNITID,Location,NTOR_Approach,LPI_Status,LPI_Approach,SIGNAL_TYPE",
        "orderByFields": "Location ASC",
    })
    print(f"=== Intersections with No Turn On Red ({len(rows)} total) ===\n")
    print(f"{'UNITID':<12} {'NTOR Approach':<14} {'LPI':<6} {'Type':<6} {'Location'}")
    print("-" * 90)
    for r in rows:
        loc = (r.get("Location") or "").strip()
        print(
            f"{r.get('UNITID',''):<12} "
            f"{r.get('NTOR_Approach',''):<14} "
            f"{r.get('LPI_Status',''):<6} "
            f"{r.get('SIGNAL_TYPE',''):<6} "
            f"{loc}"
        )


def recent_installs(years: int = 3) -> None:
    """Show signals installed or significantly modified in the last N years.

    Checks INSTALL_DATE, PEDHDFIRSTINSTALLDT (ped-head install),
    PEDAUDIOINSTALLDT, LTFIRSTINSTALLDT, and RTFIRSTINSTALLDT.
    """
    ep = ENDPOINTS["signals_active"]
    cutoff_dt = datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year - years)
    cutoff_str = cutoff_dt.strftime("%Y-%m-%d")

    date_fields = [
        "INSTALL_DATE",
        "PEDHDFIRSTINSTALLDT",
        "PEDAUDIOINSTALLDT",
        "LTFIRSTINSTALLDT",
        "RTFIRSTINSTALLDT",
        "PEDPSHINSTALLDT",
    ]
    # ArcGIS requires DATE 'YYYY-MM-DD' syntax for date comparisons
    where_parts = [f"{col} >= DATE '{cutoff_str}'" for col in date_fields]
    where = " OR ".join(where_parts)

    out_fields = ",".join([
        "UNITID", "UNITDESC", "SIGNAL_TYPE", "CURRENT_STATUS",
        *date_fields,
    ])

    rows = query_all_features(ep, {
        "where": where,
        "outFields": out_fields,
        "orderByFields": "INSTALL_DATE DESC",
    })

    print(f"=== Signals installed/modified in the last {years} year(s) ({len(rows)} results) ===\n")
    print(f"{'UNITID':<12} {'Installed':<12} {'PedHead':<12} {'Audio':<12} {'LT Phase':<12} {'Location'}")
    print("-" * 100)
    for r in rows:
        loc = (r.get("UNITDESC") or "").strip()
        print(
            f"{r.get('UNITID',''):<12} "
            f"{epoch_ms_to_date(r.get('INSTALL_DATE')) or '—':<12} "
            f"{epoch_ms_to_date(r.get('PEDHDFIRSTINSTALLDT')) or '—':<12} "
            f"{epoch_ms_to_date(r.get('PEDAUDIOINSTALLDT')) or '—':<12} "
            f"{epoch_ms_to_date(r.get('LTFIRSTINSTALLDT')) or '—':<12} "
            f"{loc}"
        )

    print(f"\nSource: {ep}")


def signal_details(unit_id: str) -> None:
    """Print every field for a single signal assembly (e.g. SGL-100)."""
    ep = ENDPOINTS["signals_active"]
    rows = query_all_features(ep, {
        "where": f"UNITID='{unit_id}'",
        "outFields": "*",
    })
    if not rows:
        print(f"No signal found with UNITID = {unit_id}")
        return

    r = rows[0]
    print(f"=== Signal Detail: {unit_id} ===\n")
    for k, v in sorted(r.items()):
        # Pretty-print date fields
        if k.upper().endswith(("DT", "DATE", "DTTM")) and isinstance(v, (int, float)) and v:
            v = f"{v}  ({epoch_ms_to_date(int(v))})"
        if isinstance(v, str):
            v = v.strip()
        print(f"  {k}: {v}")


def search_intersections(street: str) -> None:
    """Search signals by street name (case-insensitive substring match)."""
    ep = ENDPOINTS["lpi_ntor"]
    street_upper = street.upper()
    where = f"Location LIKE '%{street_upper}%'"
    rows = query_all_features(ep, {
        "where": where,
        "outFields": "UNITID,Location,LPI_Status,LPI_Approach,NTOR_Status,NTOR_Approach,SIGNAL_TYPE,INSTALL_DATE",
        "orderByFields": "Location ASC",
    })
    print(f"=== Signals matching '{street}' ({len(rows)} results) ===\n")
    print(f"{'UNITID':<12} {'LPI':<6} {'NTOR':<6} {'Type':<6} {'Location'}")
    print("-" * 90)
    for r in rows:
        loc = (r.get("Location") or "").strip()
        print(
            f"{r.get('UNITID',''):<12} "
            f"{r.get('LPI_Status',''):<6} "
            f"{r.get('NTOR_Status',''):<6} "
            f"{r.get('SIGNAL_TYPE',''):<6} "
            f"{loc}"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query SDOT ArcGIS data for intersection signal changes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--action",
        choices=["lpi_summary", "lpi_list", "ntor_list", "recent_installs", "signal_details", "search"],
        default="lpi_summary",
        help="Which query to run (default: lpi_summary)",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=3,
        help="For recent_installs: look back this many years (default: 3)",
    )
    parser.add_argument(
        "--unit-id",
        type=str,
        default="",
        help="For signal_details: the UNITID to look up (e.g. SGL-100)",
    )
    parser.add_argument(
        "--street",
        type=str,
        default="",
        help="For search: street name substring to match",
    )
    args = parser.parse_args()

    match args.action:
        case "lpi_summary":
            lpi_summary()
        case "lpi_list":
            lpi_list()
        case "ntor_list":
            ntor_list()
        case "recent_installs":
            recent_installs(args.years)
        case "signal_details":
            if not args.unit_id:
                parser.error("--unit-id is required for signal_details")
            signal_details(args.unit_id)
        case "search":
            if not args.street:
                parser.error("--street is required for search")
            search_intersections(args.street)


if __name__ == "__main__":
    main()
