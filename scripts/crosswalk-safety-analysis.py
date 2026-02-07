#!/usr/bin/env python3
"""
Analyze SDOT collision data to test hypothesis:
Pedestrians are still struck while crossing legally at signalized intersections,
supporting the case for exclusive pedestrian phases over LPIs.

Data source: SDOT Collisions All Years + SDOT Collisions Persons
via Seattle ArcGIS REST API.
"""

import json
import urllib.request
import urllib.parse
import sys
from collections import defaultdict

PERSONS_URL = "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_Persons/FeatureServer/0/query"
COLLISIONS_URL = "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_All_Years/FeatureServer/0/query"


def query_arcgis(base_url, params):
    """Execute an ArcGIS REST API query and return features or statistics."""
    params["f"] = "json"
    url = base_url + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (urbanism-guide analysis)")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if "error" in data:
            print(f"  API error: {data['error']}", file=sys.stderr)
            return []
        if "features" in data:
            return [f["attributes"] for f in data["features"]]
        return data
    except Exception as e:
        print(f"  Request failed: {e}", file=sys.stderr)
        return []


def stat_query(base_url, where, group_fields, count_field="OBJECTID"):
    """Run a count-groupby statistical query."""
    stats = json.dumps([{
        "statisticType": "count",
        "onStatisticField": count_field,
        "outStatisticFieldName": "cnt"
    }])
    params = {
        "where": where,
        "outStatistics": stats,
        "groupByFieldsForStatistics": group_fields,
        "orderByFields": "cnt DESC",
        "resultRecordCount": 100,
    }
    return query_arcgis(base_url, params)


def count_query(base_url, where):
    """Get a simple count."""
    params = {
        "where": where,
        "returnCountOnly": "true",
    }
    result = query_arcgis(base_url, params)
    if isinstance(result, dict) and "count" in result:
        return result["count"]
    return 0


def paginated_query(base_url, where, out_fields, max_records=2000):
    """Paginate through all matching records."""
    all_records = []
    offset = 0
    while True:
        params = {
            "where": where,
            "outFields": out_fields,
            "resultRecordCount": max_records,
            "resultOffset": offset,
        }
        batch = query_arcgis(base_url, params)
        if not batch:
            break
        all_records.extend(batch)
        if len(batch) < max_records:
            break
        offset += max_records
    return all_records


def epoch_to_year(epoch_ms):
    """Convert epoch milliseconds to year."""
    if epoch_ms is None:
        return None
    import datetime
    return datetime.datetime.utcfromtimestamp(epoch_ms / 1000).year


def main():
    print("=" * 70)
    print("SEATTLE PEDESTRIAN CROSSWALK SAFETY ANALYSIS")
    print("Data: SDOT Collisions All Years + Persons (ArcGIS)")
    print("=" * 70)

    # ---- 1. TOTAL PEDESTRIAN COLLISIONS ----
    print("\n--- 1. Total pedestrian collisions (all years) ---")
    total_ped = count_query(COLLISIONS_URL, "PEDCOUNT>=1")
    print(f"Total collisions involving pedestrians: {total_ped:,}")

    # ---- 2. PED ACTION DISTRIBUTION ----
    print("\n--- 2. Pedestrian action at time of collision ---")
    print("  (What was the pedestrian doing?)")
    ped_action = stat_query(
        PERSONS_URL,
        "ST_PARTCPNT_TYPE IN ('07','7')",
        "ST_PED_ACT_CD,ST_PED_ACT_DESC"
    )
    total_ped_persons = sum(r.get("cnt", 0) for r in ped_action)
    print(f"  Total pedestrian person-records: {total_ped_persons:,}")
    for r in ped_action:
        code = r.get("ST_PED_ACT_CD") or "?"
        desc = r.get("ST_PED_ACT_DESC") or "Unknown/NULL"
        cnt = r.get("cnt", 0)
        pct = cnt / total_ped_persons * 100 if total_ped_persons else 0
        print(f"  [{str(code):>2}] {str(desc):<55} {cnt:>5,}  ({pct:.1f}%)")

    # ---- 3. CROSSING WITH SIGNAL: INJURY SEVERITY ----
    print("\n--- 3. Injury severity: pedestrians crossing WITH signal ---")
    with_signal_severity = stat_query(
        PERSONS_URL,
        "ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1'",
        "ST_INJRY_CLSS,ST_INJRY_CLSS_DESC"
    )
    total_with_signal = sum(r.get("cnt", 0) for r in with_signal_severity)
    print(f"  Total pedestrians hit while crossing WITH signal: {total_with_signal:,}")
    for r in sorted(with_signal_severity, key=lambda x: str(x.get("ST_INJRY_CLSS") or "0")):
        desc = str(r.get("ST_INJRY_CLSS_DESC") or "Unknown")
        cnt = r.get("cnt", 0)
        pct = cnt / total_with_signal * 100 if total_with_signal else 0
        print(f"    {desc:<40} {cnt:>5,}  ({pct:.1f}%)")

    # ---- 4. CROSSING WITH SIGNAL: FACILITY TYPE (crosswalk?) ----
    print("\n--- 4. Facility type: pedestrians crossing WITH signal ---")
    with_signal_facility = stat_query(
        PERSONS_URL,
        "ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1'",
        "ST_PED_WAS_USING_CD,ST_PED_WAS_USING_DESC"
    )
    for r in with_signal_facility:
        desc = str(r.get("ST_PED_WAS_USING_DESC") or "Unknown/NULL")
        cnt = r.get("cnt", 0)
        pct = cnt / total_with_signal * 100 if total_with_signal else 0
        print(f"    {desc:<40} {cnt:>5,}  ({pct:.1f}%)")

    # ---- 5. CROSSING AGAINST SIGNAL: INJURY SEVERITY ----
    print("\n--- 5. Injury severity: pedestrians crossing AGAINST signal ---")
    against_signal_severity = stat_query(
        PERSONS_URL,
        "ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='2'",
        "ST_INJRY_CLSS,ST_INJRY_CLSS_DESC"
    )
    total_against = sum(r.get("cnt", 0) for r in against_signal_severity)
    print(f"  Total pedestrians hit while crossing AGAINST signal: {total_against:,}")
    for r in sorted(against_signal_severity, key=lambda x: str(x.get("ST_INJRY_CLSS") or "0")):
        desc = str(r.get("ST_INJRY_CLSS_DESC") or "Unknown")
        cnt = r.get("cnt", 0)
        pct = cnt / total_against * 100 if total_against else 0
        print(f"    {desc:<40} {cnt:>5,}  ({pct:.1f}%)")

    # ---- 6. COLLISION TYPE for ped collisions (turning vs straight) ----
    print("\n--- 6. Vehicle action in pedestrian collisions (state collision type) ---")
    collision_type = stat_query(
        COLLISIONS_URL,
        "PEDCOUNT>=1",
        "ST_COLCODE,ST_COLDESC"
    )
    for r in collision_type:
        code = str(r.get("ST_COLCODE") or "?")
        desc = str(r.get("ST_COLDESC") or "Unknown")
        cnt = r.get("cnt", 0)
        pct = cnt / total_ped * 100 if total_ped else 0
        print(f"  [{code:>2}] {desc:<55} {cnt:>5,}  ({pct:.1f}%)")

    # ---- 7. PEDROWNOTGRNT distribution ----
    print("\n--- 7. Pedestrian right-of-way not granted (main collisions table) ---")
    row_dist = stat_query(
        COLLISIONS_URL,
        "PEDCOUNT>=1",
        "PEDROWNOTGRNT"
    )
    for r in row_dist:
        val = r.get("PEDROWNOTGRNT")
        cnt = r.get("cnt", 0)
        pct = cnt / total_ped * 100 if total_ped else 0
        if val == "Y":
            val = "Y (ped did NOT have right of way)"
        elif val is None:
            val = "NULL (ped likely had ROW or unknown)"
        print(f"    {str(val):<55} {cnt:>5,}  ({pct:.1f}%)")

    # ---- 8. CONTRIBUTING CIRCUMSTANCES for peds crossing with signal ----
    print("\n--- 8. Contributing circumstances: peds crossing WITH signal ---")
    contribs = stat_query(
        PERSONS_URL,
        "ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1'",
        "ST_CONTRBCIR_CD1,ST_CONTRBCIR1_DESC"
    )
    for r in contribs:
        desc = str(r.get("ST_CONTRBCIR1_DESC") or "Unknown/NULL")
        cnt = r.get("cnt", 0)
        pct = cnt / total_with_signal * 100 if total_with_signal else 0
        print(f"    {desc:<55} {cnt:>5,}  ({pct:.1f}%)")

    # ---- 9. YEAR-BY-YEAR TREND: peds crossing with signal ----
    print("\n--- 9. Year-by-year: pedestrians hit while crossing WITH signal ---")
    print("  (Fetching individual records with dates...)")
    records = paginated_query(
        PERSONS_URL,
        "ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1'",
        "INCDATE,ST_INJRY_CLSS,ST_INJRY_CLSS_DESC"
    )
    year_counts = defaultdict(lambda: {"total": 0, "fatal": 0, "serious": 0, "injury": 0})
    for r in records:
        yr = epoch_to_year(r.get("INCDATE"))
        if yr is None or yr < 2006:
            continue
        year_counts[yr]["total"] += 1
        injry = str(r.get("ST_INJRY_CLSS", "0"))
        if injry in ("2", "3", "4"):  # dead at scene, DOA, died at hospital
            year_counts[yr]["fatal"] += 1
        elif injry == "5":
            year_counts[yr]["serious"] += 1
        elif injry in ("6", "7"):
            year_counts[yr]["injury"] += 1

    print(f"  {'Year':<6} {'Total':>6} {'Fatal':>6} {'Serious':>8} {'Injury':>7}")
    print(f"  {'-'*5:<6} {'-'*5:>6} {'-'*5:>6} {'-'*7:>8} {'-'*6:>7}")
    for yr in sorted(year_counts.keys()):
        d = year_counts[yr]
        print(f"  {yr:<6} {d['total']:>6,} {d['fatal']:>6,} {d['serious']:>8,} {d['injury']:>7,}")

    # ---- 10. YEAR-BY-YEAR TREND: all ped collisions for comparison ----
    print("\n--- 10. Year-by-year: ALL pedestrian collisions (for context) ---")
    all_ped_records = paginated_query(
        COLLISIONS_URL,
        "PEDCOUNT>=1",
        "INCDATE,SEVERITYCODE,SEVERITYDESC,FATALITIES,SERIOUSINJURIES,INJURIES"
    )
    all_year = defaultdict(lambda: {"total": 0, "fatal": 0, "serious": 0, "injuries": 0})
    for r in all_ped_records:
        yr = epoch_to_year(r.get("INCDATE"))
        if yr is None or yr < 2006:
            continue
        all_year[yr]["total"] += 1
        all_year[yr]["fatal"] += (r.get("FATALITIES") or 0)
        all_year[yr]["serious"] += (r.get("SERIOUSINJURIES") or 0)
        all_year[yr]["injuries"] += (r.get("INJURIES") or 0)

    print(f"  {'Year':<6} {'Collisions':>10} {'Fatalities':>10} {'Serious':>8} {'Injuries':>8}")
    print(f"  {'-'*5:<6} {'-'*9:>10} {'-'*9:>10} {'-'*7:>8} {'-'*7:>8}")
    for yr in sorted(all_year.keys()):
        d = all_year[yr]
        print(f"  {yr:<6} {d['total']:>10,} {d['fatal']:>10,} {d['serious']:>8,} {d['injuries']:>8,}")

    # ---- 11. SEVERITY: ped collisions where ped had ROW (crossing with signal, marked XW) ----
    print("\n--- 11. Severity: peds in marked crosswalk, crossing WITH signal ---")
    legal_severity = stat_query(
        PERSONS_URL,
        "ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1' AND ST_PED_WAS_USING_CD='4'",
        "ST_INJRY_CLSS,ST_INJRY_CLSS_DESC"
    )
    total_legal = sum(r.get("cnt", 0) for r in legal_severity)
    print(f"  Peds in marked crosswalk crossing with signal: {total_legal:,}")
    fatal_legal = 0
    serious_legal = 0
    for r in sorted(legal_severity, key=lambda x: str(x.get("ST_INJRY_CLSS") or "0")):
        desc = str(r.get("ST_INJRY_CLSS_DESC") or "Unknown")
        clss = str(r.get("ST_INJRY_CLSS") or "0")
        cnt = r.get("cnt", 0)
        pct = cnt / total_legal * 100 if total_legal else 0
        print(f"    {desc:<40} {cnt:>5,}  ({pct:.1f}%)")
        if clss in ("2", "3", "4"):
            fatal_legal += cnt
        elif clss == "5":
            serious_legal += cnt

    print(f"\n  ** FATAL + SERIOUS among legal crosswalk users: {fatal_legal + serious_legal:,} "
          f"({(fatal_legal + serious_legal) / total_legal * 100:.1f}% of {total_legal:,})" if total_legal else "")

    # ---- 12. Driver contributing circumstances when ped was crossing legally ----
    print("\n--- 12. Driver contributing circumstances for collisions where ped crossed with signal ---")
    # Get the COLDETKEYs for peds crossing with signal, then check the driver records
    # Actually, let's look at the vehicle-side contributing circumstances from the same incidents
    # We need a different approach - get REPORTNOs for ped-with-signal incidents, then query driver records
    # This is complex, so let's use contributing circumstances from the ped records themselves
    # which may include codes about the OTHER party

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    # ---- SUMMARY for blog post ----
    print("\n\n=== BLOG POST DATA SUMMARY ===\n")
    print(f"Total pedestrian collisions (all years): {total_ped:,}")
    print(f"Pedestrians hit crossing WITH signal: {total_with_signal:,}")
    print(f"  - of those, in marked crosswalk: {total_legal:,}")
    print(f"  - of those, fatal or serious injury: {fatal_legal + serious_legal:,}")
    print(f"Pedestrians hit crossing AGAINST signal: {total_against:,}")

    # Turning collisions
    turning_count = 0
    straight_count = 0
    for r in collision_type:
        code = str(r.get("ST_COLCODE", ""))
        cnt = r.get("cnt", 0)
        if code in ("1", "2"):  # turning right, turning left
            turning_count += cnt
        elif code == "0":  # going straight
            straight_count += cnt
    print(f"\nVehicle action in ALL ped collisions:")
    print(f"  Turning (left+right): {turning_count:,} ({turning_count/total_ped*100:.1f}%)" if total_ped else "")
    print(f"  Going straight: {straight_count:,} ({straight_count/total_ped*100:.1f}%)" if total_ped else "")

    # PEDROWNOTGRNT
    for r in row_dist:
        val = r.get("PEDROWNOTGRNT")
        if val == "Y":
            ped_no_row = r.get("cnt", 0)
        elif val is None:
            ped_had_row = r.get("cnt", 0)
    print(f"\nPedestrian right-of-way:")
    try:
        print(f"  Ped did NOT have ROW: {ped_no_row:,} ({ped_no_row/total_ped*100:.1f}%)")
        print(f"  Ped had ROW (or unknown): {ped_had_row:,} ({ped_had_row/total_ped*100:.1f}%)")
    except:
        pass


if __name__ == "__main__":
    main()
