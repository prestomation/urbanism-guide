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

## Gotchas learned the hard way

1. **`gisdata.seattle.gov` is unreliable.** Services there may be stopped ("Service not started" error). Always use `services.arcgis.com` endpoint.
2. **URL-encode `where` clauses.** `>=` must be `%3E%3D`, or use `URLSearchParams` in JS / `--data-urlencode` with curl.
3. **Socrata catalog search needs the `domains` parameter** to limit to Seattle, otherwise you get NYC/SF/etc results. But even then, federated datasets may not appear — use `api/search/views.json` over `api/catalog/v1`.
