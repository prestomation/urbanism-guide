#!/usr/bin/env python3
"""
Cross-reference SDOT collision data with LPI intersection inventory.

Joins:
  - Vision_Zero_Signals_LPI_NTOR (which intersections have LPIs)
  - SDOT_Collisions_All_Years (pedestrian collisions with INTKEY)
  - SDOT_Collisions_Persons (per-person detail, ST_PED_ACT_CD=1 for crossing with signal)

Join path: Persons.COLDETKEY -> Collisions.COLDETKEY -> Collisions.INTKEY -> LPI.INTKEY
"""

import json
import urllib.request
import urllib.parse
import sys
import datetime
from collections import defaultdict

LPI_URL = "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Vision_Zero_Signals_LPI_NTOR/FeatureServer/0/query"
COLLISIONS_URL = "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_All_Years/FeatureServer/0/query"
PERSONS_URL = "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_Persons/FeatureServer/0/query"


def query_arcgis(base_url, params):
    params["f"] = "json"
    url = base_url + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (urbanism-guide analysis)")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
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


def paginated_query(base_url, where, out_fields, max_records=2000):
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
        print(f"    ... fetched {len(all_records)} records", file=sys.stderr)
        if len(batch) < max_records:
            break
        offset += max_records
    return all_records


def epoch_to_year(epoch_ms):
    if epoch_ms is None:
        return None
    return datetime.datetime.utcfromtimestamp(epoch_ms / 1000).year


def main():
    print("=" * 70)
    print("LPI INTERSECTION CROSS-REFERENCE ANALYSIS")
    print("=" * 70)

    # ---- Step 1: Get all LPI intersection INTKEYs ----
    print("\n--- Step 1: Fetching LPI intersection inventory ---")
    lpi_records = paginated_query(
        LPI_URL,
        "1=1",
        "INTKEY,LPI_Status,LPI_Approach,NTOR_Status,UNITDESC"
    )
    print(f"  Total signalized intersections: {len(lpi_records)}")

    lpi_intkeys = set()
    non_lpi_intkeys = set()
    all_signal_intkeys = set()
    for r in lpi_records:
        intkey = r.get("INTKEY")
        if intkey is None:
            continue
        all_signal_intkeys.add(intkey)
        if r.get("LPI_Status") == "Ex":
            lpi_intkeys.add(intkey)
        else:
            non_lpi_intkeys.add(intkey)

    print(f"  Intersections with LPI: {len(lpi_intkeys)}")
    print(f"  Intersections without LPI: {len(non_lpi_intkeys)}")

    # ---- Step 2: Get all pedestrian collisions with INTKEY ----
    print("\n--- Step 2: Fetching pedestrian collisions ---")
    ped_collisions = paginated_query(
        COLLISIONS_URL,
        "PEDCOUNT>=1",
        "COLDETKEY,INTKEY,INCDATE,SEVERITYCODE,SEVERITYDESC,FATALITIES,SERIOUSINJURIES,INJURIES,ST_COLCODE,ST_COLDESC,PEDROWNOTGRNT"
    )
    print(f"  Total pedestrian collisions: {len(ped_collisions)}")

    # Build COLDETKEY -> collision lookup
    collision_by_coldetkey = {}
    for c in ped_collisions:
        cdk = c.get("COLDETKEY")
        if cdk is not None:
            collision_by_coldetkey[cdk] = c

    # Categorize collisions by LPI status
    at_lpi = []
    at_non_lpi = []
    at_signalized = []
    no_intkey = 0
    for c in ped_collisions:
        intkey = c.get("INTKEY")
        if intkey is None:
            no_intkey += 1
            continue
        if intkey in lpi_intkeys:
            at_lpi.append(c)
            at_signalized.append(c)
        elif intkey in non_lpi_intkeys:
            at_non_lpi.append(c)
            at_signalized.append(c)
        # else: not at a signalized intersection (skip)

    not_at_signal = len(ped_collisions) - len(at_signalized) - no_intkey

    print(f"\n  At LPI intersections: {len(at_lpi)}")
    print(f"  At non-LPI signalized intersections: {len(at_non_lpi)}")
    print(f"  At signalized intersections total: {len(at_signalized)}")
    print(f"  Not at any signalized intersection: {not_at_signal}")
    print(f"  No INTKEY: {no_intkey}")

    # ---- Step 3: Severity comparison ----
    print("\n--- Step 3: Severity at LPI vs non-LPI intersections ---")

    def severity_stats(collisions, label):
        total = len(collisions)
        fatal = sum(c.get("FATALITIES") or 0 for c in collisions)
        serious = sum(c.get("SERIOUSINJURIES") or 0 for c in collisions)
        injuries = sum(c.get("INJURIES") or 0 for c in collisions)
        turning = sum(1 for c in collisions if str(c.get("ST_COLCODE") or "") in ("1", "2"))
        print(f"\n  {label} ({total:,} collisions):")
        print(f"    Fatalities: {fatal}")
        print(f"    Serious injuries: {serious}")
        print(f"    Other injuries: {injuries}")
        print(f"    Turning-vehicle collisions: {turning} ({turning/total*100:.1f}%)" if total else "")
        per_intersection = total / max(1, len(lpi_intkeys) if "LPI" in label and "non" not in label.lower() else len(non_lpi_intkeys))
        print(f"    Avg collisions per intersection: {per_intersection:.1f}")
        return {"total": total, "fatal": fatal, "serious": serious,
                "injuries": injuries, "turning": turning}

    lpi_stats = severity_stats(at_lpi, "LPI intersections")
    non_lpi_stats = severity_stats(at_non_lpi, "Non-LPI signalized intersections")

    # ---- Step 4: Fetch person-level records for crossing-with-signal ----
    print("\n\n--- Step 4: Fetching person records (crossing with signal) ---")
    ped_persons = paginated_query(
        PERSONS_URL,
        "ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1'",
        "COLDETKEY,INCDATE,ST_INJRY_CLSS,ST_INJRY_CLSS_DESC,ST_PED_WAS_USING_CD"
    )
    print(f"  Pedestrians crossing with signal: {len(ped_persons)}")

    # Join persons to collisions to get INTKEY
    persons_at_lpi = []
    persons_at_non_lpi = []
    persons_at_signal = []
    persons_no_match = 0
    for p in ped_persons:
        cdk = p.get("COLDETKEY")
        collision = collision_by_coldetkey.get(cdk)
        if collision is None:
            persons_no_match += 1
            continue
        intkey = collision.get("INTKEY")
        if intkey is None:
            persons_no_match += 1
            continue
        # Attach collision fields to person record for analysis
        p["_intkey"] = intkey
        p["_st_colcode"] = collision.get("ST_COLCODE")
        if intkey in lpi_intkeys:
            persons_at_lpi.append(p)
            persons_at_signal.append(p)
        elif intkey in non_lpi_intkeys:
            persons_at_non_lpi.append(p)
            persons_at_signal.append(p)

    print(f"  Matched to LPI intersections: {len(persons_at_lpi)}")
    print(f"  Matched to non-LPI signalized: {len(persons_at_non_lpi)}")
    print(f"  Not matched to signalized intersection: {persons_no_match}")

    # ---- Step 5: Person-level severity at LPI vs non-LPI ----
    print("\n--- Step 5: Injury severity - crossing WITH signal at LPI vs non-LPI ---")

    def person_severity(persons, label, num_intersections):
        total = len(persons)
        if total == 0:
            print(f"\n  {label}: no records")
            return
        fatal = 0
        serious = 0
        injury = 0
        in_crosswalk = 0
        for p in persons:
            clss = str(p.get("ST_INJRY_CLSS") or "0")
            if clss in ("2", "3", "4"):
                fatal += 1
            elif clss == "5":
                serious += 1
            elif clss in ("6", "7"):
                injury += 1
            if str(p.get("ST_PED_WAS_USING_CD") or "") == "4":
                in_crosswalk += 1
        print(f"\n  {label} ({total:,} pedestrians crossing with signal):")
        print(f"    Fatal: {fatal} ({fatal/total*100:.1f}%)")
        print(f"    Serious injury: {serious} ({serious/total*100:.1f}%)")
        print(f"    Other injury: {injury} ({injury/total*100:.1f}%)")
        print(f"    Fatal + serious: {fatal + serious} ({(fatal+serious)/total*100:.1f}%)")
        print(f"    In marked crosswalk: {in_crosswalk} ({in_crosswalk/total*100:.1f}%)")
        print(f"    Avg per intersection: {total / num_intersections:.2f}")

    person_severity(persons_at_lpi, "LPI intersections", len(lpi_intkeys))
    person_severity(persons_at_non_lpi, "Non-LPI signalized intersections", len(non_lpi_intkeys))

    # ---- Step 6: Year-by-year at LPI intersections ----
    print("\n\n--- Step 6: Year-by-year - peds crossing with signal at LPI intersections ---")
    lpi_by_year = defaultdict(lambda: {"total": 0, "fatal": 0, "serious": 0})
    non_lpi_by_year = defaultdict(lambda: {"total": 0, "fatal": 0, "serious": 0})

    for p in persons_at_lpi:
        yr = epoch_to_year(p.get("INCDATE"))
        if yr is None or yr < 2006:
            continue
        lpi_by_year[yr]["total"] += 1
        clss = str(p.get("ST_INJRY_CLSS") or "0")
        if clss in ("2", "3", "4"):
            lpi_by_year[yr]["fatal"] += 1
        elif clss == "5":
            lpi_by_year[yr]["serious"] += 1

    for p in persons_at_non_lpi:
        yr = epoch_to_year(p.get("INCDATE"))
        if yr is None or yr < 2006:
            continue
        non_lpi_by_year[yr]["total"] += 1
        clss = str(p.get("ST_INJRY_CLSS") or "0")
        if clss in ("2", "3", "4"):
            non_lpi_by_year[yr]["fatal"] += 1
        elif clss == "5":
            non_lpi_by_year[yr]["serious"] += 1

    all_years = sorted(set(list(lpi_by_year.keys()) + list(non_lpi_by_year.keys())))
    print(f"\n  {'Year':<6} {'LPI Total':>10} {'LPI F+S':>8} {'nonLPI Tot':>11} {'nonLPI F+S':>11}")
    print(f"  {'-'*5:<6} {'-'*9:>10} {'-'*7:>8} {'-'*10:>11} {'-'*10:>11}")
    for yr in all_years:
        ld = lpi_by_year[yr]
        nd = non_lpi_by_year[yr]
        print(f"  {yr:<6} {ld['total']:>10,} {ld['fatal']+ld['serious']:>8,} {nd['total']:>11,} {nd['fatal']+nd['serious']:>11,}")

    # ---- Step 7: Turning collision breakdown at LPI intersections ----
    print("\n\n--- Step 7: Vehicle action at LPI vs non-LPI (all ped collisions) ---")

    def turning_breakdown(collisions, label):
        total = len(collisions)
        straight = sum(1 for c in collisions if str(c.get("ST_COLCODE") or "") == "0")
        left = sum(1 for c in collisions if str(c.get("ST_COLCODE") or "") == "2")
        right = sum(1 for c in collisions if str(c.get("ST_COLCODE") or "") == "1")
        other = total - straight - left - right
        print(f"\n  {label} ({total:,} collisions):")
        print(f"    Going straight: {straight:>5,} ({straight/total*100:.1f}%)" if total else "")
        print(f"    Turning left:   {left:>5,} ({left/total*100:.1f}%)" if total else "")
        print(f"    Turning right:  {right:>5,} ({right/total*100:.1f}%)" if total else "")
        print(f"    Other/unknown:  {other:>5,} ({other/total*100:.1f}%)" if total else "")
        print(f"    TOTAL turning:  {left+right:>5,} ({(left+right)/total*100:.1f}%)" if total else "")

    turning_breakdown(at_lpi, "LPI intersections")
    turning_breakdown(at_non_lpi, "Non-LPI signalized intersections")

    # ---- Step 8: Recent years (2020-2025) at LPI intersections ----
    print("\n\n--- Step 8: Recent years (2020-2025) focus ---")
    recent_lpi = [c for c in at_lpi if epoch_to_year(c.get("INCDATE")) and epoch_to_year(c.get("INCDATE")) >= 2020]
    recent_non_lpi = [c for c in at_non_lpi if epoch_to_year(c.get("INCDATE")) and epoch_to_year(c.get("INCDATE")) >= 2020]
    recent_lpi_persons = [p for p in persons_at_lpi if epoch_to_year(p.get("INCDATE")) and epoch_to_year(p.get("INCDATE")) >= 2020]
    recent_non_lpi_persons = [p for p in persons_at_non_lpi if epoch_to_year(p.get("INCDATE")) and epoch_to_year(p.get("INCDATE")) >= 2020]

    print(f"\n  Since 2020 (most LPIs already installed):")
    print(f"    Ped collisions at LPI intersections: {len(recent_lpi)}")
    print(f"      Fatalities: {sum(c.get('FATALITIES') or 0 for c in recent_lpi)}")
    print(f"      Serious injuries: {sum(c.get('SERIOUSINJURIES') or 0 for c in recent_lpi)}")
    print(f"    Ped collisions at non-LPI intersections: {len(recent_non_lpi)}")
    print(f"      Fatalities: {sum(c.get('FATALITIES') or 0 for c in recent_non_lpi)}")
    print(f"      Serious injuries: {sum(c.get('SERIOUSINJURIES') or 0 for c in recent_non_lpi)}")

    print(f"\n    Peds crossing WITH signal at LPI intersections: {len(recent_lpi_persons)}")
    recent_lpi_fatal = sum(1 for p in recent_lpi_persons if str(p.get("ST_INJRY_CLSS") or "0") in ("2","3","4"))
    recent_lpi_serious = sum(1 for p in recent_lpi_persons if str(p.get("ST_INJRY_CLSS") or "0") == "5")
    print(f"      Fatal: {recent_lpi_fatal}")
    print(f"      Serious injury: {recent_lpi_serious}")
    print(f"    Peds crossing WITH signal at non-LPI intersections: {len(recent_non_lpi_persons)}")
    recent_nlpi_fatal = sum(1 for p in recent_non_lpi_persons if str(p.get("ST_INJRY_CLSS") or "0") in ("2","3","4"))
    recent_nlpi_serious = sum(1 for p in recent_non_lpi_persons if str(p.get("ST_INJRY_CLSS") or "0") == "5")
    print(f"      Fatal: {recent_nlpi_fatal}")
    print(f"      Serious injury: {recent_nlpi_serious}")

    # ---- Step 9: Per-intersection rate comparison ----
    print("\n\n--- Step 9: Per-intersection collision rates ---")
    # Recent years only (2020-2025) for fairest comparison
    lpi_rate = len(recent_lpi) / len(lpi_intkeys) if lpi_intkeys else 0
    non_lpi_rate = len(recent_non_lpi) / len(non_lpi_intkeys) if non_lpi_intkeys else 0
    print(f"  2020-2025 ped collisions per intersection:")
    print(f"    LPI intersections ({len(lpi_intkeys)}): {lpi_rate:.2f} collisions/intersection")
    print(f"    Non-LPI signalized ({len(non_lpi_intkeys)}): {non_lpi_rate:.2f} collisions/intersection")

    lpi_person_rate = len(recent_lpi_persons) / len(lpi_intkeys) if lpi_intkeys else 0
    non_lpi_person_rate = len(recent_non_lpi_persons) / len(non_lpi_intkeys) if non_lpi_intkeys else 0
    print(f"\n  2020-2025 peds crossing with signal per intersection:")
    print(f"    LPI intersections: {lpi_person_rate:.2f} per intersection")
    print(f"    Non-LPI signalized: {non_lpi_person_rate:.2f} per intersection")

    print("\n  NOTE: LPIs are deployed at high-volume, high-conflict intersections first.")
    print("  Higher per-intersection rates at LPI locations likely reflect selection bias,")
    print("  not LPI ineffectiveness. The key finding is that crashes PERSIST at these")
    print("  intersections despite LPI treatment.")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
