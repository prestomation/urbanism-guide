---
title: "How to Query Seattle's Pedestrian Collision Data"
date: 2026-02-07
draft: false
tags: ["data", "sdot", "open-data", "tutorial"]
categories: ["data"]
summary: "A technical guide to querying SDOT's collision, person-level, and signal inventory datasets through Seattle's ArcGIS REST API. Covers endpoints, field references, join paths, and working code examples."
---

# How to Query Seattle's Pedestrian Collision Data

Seattle publishes collision data through three related datasets on its ArcGIS portal. This post documents the endpoints, key fields, query patterns, and join paths needed to analyze pedestrian crashes at signalized intersections. All data is public and requires no API key.

## The three datasets

| Dataset | Records | What it contains |
|---|---|---|
| [SDOT Collisions All Years](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::sdot-collisions-all-years) | ~220,000+ total | One row per collision. Severity, location, vehicle action, date. |
| SDOT Collisions Persons | ~500,000+ total | One row per person per collision. Injury class, pedestrian action, contributing circumstances. |
| [Vision Zero Signals LPI/NTOR](https://experience.arcgis.com/experience/26fc62bba1a942f1bfbc0f0ef4d9458e/) | 1,240 | One row per signalized intersection. LPI and No Turn on Red status. |

All three are hosted on Seattle's ArcGIS organization (`ZOyb2t4B0UYuYNYH`) and queried through the same REST API pattern.

## Endpoints

```
# Collisions (main table)
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_All_Years/FeatureServer/0/query

# Persons (per-person detail)
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_Persons/FeatureServer/0/query

# Signal inventory with LPI status
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Vision_Zero_Signals_LPI_NTOR/FeatureServer/0/query
```

## Query basics

All endpoints accept the same parameters:

| Parameter | Description |
|---|---|
| `where` | SQL-style filter (e.g., `PEDCOUNT>=1`). Required — use `1=1` for all records. |
| `outFields` | Comma-separated field names, or `*` for all. |
| `f` | Response format. Use `json`. Also supports `geojson`. |
| `resultRecordCount` | Max records per request. Server limit is 2,000. |
| `resultOffset` | Starting record for pagination. |
| `returnCountOnly` | Set to `true` to get just the count. |
| `orderByFields` | Sort order (e.g., `INCDATE DESC`). |
| `outStatistics` | JSON array for aggregate queries (see below). |
| `groupByFieldsForStatistics` | Group-by fields for aggregate queries. |

### Pagination

The server returns a maximum of 2,000 records per request. To get all matching records, loop with `resultOffset`:

```python
import json, urllib.request, urllib.parse

def paginated_query(base_url, where, out_fields, max_records=2000):
    all_records = []
    offset = 0
    while True:
        params = urllib.parse.urlencode({
            "where": where,
            "outFields": out_fields,
            "resultRecordCount": max_records,
            "resultOffset": offset,
            "f": "json"
        }, quote_via=urllib.parse.quote)
        req = urllib.request.Request(
            base_url + "?" + params,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        batch = [f["attributes"] for f in data.get("features", [])]
        all_records.extend(batch)
        if len(batch) < max_records:
            break
        offset += max_records
    return all_records
```

The LPI/signal inventory (1,240 records) fits in a single request. The Collisions and Persons tables require pagination for most queries.

### Aggregate queries

To get counts by group without downloading all records, use `outStatistics`:

```python
import json

params = {
    "where": "PEDCOUNT>=1",
    "outStatistics": json.dumps([{
        "statisticType": "count",
        "onStatisticField": "OBJECTID",
        "outStatisticFieldName": "cnt"
    }]),
    "groupByFieldsForStatistics": "ST_COLCODE,ST_COLDESC",
    "orderByFields": "cnt DESC",
    "f": "json"
}
```

This returns one row per group with the count, without transferring individual records.

## Collisions table: key fields

The Collisions table (`SDOT_Collisions_All_Years`) has one row per collision event.

### Identifiers and joins

| Field | Type | Description |
|---|---|---|
| `COLDETKEY` | Integer | Primary key. Joins to Persons and Vehicles tables. |
| `REPORTNO` | String | SPD report number. Alternative join key. |
| `INTKEY` | Integer | Intersection key. Joins to the signal/LPI inventory. Null for mid-block collisions. |

### Date fields

| Field | Type | Description |
|---|---|---|
| `INCDATE` | Date (epoch ms) | Date only — always midnight UTC. Use for year/month grouping. |
| `INCDTTM` | String | Full datetime as `"10/27/2016 8:19:00 PM"`. Parse this for time-of-day analysis. |

To convert `INCDATE` to a year in Python:

```python
import datetime
def epoch_to_year(epoch_ms):
    return datetime.datetime.utcfromtimestamp(epoch_ms / 1000).year
```

### Pedestrian-specific fields

| Field | Type | Values |
|---|---|---|
| `PEDCOUNT` | Integer | Number of pedestrians involved. Filter `PEDCOUNT>=1` for pedestrian collisions. |
| `PEDROWNOTGRNT` | String | `"Y"` = pedestrian did NOT have right of way. Null = pedestrian had ROW or field not recorded. |
| `PEDCYLCOUNT` | Integer | Number of cyclists involved. |

### Severity fields

| Field | Type | Description |
|---|---|---|
| `SEVERITYCODE` | String | `"1"` = property damage only, `"2b"` = injury, `"2"` = serious injury, `"3"` = fatality. |
| `SEVERITYDESC` | String | Text description. |
| `FATALITIES` | Integer | Count of fatalities. |
| `SERIOUSINJURIES` | Integer | Count of serious injuries. |
| `INJURIES` | Integer | Count of other injuries. |

### Collision type (vehicle action)

| Field | Type | Description |
|---|---|---|
| `ST_COLCODE` | Integer | State collision type code. |
| `ST_COLDESC` | String | Description. |

For pedestrian collisions, the relevant `ST_COLCODE` values are:

| Code | Description |
|---|---|
| `0` | Vehicle going straight hits pedestrian |
| `1` | Vehicle turning right hits pedestrian |
| `2` | Vehicle turning left hits pedestrian |
| `3` | Vehicle backing hits pedestrian |
| `4` | Vehicle hits pedestrian — all other actions |

### Common filters

```sql
-- All pedestrian collisions
PEDCOUNT>=1

-- Fatal pedestrian collisions
PEDCOUNT>=1 AND FATALITIES>=1

-- Pedestrian collisions at signalized intersections (has INTKEY)
PEDCOUNT>=1 AND INTKEY IS NOT NULL

-- Pedestrian collisions in a specific year
PEDCOUNT>=1 AND INCDATE >= DATE '2024-01-01' AND INCDATE < DATE '2025-01-01'
```

## Persons table: key fields

The Persons table (`SDOT_Collisions_Persons`) has one row per person per collision. This is where pedestrian action, injury severity, and contributing circumstances live.

### Identifiers

| Field | Type | Description |
|---|---|---|
| `COLDETKEY` | Integer | Foreign key to Collisions table. |
| `REPORTNO` | String | SPD report number. |
| `COLLISIONPSNDETKEY` | Integer | Primary key for this table. |

### Person type

| Field | Type | Values |
|---|---|---|
| `ST_PARTCPNT_TYPE` | String | `"07"` or `"7"` = Pedestrian. `"01"` = Driver. `"06"` = Cyclist. |
| `ST_PARTCPNT_TYPE_DESC` | String | Text description. |

Both `"07"` and `"7"` appear in the data for pedestrians. Always filter with `IN ('07','7')`.

### Pedestrian action

| Field | Type | Description |
|---|---|---|
| `ST_PED_ACT_CD` | String | What the pedestrian was doing at time of collision. |
| `ST_PED_ACT_DESC` | String | Text description. |

Key values:

| Code | Description | Typical share |
|---|---|---|
| `1` | Crossing at intersection with signal | ~35% |
| `2` | Crossing at intersection against signal | ~7% |
| `3` | Crossing at intersection — no signal | ~18% |
| `4` | Crossing at intersection — diagonally | ~1% |
| `5` | From behind parked vehicle | ~3% |
| `6` | Crossing non-intersection — no crosswalk | ~11% |
| `7` | Crossing non-intersection — in crosswalk | ~2% |

### Pedestrian facility

| Field | Type | Description |
|---|---|---|
| `ST_PED_WAS_USING_CD` | String | Type of facility the pedestrian was using. |
| `ST_PED_WAS_USING_DESC` | String | Text description. |

| Code | Description |
|---|---|
| `4` | Marked crosswalk |
| `5` | Unmarked crosswalk |

### Injury severity

| Field | Type | Description |
|---|---|---|
| `ST_INJRY_CLSS` | String | Injury classification code. |
| `ST_INJRY_CLSS_DESC` | String | Text description. |

| Code | Description |
|---|---|
| `1` | No injury |
| `2` | Dead at scene |
| `3` | Dead on arrival |
| `4` | Died at hospital |
| `5` | Serious injury |
| `6` | Non-serious evident injury |
| `7` | Possible injury |

### Contributing circumstances

| Field | Type | Description |
|---|---|---|
| `ST_CONTRBCIR_CD1` | String | Primary contributing circumstance code. |
| `ST_CONTRBCIR1_DESC` | String | Text description. |

The field records circumstances for the person in that row — not necessarily the other party. For pedestrians crossing with the signal, the most common value is `"18"` / `"None"` (~85% of records).

### Demographics

| Field | Type | Description |
|---|---|---|
| `ST_AGE` | Integer | Person's age. |
| `ST_GENDER` | Integer | `1` = Male, `2` = Female. |

## LPI signal inventory: key fields

The Vision Zero Signals LPI/NTOR dataset contains all 1,240 signalized intersections in Seattle with their LPI and No Turn on Red status.

| Field | Type | Description |
|---|---|---|
| `INTKEY` | Integer | Intersection key. Joins to Collisions table. |
| `UNITID` | String | Signal unit ID (e.g., `"SGL-278"`). |
| `UNITDESC` | String | Intersection name (e.g., `"GREENWOOD AVE N AND N 80TH ST"`). |
| `LPI_Status` | String | `"Ex"` = LPI installed. Null or empty = no LPI. |
| `LPI_Approach` | String | `"All"` = all approaches. `"Partial"` = some approaches. |
| `NTOR_Status` | String | `"Ex"` = No Turn on Red installed. |
| `NTOR_Approach` | String | `"All"` or `"Partial"`. |

This is a snapshot as of January 2024. It does not include LPI installation dates.

## Joining the tables

The three tables connect through two keys:

```
Persons.COLDETKEY  →  Collisions.COLDETKEY  (gets INTKEY, severity, collision type)
Collisions.INTKEY  →  LPI_NTOR.INTKEY       (gets LPI_Status)
```

### Example: count pedestrians crossing with signal at LPI intersections

```python
# 1. Get all LPI INTKEYs
lpi_records = paginated_query(
    LPI_URL, "1=1",
    "INTKEY,LPI_Status"
)
lpi_intkeys = {
    r["INTKEY"] for r in lpi_records
    if r.get("LPI_Status") == "Ex" and r.get("INTKEY") is not None
}

# 2. Get all pedestrian collisions with INTKEY
ped_collisions = paginated_query(
    COLLISIONS_URL, "PEDCOUNT>=1",
    "COLDETKEY,INTKEY"
)
collision_by_coldetkey = {
    c["COLDETKEY"]: c for c in ped_collisions
    if c.get("COLDETKEY") is not None
}

# 3. Get pedestrian person records (crossing with signal)
ped_persons = paginated_query(
    PERSONS_URL,
    "ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1'",
    "COLDETKEY,ST_INJRY_CLSS"
)

# 4. Join and count
at_lpi = 0
for p in ped_persons:
    collision = collision_by_coldetkey.get(p.get("COLDETKEY"))
    if collision and collision.get("INTKEY") in lpi_intkeys:
        at_lpi += 1

print(f"Pedestrians crossing with signal at LPI intersections: {at_lpi}")
```

### Join coverage

Not all records join successfully:

- ~33% of pedestrian collisions have no `INTKEY` (mid-block crashes or unmatched locations). These cannot be linked to the signal inventory.
- Some LPI records have null `INTKEY` values.
- Person records occasionally have no matching `COLDETKEY` in the Collisions table.

## Known issues

1. **Date fields are epoch milliseconds in UTC.** `INCDATE` is date-only (always midnight). For time-of-day, parse the `INCDTTM` string field.

2. **Null handling.** ArcGIS returns explicit `null` for empty fields. Python's `.get("field", "default")` does not catch these — it only handles missing keys. Use `r.get("field") or "fallback"` instead.

3. **Participant type inconsistency.** Pedestrians appear as both `"07"` and `"7"` in `ST_PARTCPNT_TYPE`. Always use `IN ('07','7')`.

4. **curl piping can fail.** Large ArcGIS JSON responses can exceed pipe buffer limits when piping `curl` output to `python3`. Use Python's `urllib.request` directly.

5. **URL encoding matters.** Operators like `>=` must be URL-encoded (`%3E%3D`). In Python, use `urllib.parse.urlencode` with `quote_via=urllib.parse.quote`. With curl, use `--data-urlencode`.

6. **Service name discoverability.** The LPI dataset is named `Vision_Zero_Signals_LPI_NTOR` — it does not appear under a "Leading Pedestrian Interval" search. The base `Traffic_Signal_Assemblies` layers do not contain LPI status.

7. **LPI data is a snapshot.** The inventory reflects current installations as of its last refresh date (January 2024 as of this writing). There are no installation dates in the public dataset. Collisions from earlier years at "LPI intersections" may have occurred before the LPI was active.

## Data dictionary

To discover all fields for any dataset, query with `outFields=*&resultRecordCount=1`:

```
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_All_Years/FeatureServer/0/query?where=1=1&outFields=*&resultRecordCount=1&f=json
```

The response includes a `fields` array with name, type, alias, and domain for every field. The `features` array contains one sample record.

## Related resources

- [Seattle GIS Data Portal](https://data-seattlecitygis.opendata.arcgis.com/) -- browse and preview all datasets
- [SDOT Vision Zero](https://www.seattle.gov/transportation/projects-and-programs/safety-first/vision-zero) -- program context and maps
- [ArcGIS REST API reference](https://developers.arcgis.com/rest/services-reference/enterprise/query-feature-service-layer/) -- full query parameter documentation

---

*Last updated: February 2026*
