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

### Related services (same query pattern, same org ID)

- `SDOT_Collisions_Persons` — per-person detail (age, role)
- `SDOT_Collisions_Vehicles` — per-vehicle detail

## SDOT Intersection Signals — LPI, NTOR, and signal inventory

A ready-made CLI script is included in this skill folder:

```bash
python3 .claude/skills/seattle-open-data/sdot_intersection_signals.py --action lpi_summary
python3 .claude/skills/seattle-open-data/sdot_intersection_signals.py --action lpi_list
python3 .claude/skills/seattle-open-data/sdot_intersection_signals.py --action ntor_list
python3 .claude/skills/seattle-open-data/sdot_intersection_signals.py --action recent_installs --years 5
python3 .claude/skills/seattle-open-data/sdot_intersection_signals.py --action signal_details --unit-id SGL-1207
python3 .claude/skills/seattle-open-data/sdot_intersection_signals.py --action search --street RAINIER
```

It uses only stdlib (`urllib`), handles ArcGIS pagination, and exposes reusable helpers (`query_arcgis`, `query_all_features`, `count_features`, `epoch_ms_to_date`).

Three FeatureServer layers cover intersection signal changes. All use Seattle's org ID.

### Vision_Zero_Signals_LPI_NTOR — LPI and No-Turn-On-Red status

```
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Vision_Zero_Signals_LPI_NTOR/FeatureServer/0/query
```

~1,240 records (one per signalised intersection). Geometry: `esriGeometryMultipoint`.

**Key fields:**

| Field | Type | Description |
|---|---|---|
| `UNITID` | string | Signal ID (e.g. `SGL-278`) |
| `UNITDESC` | string | Cross-street description (padded with spaces — `.strip()` it) |
| `Location` | string | Clean cross-street name |
| `LPI_Status` | string | `"Ex"` = LPI exists, `""` or `"None"` = no LPI |
| `LPI_Approach` | string | `"All"` or `"Partial"` — which approaches have LPI |
| `NTOR_Status` | string | `"Ex"` = No-Turn-On-Red exists |
| `NTOR_Approach` | string | `"All"` or `"Partial"` |
| `SIGNAL_TYPE` | string | `"FULL"`, `"SEMI"`, `"PRE"` |
| `INSTALL_DATE` | date (epoch ms) | Signal installation date (often null in this layer) |
| `CURRENT_STATUS` | string | e.g. `"INSVC"` |
| `INTKEY` | integer | Intersection key (join to other datasets) |

**Common filters:**
- Signals with LPI: `where=LPI_Status='Ex'`
- Signals with NTOR: `where=NTOR_Status='Ex'`
- Both: `where=LPI_Status='Ex' AND NTOR_Status='Ex'`
- Street search: `where=Location LIKE '%RAINIER%'`

### Traffic_Signal_Assemblies_(Active) — full signal inventory with dates

```
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Traffic_Signal_Assemblies_(Active)/FeatureServer/0/query
```

The detailed signal assembly inventory. Same geometry. This layer has **install and modification dates** for specific signal components — the best source for "when did this change happen at an intersection."

**Date fields (all epoch ms):**

| Field | What it tracks |
|---|---|
| `INSTALL_DATE` | Signal assembly installation |
| `PEDHDFIRSTINSTALLDT` | First pedestrian signal head installed |
| `PEDAUDIOINSTALLDT` | Accessible pedestrian audio device installed |
| `PEDPSHINSTALLDT` | Pedestrian push button installed |
| `LTFIRSTINSTALLDT` | Left-turn signal phase first installed |
| `LTREMOVEDT` | Left-turn signal phase removed |
| `RTFIRSTINSTALLDT` | Right-turn signal phase first installed |
| `RTREMOVEDT` | Right-turn signal phase removed |
| `MMUINSTALLDT` | Malfunction management unit installed |
| `LASTSIGNALOPTDT` | Last signal optimization |
| `CABLASTPMDT` | Last cabinet preventive maintenance |
| `CURRENT_STATUS_DATE` | Last status change |
| `CONDITION_ASSESSMENT_DATE` | Last condition assessment |
| `ADDDTTM` / `MODDTTM` | Record add/modify timestamps |

**Other notable fields:** `BIKESIGNALHDYN` (bike signal head Y/N), `PEDAUDIODEVICEYN`, `PEDSIGNALYN`, `HALFSIGNALYN`, `METEREDYN`, `DETDEVSTOPBARYN` (detection device at stop bar), `DETDEVADVANCEDYN`, `CO_MODELTYPE` (controller model), `CO_SERIALNBR`, `CO_SOFTWRREV` (controller software revision).

### Traffic_Signal_Assemblies_NO_LPI — signals lacking LPI

```
https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Traffic_Signal_Assemblies_NO_LPI/FeatureServer/0/query
```

Filtered view of signals that do **not** have LPI. Useful for gap analysis.

### Other intersection-adjacent datasets

| Service name | What it covers |
|---|---|
| `SDOT_Intersections` | Base intersection geometry and attributes |
| `Bicycle_and_Pedestrian_Safety_Analysis_Intersections` | Safety analysis scores per intersection |
| `Accessible_Pedestrian_Signals_(Active)` | APS device inventory |
| `Traffic_Circles_view` | Neighborhood traffic circles |
| `Traffic_Operations` | General traffic operations data |
| `Curb_Ramps_(Active)` | Curb ramp inventory |

### Discovering datasets via ArcGIS portal search

Search Seattle's ArcGIS org for any topic:
```python
import urllib.request, urllib.parse, json
q = "SDOT signal"
url = f"https://www.arcgis.com/sharing/rest/search?q={urllib.parse.quote(q)}%20orgid:ZOyb2t4B0UYuYNYH&num=10&f=json"
data = json.loads(urllib.request.urlopen(url).read())
for r in data["results"]:
    print(r["title"], "|", r["type"], "|", r.get("url", ""))
```

## Gotchas learned the hard way

1. **`gisdata.seattle.gov` is unreliable.** Services there may be stopped ("Service not started" error). Always use `services.arcgis.com` endpoint.
2. **URL-encode `where` clauses.** `>=` must be `%3E%3D`, or use `URLSearchParams` in JS / `--data-urlencode` with curl.
3. **Socrata catalog search needs the `domains` parameter** to limit to Seattle, otherwise you get NYC/SF/etc results. But even then, federated datasets may not appear — use `api/search/views.json` over `api/catalog/v1`.
4. **Date comparisons need `DATE` keyword, not epoch ms.** ArcGIS `where` clauses on date fields must use `DATE 'YYYY-MM-DD'` syntax. Using raw epoch milliseconds (e.g. `INSTALL_DATE>=1707407577822`) silently returns 0 results — no error, just empty. Correct: `INSTALL_DATE >= DATE '2024-02-08'`.
5. **`returnDistinctValues=true` doesn't deduplicate** on the LPI/NTOR layer — it returns one row per feature, not distinct values. Use `outStatistics` with `statisticType=count` and `groupByFieldsForStatistics` instead for value distributions.
6. **UNITDESC is space-padded** to ~256 chars. Always `.strip()` it. The `Location` field in the LPI/NTOR layer is the clean version.
7. **LPI_Status values:** `"Ex"` (exists), `""` (empty string = no LPI), or `"None"` (string literal "None" = no LPI). Filter with `LPI_Status='Ex'` to get signals that have it.
