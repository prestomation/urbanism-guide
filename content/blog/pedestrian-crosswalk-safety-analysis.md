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

## The trend: LPIs help, but crashes persist

Seattle began installing LPIs around 2009 and accelerated deployment after adopting Vision Zero in 2015. By [2023, SDOT was adding 100 LPIs per year](https://sdotblog.seattle.gov/2023/08/31/vision-zero-were-accelerating-leading-pedestrian-interval-lpi-signal-rollout-throughout-the-city/). Here is the year-by-year count of pedestrians hit while crossing with the signal:

| Year | Peds hit with signal | Fatal | Serious injury |
|---|---|---|---|
| 2006 | 216 | 1 | 25 |
| 2007 | 185 | 0 | 12 |
| 2008 | 180 | 2 | 13 |
| 2009 | 169 | 1 | 15 |
| 2010 | 200 | 0 | 11 |
| 2011 | 147 | 1 | 10 |
| 2012 | 180 | 1 | 18 |
| 2013 | 146 | 1 | 11 |
| 2014 | 198 | 1 | 17 |
| 2015 | 162 | 4 | 4 |
| 2016 | 180 | 1 | 15 |
| 2017 | 184 | 6 | 15 |
| 2018 | 223 | 1 | 21 |
| 2019 | 213 | 0 | 16 |
| 2020 | 104 | 0 | 9 |
| 2021 | 117 | 1 | 14 |
| 2022 | 110 | 0 | 20 |
| 2023 | 114 | 2 | 21 |
| 2024 | 123 | 1 | 9 |
| 2025 | 92 | 2 | 21 |

Total volumes dropped after 2019, largely due to reduced traffic during and after the pandemic. But serious injuries have not declined with them. In 2022 and 2023, there were 20-21 serious injuries per year among pedestrians crossing with the signal -- matching or exceeding pre-pandemic levels despite fewer total incidents.

As a share of all pedestrian collisions, crashes at signalized intersections during the walk phase have held steady at roughly 32-38% across the entire period. LPI deployment has not measurably reduced this share.

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

But the collision data quantifies the cost of that choice. In Seattle, **3,550 pedestrians** were hit at signalized intersections during the walk phase. **283** of those crossing in a marked crosswalk suffered fatal or serious injuries. These crashes happen because the system allows vehicles and pedestrians to occupy the crosswalk at the same time.

At intersections on the [High Injury Network]({{< relref "/glossary/transportation#high-injury-network" >}}) -- particularly along corridors like Rainier Avenue, Aurora Avenue, and MLK Jr Way -- the volume of turning conflicts and the severity of outcomes argue for exclusive phases as a next step beyond LPIs.

Adding 15-20 seconds of vehicle delay per signal cycle is a measurable cost. So is 283 people with life-altering injuries who were following every rule.

## Data source and methodology

This analysis uses two public datasets from SDOT, accessed via the [Seattle ArcGIS REST API](https://data-seattlecitygis.opendata.arcgis.com/):

- **[SDOT Collisions All Years](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::sdot-collisions-all-years)** -- 9,921 collision records involving pedestrians, with fields for collision type (`ST_COLCODE`), severity, and right-of-way (`PEDROWNOTGRNT`).
- **SDOT Collisions Persons** -- Per-person detail records for each collision, with fields for pedestrian action (`ST_PED_ACT_CD`), facility used (`ST_PED_WAS_USING_CD`), injury class (`ST_INJRY_CLSS`), and contributing circumstances.

Key filters: pedestrian persons were identified with `ST_PARTCPNT_TYPE IN ('07','7')`. "Crossing with signal" uses `ST_PED_ACT_CD = 1`. "Marked crosswalk" uses `ST_PED_WAS_USING_CD = 4`.

**Limitations:**

- The collision data does not record signal phasing type (LPI vs. concurrent vs. exclusive). We cannot directly compare crash rates at LPI intersections vs. non-LPI intersections from this dataset alone.
- `ST_PED_ACT_CD = 1` ("crossing at intersection with signal") records that the pedestrian was crossing during the walk phase at a signalized intersection. It does not distinguish between the LPI head-start period and the concurrent green.
- The `PEDROWNOTGRNT` field only records the negative case (pedestrian did NOT have right of way). A null value is ambiguous -- it could mean the pedestrian had ROW or that the field wasn't recorded.
- Injury severity is reported by the responding officer and may not reflect final medical outcomes.

A more precise analysis would require joining collision locations against SDOT's signal phasing inventory (which intersections have LPIs, which have exclusive phases) using the `INTKEY` foreign key. SDOT has done this internally -- their published [48% reduction figure](https://sdotblog.seattle.gov/2018/12/06/leading-pedestrian-intervals-every-second-counts/) confirms the methodology is feasible -- but the joined dataset is not publicly available.

---

*Last updated: February 2026*
