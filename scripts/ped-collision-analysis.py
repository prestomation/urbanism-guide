#!/usr/bin/env python3
"""
Seattle Pedestrian Collision Analysis

Queries SDOT Collisions All Years from Seattle's ArcGIS open data,
filters for pedestrian-involved incidents, and generates visualizations.

Data source: https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::sdot-collisions-all-years
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Configuration ──────────────────────────────────────────────────────────
BASE_URL = (
    "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/ArcGIS/rest/services/"
    "SDOT_Collisions_All_Years/FeatureServer/0/query"
)
FIELDS = [
    "INCKEY", "SEVERITYCODE", "SEVERITYDESC", "PERSONCOUNT", "PEDCOUNT",
    "INJURIES", "SERIOUSINJURIES", "FATALITIES", "INCDATE", "INCDTTM",
    "WEATHER", "LIGHTCOND", "ROADCOND", "COLLISIONTYPE", "LOCATION",
    "ADDRTYPE", "JUNCTIONTYPE", "CROSSWALKKEY", "PEDROWNOTGRNT",
    "INATTENTIONIND", "UNDERINFL", "SPEEDING",
]
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "analysis")
BATCH_SIZE = 2000

# ── Data Fetching ──────────────────────────────────────────────────────────

def fetch_ped_collisions():
    """Fetch all pedestrian-involved collision records in batches."""
    all_records = []
    offset = 0
    while True:
        params = urllib.parse.urlencode({
            "where": "PEDCOUNT>=1",
            "outFields": ",".join(FIELDS),
            "f": "json",
            "resultRecordCount": BATCH_SIZE,
            "resultOffset": offset,
            "orderByFields": "INCDATE ASC",
        })
        url = f"{BASE_URL}?{params}"
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = json.loads(resp.read())
        features = data.get("features", [])
        if not features:
            break
        for f in features:
            all_records.append(f["attributes"])
        print(f"  Fetched {len(all_records)} records so far...")
        if len(features) < BATCH_SIZE:
            break
        offset += BATCH_SIZE
    return all_records


def build_dataframe(records):
    """Convert raw records to a cleaned DataFrame."""
    df = pd.DataFrame(records)
    # INCDATE is epoch milliseconds (date only, no time)
    df["date"] = pd.to_datetime(df["INCDATE"], unit="ms", utc=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek  # 0=Mon, 6=Sun

    # INCDTTM has the actual time (e.g. "10/27/2016 8:19:00 PM")
    df["datetime"] = pd.to_datetime(df["INCDTTM"], format="%m/%d/%Y %I:%M:%S %p",
                                     errors="coerce")
    df["hour"] = df["datetime"].dt.hour

    # Drop records with missing/bad dates or years outside a reasonable range
    df = df[(df["year"] >= 2004) & (df["year"] <= 2025)]
    return df


# ── Visualization Helpers ──────────────────────────────────────────────────

COLORS = {
    "primary": "#2563EB",
    "fatal": "#DC2626",
    "serious": "#EA580C",
    "injury": "#F59E0B",
    "property": "#6B7280",
    "accent": "#059669",
    "bg": "#FFFFFF",
    "grid": "#E5E7EB",
    "text": "#1F2937",
}


def style_ax(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=13, fontweight="bold", color=COLORS["text"], pad=12)
    ax.set_xlabel(xlabel, fontsize=10, color=COLORS["text"])
    ax.set_ylabel(ylabel, fontsize=10, color=COLORS["text"])
    ax.tick_params(colors=COLORS["text"], labelsize=9)
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.5)
    ax.set_facecolor(COLORS["bg"])
    for spine in ax.spines.values():
        spine.set_visible(False)


# ── Charts ─────────────────────────────────────────────────────────────────

def chart_annual_trend(df, out):
    """1. Annual pedestrian collisions with fatalities overlay."""
    yearly = df.groupby("year").agg(
        total=("INCKEY", "count"),
        fatalities=("FATALITIES", "sum"),
        serious=("SERIOUSINJURIES", "sum"),
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.bar(yearly["year"], yearly["total"], color=COLORS["primary"], alpha=0.7,
            label="Total pedestrian collisions", zorder=2)
    style_ax(ax1, "Seattle Pedestrian Collisions by Year",
             "Year", "Number of Collisions")
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    ax2 = ax1.twinx()
    ax2.plot(yearly["year"], yearly["fatalities"], color=COLORS["fatal"],
             marker="o", linewidth=2.5, label="Pedestrian fatalities", zorder=3)
    ax2.plot(yearly["year"], yearly["serious"], color=COLORS["serious"],
             marker="s", linewidth=2, linestyle="--",
             label="Serious injuries", zorder=3)
    ax2.set_ylabel("Fatalities / Serious Injuries", fontsize=10, color=COLORS["text"])
    ax2.tick_params(colors=COLORS["text"], labelsize=9)
    for spine in ax2.spines.values():
        spine.set_visible(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)

    fig.tight_layout()
    path = os.path.join(out, "01-annual-trend.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")
    return yearly


def chart_severity_breakdown(df, out):
    """2. Stacked bar chart of collision severity by year."""
    sev_map = {
        1: "Property Damage Only",
        2: "Injury",
        2: "Injury",
        3: "Serious Injury",
        "2b": "Serious Injury",
    }
    # Use SEVERITYDESC directly
    yearly_sev = df.groupby(["year", "SEVERITYDESC"]).size().unstack(fill_value=0)

    color_map = {
        "Property Damage Only Collision": COLORS["property"],
        "Injury Collision": COLORS["injury"],
        "Serious Injury Collision": COLORS["serious"],
        "Fatality Collision": COLORS["fatal"],
        "Unknown": "#9CA3AF",
    }

    fig, ax = plt.subplots(figsize=(11, 5))
    # Reorder columns for stacking (least severe on bottom)
    order = ["Property Damage Only Collision", "Injury Collision",
             "Serious Injury Collision", "Fatality Collision"]
    cols_present = [c for c in order if c in yearly_sev.columns]
    other_cols = [c for c in yearly_sev.columns if c not in order]
    plot_cols = cols_present + other_cols

    yearly_sev[plot_cols].plot(
        kind="bar", stacked=True, ax=ax, width=0.8,
        color=[color_map.get(c, "#9CA3AF") for c in plot_cols],
    )
    style_ax(ax, "Pedestrian Collision Severity by Year", "Year", "Number of Collisions")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_xticklabels(yearly_sev.index, rotation=45, ha="right")

    fig.tight_layout()
    path = os.path.join(out, "02-severity-breakdown.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def chart_time_of_day(df, out):
    """3. Pedestrian collisions by hour of day, split by severity."""
    fatal_serious = df[df["FATALITIES"] + df["SERIOUSINJURIES"] > 0]
    other = df[~df.index.isin(fatal_serious.index)]

    fig, ax = plt.subplots(figsize=(10, 5))
    hours = range(24)
    other_counts = other.groupby("hour").size().reindex(hours, fill_value=0)
    fs_counts = fatal_serious.groupby("hour").size().reindex(hours, fill_value=0)

    ax.bar(hours, other_counts, color=COLORS["primary"], alpha=0.6,
           label="Other collisions", zorder=2)
    ax.bar(hours, fs_counts, bottom=other_counts, color=COLORS["fatal"],
           alpha=0.8, label="Fatal / serious injury", zorder=2)

    style_ax(ax, "Pedestrian Collisions by Time of Day",
             "Hour of Day", "Number of Collisions (all years)")
    ax.set_xticks(hours)
    ax.set_xticklabels([f"{h:02d}" for h in hours], fontsize=8)
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(out, "03-time-of-day.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def chart_weather_light(df, out):
    """4. Collisions by weather and light conditions."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Weather
    weather = df["WEATHER"].fillna("Unknown").value_counts().head(8)
    ax1.barh(weather.index[::-1], weather.values[::-1], color=COLORS["primary"], alpha=0.7)
    style_ax(ax1, "By Weather Condition", "Number of Collisions", "")

    # Light
    light = df["LIGHTCOND"].fillna("Unknown").value_counts().head(8)
    ax2.barh(light.index[::-1], light.values[::-1], color=COLORS["accent"], alpha=0.7)
    style_ax(ax2, "By Light Condition", "Number of Collisions", "")

    fig.suptitle("Pedestrian Collision Conditions", fontsize=14, fontweight="bold",
                 color=COLORS["text"], y=1.02)
    fig.tight_layout()
    path = os.path.join(out, "04-weather-light.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def chart_day_of_week(df, out):
    """5. Collisions by day of week."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dow = df.groupby("day_of_week").agg(
        total=("INCKEY", "count"),
        fatalities=("FATALITIES", "sum"),
    ).reindex(range(7), fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(7), dow["total"], color=COLORS["primary"], alpha=0.7, label="Total", zorder=2)
    style_ax(ax, "Pedestrian Collisions by Day of Week",
             "", "Number of Collisions (all years)")
    ax.set_xticks(range(7))
    ax.set_xticklabels(days)

    ax2 = ax.twinx()
    ax2.plot(range(7), dow["fatalities"], color=COLORS["fatal"], marker="o",
             linewidth=2.5, label="Fatalities", zorder=3)
    ax2.set_ylabel("Fatalities", fontsize=10, color=COLORS["text"])
    for spine in ax2.spines.values():
        spine.set_visible(False)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)

    fig.tight_layout()
    path = os.path.join(out, "05-day-of-week.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def chart_fatality_heatmap(df, out):
    """6. Heatmap of fatal/serious collisions by hour and day of week."""
    fs = df[df["FATALITIES"] + df["SERIOUSINJURIES"] > 0].copy()
    pivot = fs.groupby(["day_of_week", "hour"]).size().unstack(fill_value=0)
    pivot = pivot.reindex(index=range(7), columns=range(24), fill_value=0)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fig, ax = plt.subplots(figsize=(14, 4))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd", interpolation="nearest")
    ax.set_yticks(range(7))
    ax.set_yticklabels(days)
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}" for h in range(24)], fontsize=7)
    ax.set_xlabel("Hour of Day", fontsize=10)
    ax.set_title("Fatal & Serious Injury Pedestrian Collisions\n(Hour × Day of Week, All Years)",
                 fontsize=13, fontweight="bold", pad=12)
    fig.colorbar(im, ax=ax, label="Number of incidents", shrink=0.8)

    fig.tight_layout()
    path = os.path.join(out, "06-fatality-heatmap.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def chart_monthly_seasonality(df, out):
    """7. Monthly seasonality pattern."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = df.groupby("month").agg(
        total=("INCKEY", "count"),
        fatalities=("FATALITIES", "sum"),
    ).reindex(range(1, 13), fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(1, 13), monthly["total"], color=COLORS["primary"], alpha=0.7,
           label="Total collisions", zorder=2)

    ax2 = ax.twinx()
    ax2.plot(range(1, 13), monthly["fatalities"], color=COLORS["fatal"], marker="o",
             linewidth=2.5, label="Fatalities", zorder=3)
    ax2.set_ylabel("Fatalities", fontsize=10)
    for spine in ax2.spines.values():
        spine.set_visible(False)

    style_ax(ax, "Pedestrian Collisions by Month (All Years Combined)",
             "Month", "Total Collisions")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    fig.tight_layout()
    path = os.path.join(out, "07-monthly-seasonality.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def print_summary(df, yearly):
    """Print key statistics."""
    print("\n" + "=" * 60)
    print("SEATTLE PEDESTRIAN COLLISION SUMMARY")
    print("=" * 60)
    print(f"Total records:        {len(df):,}")
    print(f"Date range:           {df['year'].min()} – {df['year'].max()}")
    print(f"Total fatalities:     {int(df['FATALITIES'].sum()):,}")
    print(f"Serious injuries:     {int(df['SERIOUSINJURIES'].sum()):,}")
    print(f"Total injuries:       {int(df['INJURIES'].sum()):,}")
    print()

    peak_year = yearly.loc[yearly["total"].idxmax()]
    print(f"Peak year (collisions): {int(peak_year['year'])} ({int(peak_year['total']):,} collisions)")
    peak_fatal = yearly.loc[yearly["fatalities"].idxmax()]
    print(f"Peak year (fatalities): {int(peak_fatal['year'])} ({int(peak_fatal['fatalities']):,} fatalities)")

    recent = yearly[yearly["year"] >= 2019]
    if not recent.empty:
        print(f"\nRecent years (2019+):")
        for _, row in recent.iterrows():
            print(f"  {int(row['year'])}: {int(row['total']):>4} collisions, "
                  f"{int(row['fatalities']):>2} fatalities, "
                  f"{int(row['serious']):>2} serious injuries")

    print()
    valid_hours = df.dropna(subset=["hour"])
    top_hours = valid_hours.groupby("hour").size().sort_values(ascending=False).head(5)
    print("Most dangerous hours:")
    for h, count in top_hours.items():
        print(f"  {int(h):02d}:00 – {count:,} collisions")

    print("=" * 60)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching pedestrian collision data from Seattle ArcGIS...")
    records = fetch_ped_collisions()
    print(f"Total records fetched: {len(records):,}")

    print("Building DataFrame...")
    df = build_dataframe(records)
    print(f"Records after cleaning: {len(df):,}")

    print("\nGenerating charts...")
    yearly = chart_annual_trend(df, OUTPUT_DIR)
    chart_severity_breakdown(df, OUTPUT_DIR)
    chart_time_of_day(df, OUTPUT_DIR)
    chart_weather_light(df, OUTPUT_DIR)
    chart_day_of_week(df, OUTPUT_DIR)
    chart_fatality_heatmap(df, OUTPUT_DIR)
    chart_monthly_seasonality(df, OUTPUT_DIR)

    print_summary(df, yearly)
    print(f"\nAll charts saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
