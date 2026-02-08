---
name: seattle-open-data
description: Query Seattle's open data APIs for transportation, collision, and pedestrian data. Use when fetching SDOT data, building charts from city datasets, or working with Seattle's ArcGIS or Socrata portals.
user-invocable: false
---

# Querying Seattle Open Data

Seattle publishes data through two systems. Understanding which to use avoids dead ends.

## Socrata (`data.seattle.gov`) — discovery only for geo datasets

The catalog/search frontend. Transportation datasets here are **federated** (linked from ArcGIS) and **cannot be queried** through the Socrata API. Calling `/resource/{id}.json` on a federated dataset returns `"no row or column access to non-tabular tables"`.

Use Socrata search only to discover dataset IDs and names:
```
GET https://data.seattle.gov/api/search/views.json?q=<term>&limit=20
```
Check `displayType` in results — `"federated"` means query via ArcGIS instead.

Socrata API docs: https://dev.socrata.com/

## ArcGIS (`services.arcgis.com`) — where data actually lives

Seattle's org ID: `ZOyb2t4B0UYuYNYH`

Query pattern:
```
GET https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/{SERVICE}/FeatureServer/{LAYER}/query?{params}
```

Key parameters: `where`, `outFields`, `f=json`, `resultRecordCount`, `resultOffset`, `orderByFields`, `returnCountOnly`.

**Pagination is required** — max ~2000 records per request. Loop with `resultOffset` until returned features < `resultRecordCount`.

**CORS is fully open** (`Access-Control-Allow-Origin: *`) — works from browser JS with no proxy.

ArcGIS REST API docs: https://developers.arcgis.com/rest/services-reference/enterprise/query-feature-service-layer/

Seattle GIS catalog (browse datasets): https://data-seattlecitygis.opendata.arcgis.com/

## SDOT Collisions All Years — the main collision dataset

The working endpoint (updated weekly, ~220k+ records total):
```
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_All_Years/FeatureServer/0/query
```

Catalog page: https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::sdot-collisions-all-years

To discover all fields, query with `outFields=*&resultRecordCount=1`.

### Critical gotcha: date vs time fields

- `INCDATE` — epoch ms but **date only** (always midnight UTC). Use for year/month/day grouping.
- `INCDTTM` — string like `"10/27/2016 8:19:00 PM"`. **This has the actual time.** Parse it for time-of-day analysis.

### Common filters

- Pedestrian collisions: `where=PEDCOUNT>=1`
- Cyclist collisions: `where=PEDCYLCOUNT>=1`
- Fatal collisions: `where=FATALITIES>=1`

### Key fields in SDOT_Collisions_All_Years

| Field | Type | Notes |
|---|---|---|
| `COLDETKEY` | Integer | Primary key. Joins to Persons/Vehicles tables. |
| `REPORTNO` | String | SPD report number. Also joins to Persons/Vehicles. |
| `INTKEY` | Integer | Intersection key. Joins to signal/LPI datasets. **Null for mid-block collisions (~33% of ped records).** |
| `INCDATE` | Date (epoch ms) | Date only (midnight UTC). Use for year/month grouping. |
| `INCDTTM` | String | Full datetime as `"10/27/2016 8:19:00 PM"`. Parse for time-of-day. |
| `PEDCOUNT` | Integer | Number of pedestrians involved. Filter `PEDCOUNT>=1` for ped collisions. |
| `PEDCYLCOUNT` | Integer | Number of cyclists involved. |
| `SEVERITYCODE` | String | `"1"` (property damage) through `"3"` (fatality). |
| `FATALITIES` | Integer | Number of fatalities in collision. |
| `SERIOUSINJURIES` | Integer | Number of serious injuries. |
| `INJURIES` | Integer | Number of other injuries. |
| `ST_COLCODE` | Integer | State collision type. For ped collisions: `0`=vehicle straight, `1`=right turn, `2`=left turn, `3`=backing, `4`=all other. |
| `ST_COLDESC` | String | Description of `ST_COLCODE`. |
| `PEDROWNOTGRNT` | String | `"Y"` = pedestrian did NOT have right of way. Null = ped had ROW or unknown. |

### Related services (same query pattern, same org ID)

- `SDOT_Collisions_Persons` — per-person detail (age, role, injury, actions)
- `SDOT_Collisions_Vehicles` — per-vehicle detail

## SDOT Collisions Persons — per-person detail

```
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/SDOT_Collisions_Persons/FeatureServer/0/query
```

Joins to main collision table via `COLDETKEY` (or `REPORTNO`). One row per person per collision.

### Key fields for pedestrian analysis

| Field | Type | Notes |
|---|---|---|
| `COLDETKEY` | Integer | Foreign key to Collisions table. |
| `REPORTNO` | String | SPD report number. |
| `ST_PARTCPNT_TYPE` | String | `"07"` or `"7"` = Pedestrian. Filter on this first. |
| `ST_PED_ACT_CD` | String | Pedestrian action. `"1"`=crossing with signal, `"2"`=crossing against signal, `"3"`=crossing no signal, `"6"`=crossing non-intersection no crosswalk. |
| `ST_PED_ACT_DESC` | String | Description of above. |
| `ST_PED_WAS_USING_CD` | String | `"4"`=marked crosswalk, `"5"`=unmarked crosswalk. |
| `ST_INJRY_CLSS` | String | Injury class. `"2"/"3"/"4"`=fatal, `"5"`=serious, `"6"`=evident, `"7"`=possible. |
| `ST_INJRY_CLSS_DESC` | String | Description of above. |
| `ST_CONTRBCIR_CD1` | String | Primary contributing circumstance code. |
| `ST_CONTRBCIR1_DESC` | String | Description of above. |
| `INCDATE` | Date (epoch ms) | Collision date (duplicated from main table). |
| `ST_AGE` | Integer | Person's age. |
| `ST_GENDER` | Integer | `1`=Male, `2`=Female. |

**Important:** The Persons table does NOT have `INTKEY`. To link persons to intersections, join Persons → Collisions via `COLDETKEY`, then use `INTKEY` from the Collisions table.

### Common pedestrian filters

```
# All pedestrian person-records
where=ST_PARTCPNT_TYPE IN ('07','7')

# Pedestrians crossing with signal (had walk phase)
where=ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1'

# Pedestrians in marked crosswalk with signal
where=ST_PARTCPNT_TYPE IN ('07','7') AND ST_PED_ACT_CD='1' AND ST_PED_WAS_USING_CD='4'
```

### Statistical queries (groupBy)

Use `outStatistics` with `groupByFieldsForStatistics` for aggregate counts without downloading all records:

```
outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]
groupByFieldsForStatistics=ST_PED_ACT_CD,ST_PED_ACT_DESC
orderByFields=cnt DESC
```

**Gotcha:** Some fields return `null` instead of their coded value. Always use `str(r.get("FIELD") or "fallback")` when formatting output.

## Vision Zero Signals LPI/NTOR — LPI intersection inventory

```
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Vision_Zero_Signals_LPI_NTOR/FeatureServer/0/query
```

Catalog/map: https://experience.arcgis.com/experience/26fc62bba1a942f1bfbc0f0ef4d9458e/

All 1,240 signalized intersections in Seattle, with LPI and No Turn on Red status. Snapshot as of January 2024 (manual refresh cycle).

### Key fields

| Field | Type | Notes |
|---|---|---|
| `INTKEY` | Integer | Intersection key. **Joins to SDOT_Collisions_All_Years.** |
| `UNITID` | String | Signal unit ID (e.g., `"SGL-278"`). |
| `UNITDESC` | String | Intersection description (e.g., `"GREENWOOD AVE N AND N 80TH ST"`). |
| `LPI_Status` | String | `"Ex"` = LPI installed. Null/empty = no LPI. |
| `LPI_Approach` | String | `"All"` = LPI on all approaches. `"Partial"` = some approaches. |
| `NTOR_Status` | String | `"Ex"` = No Turn on Red installed. |
| `NTOR_Approach` | String | `"All"` or `"Partial"`. |

### Counts (Jan 2024 snapshot)

- Total signals: 1,240
- With LPI: ~642 (query `LPI_Status='Ex'` — exact count depends on nulls in INTKEY)
- Without LPI: ~506
- With No Turn on Red: ~166

### Common queries

```
# All LPI intersections (get INTKEYs for joining to collisions)
where=LPI_Status='Ex'&outFields=INTKEY,UNITDESC,LPI_Approach

# All signals (to build full LPI/non-LPI classification)
where=1=1&outFields=INTKEY,LPI_Status,LPI_Approach,NTOR_Status

# Total fits in one request (1,240 < 2,000 limit) — no pagination needed
```

### Related service

- `Traffic_Signal_Assemblies_NO_LPI` (FeatureServer/42) — signals without LPI only (June 2024 snapshot, 420 records). More recent but subset only.

## Joining collision data to LPI inventory

The three-table join path:

```
SDOT_Collisions_Persons.COLDETKEY
  → SDOT_Collisions_All_Years.COLDETKEY  (gets INTKEY)
    → Vision_Zero_Signals_LPI_NTOR.INTKEY  (gets LPI_Status)
```

**Steps in Python:**
1. Fetch all LPI records, build set of LPI INTKEYs and non-LPI INTKEYs
2. Fetch all pedestrian collisions (`PEDCOUNT>=1`), build `COLDETKEY → collision` dict
3. Fetch pedestrian person records (e.g., `ST_PED_ACT_CD='1'`), look up each person's `COLDETKEY` in the collision dict to get `INTKEY`, then check LPI set membership

**Gotcha:** ~33% of pedestrian collisions have null `INTKEY` (mid-block crashes, unmatched locations). These cannot be joined to the LPI inventory.

## Gotchas learned the hard way

1. **`gisdata.seattle.gov` is unreliable.** Services there may be stopped ("Service not started" error). Always use `services.arcgis.com` endpoint.
2. **URL-encode `where` clauses.** `>=` must be `%3E%3D`, or use `URLSearchParams` in JS / `--data-urlencode` with curl.
3. **Socrata catalog search needs the `domains` parameter** to limit to Seattle, otherwise you get NYC/SF/etc results. But even then, federated datasets may not appear — use `api/search/views.json` over `api/catalog/v1`.
4. **curl piping to Python fails for large ArcGIS responses.** Use Python's `urllib.request` directly instead of `curl | python3`. The response can exceed pipe buffer limits, and curl's `--data-urlencode` can also mismatch with ArcGIS expectations.
5. **ArcGIS null handling.** Fields can return `None` even for coded-value fields. Always use `str(r.get("FIELD") or "fallback")` rather than `.get("FIELD", "default")` — the latter doesn't catch explicit `None` values, only missing keys.
6. **ST_PARTCPNT_TYPE values vary.** Pedestrians appear as both `"07"` and `"7"`. Always filter with `IN ('07','7')`.
7. **Persons table has no INTKEY.** You must join through the Collisions table via `COLDETKEY`.
8. **LPI dataset service name is not obvious.** It's `Vision_Zero_Signals_LPI_NTOR`, not listed under any "LPI" or "Leading_Pedestrian" prefix. The base `Traffic_Signal_Assemblies` layers do NOT contain LPI status — that data is maintained in a separate Vision Zero spreadsheet joined to the signal data.
9. **Statistical queries (outStatistics) return max 100 groups by default.** Set `resultRecordCount=100` or higher to ensure all groups are returned.
