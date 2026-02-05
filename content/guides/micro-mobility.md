---
title: "Micro Mobility"
weight: 1
bookToc: true
---

# Micro Mobility in Seattle

Shared e-scooters and bikes have become a significant part of Seattle's transportation landscape. This guide covers the current operators, the history of the program, how city permits work, and where to find data.

## Current operators

As of 2025, two companies operate shared micro mobility services in Seattle:

### Lime

[Lime](https://www.li.me/) is the dominant provider, accounting for over 90% of all shared micro mobility trips in Seattle. Lime operates:

- **Electric scooters** (traditional standing scooters)
- **Lime Glider** (seated scooters, launched May 2025)
- **Electric bikes**

Lime has approximately 13,400 vehicles deployed across Seattle as of 2025.

### Bird

Bird operates as a smaller secondary provider with electric scooters. Bird filed for Chapter 11 bankruptcy in late 2023 but continues to operate in Seattle. The company has approximately 2,400 vehicles deployed.

## Pricing

### Standard rates

Lime charges $1 to unlock plus $0.47 per minute. Bird has similar per-ride pricing.

### LimePrime subscription

For frequent riders, Lime offers a $6/month subscription with improved rates:
- Rides up to 5 minutes: $1.50 flat
- Rides up to 20 minutes: $2.85 flat (comparable to a single transit fare)
- Rides over 20 minutes: $0.28 per additional minute

### Reduced-fare programs

Both Lime and Bird offer discounted rates for qualifying low-income riders:
- **Unlock fee:** $0.75
- **Per-minute rate:** $0.01

You may qualify if you have ORCA LIFT, the Regional Reduced Fare Permit (RRFP), Apple Health (Medicaid), or receive discounted utilities, housing assistance, or SNAP benefits.

**Learn more:** [How to Use Scooter Share and Bike Share](https://www.seattle.gov/transportation/projects-and-programs/programs/bike-program/how-to-use-scooter-share-and-bike-share) (seattle.gov)

## History

### 2014-2017: Pronto's rise and fall

Seattle's first bike share system was **Pronto Cycle Share**, a docked system that launched in October 2014. The non-profit-run program struggled financially and operationally. The city shut down Pronto in March 2017 rather than continue subsidizing it.

### 2017: Dockless bike share arrives

Just four months after Pronto closed, Seattle became the first major U.S. city to permit **dockless bike share**. In July 2017, SDOT launched a pilot program allowing three companies to operate:

- **LimeBike** (now Lime) - green bikes
- **Spin** - orange bikes
- **Ofo** - yellow bikes

The dockless model let riders pick up and drop off bikes anywhere, rather than at fixed stations. Ridership took off immediately, with the three companies generating more trips in their first four months than Pronto did in two and a half years.

### 2018-2019: Market consolidation

The venture-capital-fueled bike share boom didn't last. Ofo, the Chinese bike share giant, pulled out of Seattle and eventually folded globally under massive debt. Spin pivoted away from bikes to focus on scooters and left Seattle.

By 2019, Lime was the only bike share operator remaining.

### 2020: E-scooters arrive

Seattle took a cautious approach to e-scooters, waiting to learn from other cities before launching its own program. In September 2020, SDOT permitted three scooter companies to begin operating:

- **Lime** (returning operator)
- **LINK** (by Superpedestrian)
- **Wheels**
- **Spin**

The scooter program launched during the COVID-19 pandemic but still recorded nearly 1.5 million rides in its first year.

### 2022: Permit refresh

After a pilot evaluation, SDOT ran a competitive application process emphasizing safety, equity, and proper parking. The new permit holders for 2022-2023 were:

- **Lime** (returning)
- **LINK by Superpedestrian** (returning)
- **Bird** (new)

Wheels and Spin departed.

### 2023: Industry turmoil

The shared micro mobility industry hit turbulence in late 2023:

- **Superpedestrian** (LINK scooters) abruptly shut down U.S. operations in December 2023, turning off access to its scooters on December 26 with little warning
- **Bird** filed for Chapter 11 bankruptcy

Seattle responded by reassigning Superpedestrian's approximately 2,000 permits to the remaining operators, Lime and Bird.

### 2024-2025: Record growth

Despite the industry consolidation, Seattle's shared micro mobility ridership has continued growing:

- **2023:** 5.1 million trips
- **2024:** 6.3 million trips (up 28%)
- **2025:** On pace to exceed 10 million trips

Lime introduced the seated Lime Glider scooter in May 2025, which surpassed 1 million trips within months of launch. The company also expanded service to the University of Washington campus.

**Learn more:** [Seattle's Scooter and Bikeshare Boom Reaches New Heights](https://www.theurbanist.org/2025/04/15/seattles-scooter-and-bikeshare-boom-reaches-new-heights/) (The Urbanist)

## How city permits work

### Permit structure

SDOT manages shared micro mobility through a permit system. Key elements:

- **Permit fees:** Companies pay permit fees to operate in Seattle, which fund program administration
- **Fleet caps:** Each permitted company can deploy a set number of vehicles (historically up to 2,000 per operator, though caps have increased)
- **Annual review:** Permits are issued for one-year terms with regular evaluation

### Operator requirements

Permitted companies must:

- Host real-time data in a public API feed using the [General Bikeshare Feed Specification (GBFS)](https://gbfs.org/)
- Implement safety features (speed governors, helmet programs, first-ride speed limits)
- Offer reduced-fare programs for low-income riders
- Use GPS and geofencing to manage parking compliance
- Distribute helmets at community events (SDOT has given away over 13,000 helmets since 2022)

### Selection criteria

When SDOT evaluates permit applications, they prioritize:

1. **Safety:** Equipment quality, helmet distribution, speed management
2. **Equity:** Geographic coverage including underserved areas, accessible pricing
3. **Parking compliance:** Technology to prevent sidewalk obstruction

**Learn more:** [SDOT Scooter Share Program Updates](https://sdotblog.seattle.gov/2022/05/12/seattle-scooter-share-program-updates/) (SDOT Blog)

## Bike & Scoot to Transit program

The **Bike & Scoot to Transit** program is a collaboration between King County Metro, SDOT, Sound Transit, Lime, Bird, and technology partners. It incentivizes using shared micro mobility for first/last-mile connections to transit.

### How it works

1. Connect your Transit GO Ticket app with your Lime or Bird account
2. Ride a shared bike or scooter to a transit hub
3. Park in designated spots
4. Earn rewards toward future transit trips or bike/scooter rides

The program aims to reduce car trips by making it easier and cheaper to combine micro mobility with public transit.

**Learn more:** [Bike & Scoot to Transit](https://kingcounty.gov/en/dept/metro/promo/bike-scoot) (King County Metro)

## Data sources

SDOT publishes data on the shared micro mobility program for transparency and planning purposes.

### SDOT data dashboard

The city maintains a dashboard showing trip counts, fleet sizes, and other metrics used for permit compliance and transportation planning.

**Access the data:** [Scooter and Bike Share - Data and Permit Information](https://www.seattle.gov/transportation/projects-and-programs/programs/new-mobility-program/scooter-bike-share-data) (seattle.gov)

### Real-time GBFS feeds

As a permit requirement, each operator must publish real-time vehicle location and availability data using the [General Bikeshare Feed Specification (GBFS)](https://gbfs.org/).

**Lime:**
- `https://data.lime.bike/api/partners/v1/gbfs/seattle/gbfs.json`
- `https://data.lime.bike/api/partners/v1/gbfs/seattle/free_bike_status.json`

For current API endpoints for all operators, check the [SDOT data page](https://www.seattle.gov/transportation/projects-and-programs/programs/new-mobility-program/scooter-bike-share-data).

### Seattle Open Data Portal

The [Seattle Open Data Portal](https://data.seattle.gov/) may contain additional transportation datasets.

### Contact

For questions about the program or data:
- **Bike share:** BikeShare@seattle.gov
- **Scooter share:** ScooterShare@seattle.gov

## Key statistics (2025)

| Metric | Value |
|--------|-------|
| Total trips (2024) | 6.3 million |
| Projected trips (2025) | 10+ million |
| Total fleet size | ~15,800 vehicles |
| Registered users | ~359,000 |
| Peak daily trips | 20,000+ |
| Lime market share | ~93% |

## Related resources

- [Vision Zero Seattle](https://seattle.gov/transportation/projects-and-programs/safety-first/vision-zero) - City's traffic safety initiative
- [Seattle Bicycle Master Plan](https://www.seattle.gov/transportation/document-library/citywide-plans/modal-plans/bicycle-master-plan) - Long-range bicycle infrastructure planning
- [Transportation Glossary]({{< relref "/glossary/transportation" >}}) - Terms like "mode share" and "first/last mile"

---

*Last updated: February 2026*
