---
title: "Doing Everything Right and Still Getting Hit: Seattle's Crosswalk Safety Data"
date: 2026-02-07
draft: false
tags: ["vision-zero", "pedestrian-safety", "data-analysis", "sdot"]
categories: ["analysis"]
summary: "SDOT collision data shows 3,550 pedestrians were struck while crossing with a walk signal -- the largest single category of pedestrian crashes in Seattle. Turning vehicles are the primary conflict, and Leading Pedestrian Intervals alone can't eliminate it."
---

# Doing Everything Right and Still Getting Hit

Seattle has invested heavily in [Leading Pedestrian Intervals]({{< relref "/glossary/transportation#leading-pedestrian-interval-lpi" >}}) (LPIs) as a core [Vision Zero]({{< relref "/glossary/transportation#vision-zero" >}}) tool. By 2024, LPIs were active at over 700 signalized intersections -- nearly three-quarters of traffic signals citywide. SDOT's own evaluation found LPIs reduced turning collisions involving pedestrians by [48% at treated intersections](https://sdotblog.seattle.gov/2018/12/06/leading-pedestrian-intervals-every-second-counts/).

But a 48% reduction is not elimination. What happens to the other half?

We analyzed the full [SDOT Collisions dataset](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::sdot-collisions-all-years) (2006-2025) to understand how many pedestrians are struck while doing everything the system asks of them: crossing at a signalized intersection, during the walk phase, in a marked crosswalk.

## The numbers

Across all years in the dataset, **9,921 collisions** involved at least one pedestrian. Using the per-person detail records (SDOT Collisions Persons), the single largest category of pedestrian crash circumstances is:

| Pedestrian action | Count | Share |
|---|---|---|
| **Crossing at intersection with signal** | **3,550** | **35.3%** |
| Crossing at intersection, no signal | 1,797 | 17.9% |
| Crossing non-intersection, no crosswalk | 1,056 | 10.5% |
| Crossing at intersection against signal | 749 | 7.5% |
| All other actions | 2,900 | 28.8% |

More than one in three pedestrians struck in Seattle was **crossing at a signalized intersection during the walk phase**.

Of those 3,550, **82% were in a marked crosswalk** (2,925 people). And 85% had "None" listed as their contributing circumstance -- meaning the data records no fault on the pedestrian's part.

## Severity: these aren't fender-benders

Among the 2,925 pedestrians hit in a marked crosswalk while crossing with the signal:

| Injury severity | Count | Share |
|---|---|---|
| Possible injury | 1,329 | 45.4% |
| Evident (non-serious) injury | 1,006 | 34.4% |
| **Serious injury** | **256** | **8.8%** |
| **Fatal** | **27** | **0.9%** |
| No injury | 192 | 6.6% |
| Unknown | 114 | 3.9% |

**283 people** -- roughly one in ten -- suffered fatal or serious injuries while walking in a marked crosswalk with the walk signal. These are people who followed every rule the transportation system set for them.

## Turning vehicles are the core conflict

Across all pedestrian collisions, the vehicle action breaks down as:

| Vehicle action | Count | Share |
|---|---|---|
| Going straight | 4,433 | 44.7% |
| **Turning left** | **2,908** | **29.3%** |
| **Turning right** | **1,559** | **15.7%** |
| Backing | 298 | 3.0% |
| All other | 723 | 7.3% |

**45% of all pedestrian collisions involve turning vehicles.** This is the specific conflict that LPIs are designed to address -- by giving pedestrians a 3-7 second head start, they become visible in the crosswalk before drivers begin their turn.

But LPIs don't eliminate the conflict. After the head start expires, vehicles turn through the crosswalk on a concurrent green while pedestrians are still crossing. A driver who is focused on finding a gap in oncoming traffic before turning left may not see a pedestrian already in the crosswalk.

## What happens at LPI intersections specifically?

The analysis above uses collision records alone, which don't record signal phasing type. But SDOT publishes a separate dataset -- [Vision Zero Signals LPI/NTOR](https://experience.arcgis.com/experience/26fc62bba1a942f1bfbc0f0ef4d9458e/) -- that identifies which of Seattle's 1,240 signalized intersections have LPIs installed. As of the January 2024 snapshot, **642 intersections have LPIs** and 506 do not.

By joining collision locations to this inventory using the shared `INTKEY` intersection identifier, we can see what's happening at LPI intersections directly.

### Pedestrians hit while crossing with signal: LPI vs. non-LPI

| | LPI intersections (642) | Non-LPI signalized (506) |
|---|---|---|
| Peds hit crossing with signal | **2,462** | 774 |
| Fatal | 21 (0.9%) | 7 (0.9%) |
| Serious injury | 225 (9.1%) | 62 (8.0%) |
| **Fatal + serious** | **246 (10.0%)** | 69 (8.9%) |
| In marked crosswalk | 2,056 (83.5%) | 645 (83.3%) |

**2,462 pedestrians were struck while crossing with the walk signal at intersections that have LPIs.** Of those, 246 suffered fatal or serious injuries. The fatality rate (0.9%) and serious injury rate (9.1%) are comparable to non-LPI signalized intersections.

The higher absolute numbers at LPI intersections reflect selection bias: SDOT installs LPIs at the busiest, highest-conflict intersections first. Per-intersection rates confirm this -- LPI locations average 3.8 pedestrians hit while crossing with the signal per intersection vs. 1.5 at non-LPI locations. But the critical finding is not the rate comparison. It's that **crashes persist at LPI intersections at scale**.

### Turning vehicles dominate at LPI intersections

At LPI intersections, the collision type breakdown for all pedestrian crashes is:

| Vehicle action | LPI intersections | Non-LPI signalized |
|---|---|---|
| Turning left | 1,550 (45.6%) | 529 (45.0%) |
| Turning right | 785 (23.1%) | 250 (21.3%) |
| **Total turning** | **2,335 (68.6%)** | **779 (66.3%)** |
| Going straight | 889 (26.1%) | 335 (28.5%) |

**Nearly 7 in 10 pedestrian crashes at LPI intersections involve turning vehicles** -- the exact conflict LPIs are designed to mitigate. The turning share is virtually identical at LPI and non-LPI intersections, suggesting that while LPIs may reduce the absolute number of turning crashes (consistent with SDOT's 48% reduction finding), they have not changed the fundamental pattern. Turning vehicles remain the dominant threat to pedestrians at signalized intersections with or without an LPI.

### The trend: crashes persist year after year

Seattle began installing LPIs around 2009 and accelerated deployment after adopting Vision Zero in 2015. By [2023, SDOT was adding 100 LPIs per year](https://sdotblog.seattle.gov/2023/08/31/vision-zero-were-accelerating-leading-pedestrian-interval-lpi-signal-rollout-throughout-the-city/). Here is the year-by-year count of pedestrians hit while crossing with the signal, broken down by LPI status of the intersection:

| Year | At LPI intersections | Fatal + serious | At non-LPI | Fatal + serious |
|---|---|---|---|---|
| 2006 | 163 | 19 | 44 | 7 |
| 2007 | 132 | 8 | 41 | 3 |
| 2008 | 114 | 8 | 55 | 4 |
| 2009 | 120 | 12 | 31 | 4 |
| 2010 | 138 | 6 | 48 | 4 |
| 2011 | 102 | 8 | 39 | 1 |
| 2012 | 146 | 19 | 27 | 0 |
| 2013 | 110 | 10 | 24 | 1 |
| 2014 | 141 | 16 | 40 | 1 |
| 2015 | 107 | 7 | 46 | 1 |
| 2016 | 120 | 12 | 43 | 3 |
| 2017 | 135 | 15 | 37 | 6 |
| 2018 | 155 | 11 | 46 | 6 |
| 2019 | 137 | 9 | 48 | 3 |
| 2020 | 65 | 7 | 25 | 0 |
| 2021 | 79 | 11 | 20 | 3 |
| 2022 | 73 | 12 | 20 | 5 |
| 2023 | 69 | 15 | 30 | 5 |
| 2024 | 80 | 9 | 25 | 0 |
| 2025 | 58 | 14 | 19 | 5 |

Total volumes at LPI intersections dropped after 2019, largely due to reduced traffic during and after the pandemic. But fatal and serious injuries have not followed. In 2023, there were 15 fatal or serious injuries at LPI intersections among pedestrians crossing with the signal. In the first portion of 2025, there are already 14.

### Since 2020: the LPI era

By 2020, the majority of Seattle's LPIs were already installed. Looking at just the 2020-2025 period:

- **424 pedestrians** were hit while crossing with the signal at LPI intersections
- **5 were killed** and **63 suffered serious injuries**
- That's 68 fatal or serious injuries in roughly six years -- about one per month -- at intersections that already have the city's primary pedestrian safety treatment installed

## The case for exclusive pedestrian phases

An LPI gives pedestrians a head start. An [exclusive pedestrian phase]({{< relref "/glossary/transportation#diagonal-crossing-pedestrian-scramble" >}}) (also called a pedestrian scramble or Barnes Dance) stops **all** vehicle traffic while pedestrians cross. There is zero conflict between turning vehicles and crossing pedestrians during the walk phase.

The national research supports the distinction:

- **FHWA** classifies LPIs as a [proven safety countermeasure](https://www.seattle.gov/transportation/projects-and-programs/safety-first/vision-zero/leading-pedestrian-intervals) with documented crash reductions, but LPIs only partially separate pedestrian and vehicle movements.
- A New York City study (Chen et al., 2012) found exclusive pedestrian phasing reduced vehicle-pedestrian crashes by **51%** -- a Crash Modification Factor of 0.49.
- A Montreal study found a **43% reduction** in pedestrian crashes at intersections converted to exclusive pedestrian phases.
- A Connecticut study (Zheng et al., 2015) found lower crash severity at exclusive-phase intersections compared to concurrent-phase intersections.

SDOT's own [Seattle Streets Illustrated](https://streetsillustrated.seattle.gov/design-standards/intersections/its/) design standards acknowledge that exclusive phases "improve pedestrian safety" and specify evaluation criteria: high pedestrian volumes, conflicting vehicle turning movements above 250 per hour, and proximity to schools, senior housing, or medical facilities.

## The tradeoff and why it's worth making

Exclusive pedestrian phases add delay. When pedestrians get their own phase, the total signal cycle gets longer, and vehicles wait more. This is the primary reason cities default to concurrent signals with LPIs instead.

But the collision data quantifies the cost of that choice. At Seattle's 642 LPI-equipped intersections, **2,462 pedestrians** were hit while crossing with the signal, and **246** suffered fatal or serious injuries. Since 2020, with most LPIs already deployed, pedestrians crossing legally at LPI intersections have been killed or seriously injured at a rate of about one per month. Turning vehicles cause 69% of all pedestrian crashes at these locations.

At intersections on the [High Injury Network]({{< relref "/glossary/transportation#high-injury-network" >}}) -- particularly along corridors like Rainier Avenue, Aurora Avenue, and MLK Jr Way -- the volume of turning conflicts and the severity of outcomes argue for exclusive phases as a next step beyond LPIs.

Adding 15-20 seconds of vehicle delay per signal cycle is a measurable cost. So is one fatal or serious pedestrian injury per month at intersections that already have the city's primary safety treatment installed.

## Data source and methodology

This analysis uses three public datasets from SDOT, accessed via the [Seattle ArcGIS REST API](https://data-seattlecitygis.opendata.arcgis.com/):

- **[SDOT Collisions All Years](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::sdot-collisions-all-years)** -- 9,921 collision records involving pedestrians, with fields for collision type (`ST_COLCODE`), severity, right-of-way (`PEDROWNOTGRNT`), and intersection key (`INTKEY`).
- **SDOT Collisions Persons** -- Per-person detail records for each collision, with fields for pedestrian action (`ST_PED_ACT_CD`), facility used (`ST_PED_WAS_USING_CD`), injury class (`ST_INJRY_CLSS`), and contributing circumstances. Joined to the collision table via `COLDETKEY`.
- **[Vision Zero Signals LPI/NTOR](https://experience.arcgis.com/experience/26fc62bba1a942f1bfbc0f0ef4d9458e/)** -- Inventory of all 1,240 signalized intersections with `LPI_Status` indicating whether an LPI is installed (January 2024 snapshot). Joined to the collision table via `INTKEY`.

Key filters: pedestrian persons were identified with `ST_PARTCPNT_TYPE IN ('07','7')`. "Crossing with signal" uses `ST_PED_ACT_CD = 1`. "Marked crosswalk" uses `ST_PED_WAS_USING_CD = 4`. LPI intersections were identified with `LPI_Status = 'Ex'`.

**Limitations:**

- **LPI status is a snapshot, not a timeline.** The LPI inventory reflects installations as of January 2024. We cannot determine when each LPI was installed, so collisions from earlier years at "LPI intersections" may have occurred before the LPI was active. This means the pre-2015 data at LPI locations includes years without LPIs. The 2020-2025 analysis is the most reliable period, as the majority of LPIs were already installed.
- **Selection bias.** SDOT installs LPIs at the busiest, highest-conflict intersections first. Higher collision counts at LPI intersections do not mean LPIs are ineffective -- these intersections had more crashes to begin with. The analysis does not attempt to estimate LPI effectiveness (SDOT's [before/after study](https://sdotblog.seattle.gov/2018/12/06/leading-pedestrian-intervals-every-second-counts/) already does that). It shows that crashes continue at treated intersections at a level that warrants further intervention.
- **No pedestrian volume data.** Without intersection-level pedestrian counts, we cannot calculate per-exposure crash rates. The per-intersection comparisons in this analysis are a rough proxy.
- `ST_PED_ACT_CD = 1` records that the pedestrian was crossing during the walk phase. It does not distinguish between the LPI head-start period and the concurrent green.
- Injury severity is reported by the responding officer and may not reflect final medical outcomes.
- 3,249 of 9,921 pedestrian collisions had no `INTKEY` and could not be matched to any signalized intersection.

The analysis scripts are available in the [project repository](https://github.com/prestomation/urbanism-guide/tree/main/scripts).

---

*Last updated: February 2026*
