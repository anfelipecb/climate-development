"""
Generate all visualizations for the static HTML story.

This script reads processed data and creates all graphs used in the presentation.
All graphs are saved as SVG files in the static_viz/ directory.
"""

from pathlib import Path
import polars as pl
import altair as alt
import pandas as pd
import numpy as np

# Enable vegafusion for large datasets
alt.data_transformers.enable("vegafusion")

# Configure global theme for better readability
# Asked AI how to register the components for fontsizes
alt.themes.register("custom_theme", lambda: {
    "config": {
        "title": {
            "fontSize": 18,
            "font": "sans-serif",
            "anchor": "start",
            "fontWeight": 600
        },
        "axis": {
            "labelFontSize": 13,
            "titleFontSize": 15,
            "titleFontWeight": 600,
            "labelLimit": 300
        },
        "legend": {
            "labelFontSize": 12,
            "titleFontSize": 13
        },
        "header": {
            "labelFontSize": 13,
            "titleFontSize": 14
        }
    }
})
alt.themes.enable("custom_theme")

# Paths - resolve relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data" / "processed"
OUTPUT_DIR = SCRIPT_DIR.parent / "static_viz"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Study countries for filtering
STUDY_COUNTRIES = ["Georgia", "Gambia", "State of Palestine", "Madagascar", "Malawi", "Sierra Leone"]

# Country ID mapping for TopoJSON filtering
# AI: Asked which IDs correspond to each country in world-atlas
COUNTRY_ID_MAP = {
    "Georgia": 268,
    "Gambia": 270,
    "State of Palestine": 275,
    "Madagascar": 450,
    "Malawi": 454,
    "Sierra Leone": 694,
}


def save_chart(chart, filename: str):
    """Helper to save Altair charts as SVG."""
    output_path = OUTPUT_DIR / filename
    chart.save(str(output_path))
    print(f"Saved {filename}")


# === DATA LOADING ===

def load_climate_data():
    """Load processed climate data (temperature time series and spatial)."""
    print("Loading climate data...")
    
    monthly_temp = pl.read_parquet(DATA_DIR / "global_monthly_stats_1991_2025.parquet")
    spatial_temp = pl.read_parquet(DATA_DIR / "spatial_anomalies_2024_2024.parquet")
    
    # Add date column for time series plotting
    monthly_temp = monthly_temp.with_columns(
        pl.date(pl.col("year"), pl.col("month"), 1).alias("date")
    )
    
    print(f"  Monthly data: {monthly_temp.shape}")
    print(f"  Spatial data: {spatial_temp.shape}")
    
    return monthly_temp, spatial_temp


def load_mics_discipline_data():
    """Load MICS discipline data with temperature exposure."""
    print("Loading MICS discipline data...")
    
    # Read Stata file directly for now (will use processed CSV once pipeline runs)
    df = pd.read_stata(DATA_DIR / "MICS_FINAL_Compl_TEMPERATURE_25Nov2024.dta")
    
    # Filter to study countries
    df = df[df["country"].isin(STUDY_COUNTRIES + ["The Gambia"])]
    
    # Create discipline indicators
    df['physical_punishment'] = (
        (df['discshook'] == 'Yes') | (df['discspank'] == 'Yes')
    ).astype(int)
    
    df['severe_physical'] = (
        (df['discstrike'] == 'Yes') | (df['dischithead'] == 'Yes') | 
        (df['dischitlimb'] == 'Yes') | (df['discbeathard'] == 'Yes')
    ).astype(int)
    
    df['psychological_aggression'] = (
        (df['discshout'] == 'Yes') | (df['disccallname'] == 'Yes')
    ).astype(int)
    
    df['nonviolent_discipline'] = (
        (df['discprivileges'] == 'Yes') | (df['discwhywrong'] == 'Yes') | 
        (df['discnewtask'] == 'Yes')
    ).astype(int)
    
    print(f"  Discipline data: {df.shape}")
    
    return df


def load_mics_ecdi_data():
    """Load MICS ECDI data with temperature exposure."""
    print("Loading MICS ECDI data...")
    
    df = pd.read_stata(DATA_DIR / "data_NGP_Dec2024.dta")
    
    # Filter to study countries
    df = df[df["country"].isin(STUDY_COUNTRIES + ["The Gambia"])]
    
    print(f"  ECDI data: {df.shape}")
    
    return df


def load_cluster_data():
    """Load cluster location data (local only)."""
    print("Loading cluster data...")
    
    cluster_file = DATA_DIR / "Countries-Cluser.csv"
    if not cluster_file.exists():
        print("  WARNING: Cluster file not found. Skipping cluster maps.")
        return None
    
    df_clusters = pl.read_csv(cluster_file)
    df_clusters = df_clusters.filter(
        pl.col("country_str").is_in(STUDY_COUNTRIES + ["The Gambia"])
    )
    
    print(f"  Cluster data: {df_clusters.shape}")
    
    return df_clusters


# === GRAPH 1: Temperature Time Series ===

def graph1_temperature_time_series(df):
    """Time series showing median temperature with colored deviation areas."""
    print("\nGenerating Graph 1: Temperature time series...")
    
    # Filter to recent years for clarity
    df_filtered = df.filter((pl.col("year") >= 2010) & (pl.col("year") <= 2025))
    
    chart = alt.Chart(df_filtered)
    base = chart.encode(x=alt.X("date:T", title="Year"))
    
    # Area above median (warm deviations - red)
    area_above = base.mark_area(opacity=0.3, color="#fa4d56").encode(
        y=alt.Y("t2m_mean_c_median:Q", title="Temperature (°C)"),
        y2="t2m_mean_c_max:Q"
    )
    
    # Area below median (cold deviations - blue)
    area_below = base.mark_area(opacity=0.3, color="#3498db").encode(
        y=alt.Y("t2m_mean_c_min:Q"),
        y2="t2m_mean_c_median:Q"
    )
    
    # Tooltip for all layers
    tooltip = [
        alt.Tooltip("date:T", title="Date", format="%b %Y"),
        alt.Tooltip("t2m_mean_c_median:Q", title="Median Temp", format=".1f"),
        alt.Tooltip("t2m_mean_c_max:Q", title="Max Temp", format=".1f"),
        alt.Tooltip("t2m_mean_c_min:Q", title="Min Temp", format=".1f")
    ]
    
    # Median line (main trend)
    line_median = base.mark_line(strokeWidth=2.5).transform_calculate(
        series='"Median"'
    ).encode(
        y="t2m_mean_c_median:Q",
        color=alt.Color("series:N", 
                      scale=alt.Scale(domain=["Median", "Maximum", "Minimum"],
                                    range=["#2c3e50", "#750e13", "#003a6d"]),
                      legend=alt.Legend(title="Temperature")),
        tooltip=tooltip
    )
    
    # Max line (hottest location)
    line_max = base.mark_line(strokeWidth=1.5, opacity=0.6).transform_calculate(
        series='"Maximum"'
    ).encode(
        y="t2m_mean_c_max:Q",
        color="series:N",
        tooltip=tooltip
    )
    
    # Min line (coldest location)
    line_min = base.mark_line(strokeWidth=1.5, opacity=0.6).transform_calculate(
        series='"Minimum"'
    ).encode(
        y="t2m_mean_c_min:Q",
        color="series:N",
        tooltip=tooltip
    )
    
    chart_main = alt.layer(area_above, area_below, line_min, line_max, line_median).properties(
        width=800, 
        height=400,
        title="Location-specific global Temperature Range and Median (2010-2025)"
    )
    
    # Add note at the bottom
    note = alt.Chart({"values": [{}]}).mark_text(
        align="left",
        baseline="top",
        fontSize=10,
        color="gray",
        dx=-400,
        dy=10
    ).encode(
        text=alt.value("Note: Data from ERA5-Land monthly mean 2m temperature reanalysis at ~0.1° (~10km) grid resolution")
    ).properties(width=800, height=20)
    
    final_chart = alt.vconcat(chart_main, note, spacing=5).configure_concat(spacing=0)
    
    save_chart(final_chart, "gr1temperature_time_series.svg")


# === GRAPH 2: Rolling Anomalies ===

def graph2_rolling_anomalies(df):
    """Line chart of temperature anomalies with 3-month rolling average."""
    print("\nGenerating Graph 2: Rolling anomalies...")
    
    df_filtered = df.filter((pl.col("year") >= 2000)).sort("date").with_columns(
        pl.col("t2m_anomaly_c_mean").rolling_mean(window_size=3).alias("anomaly_rolling")
    )
    
    chart = alt.Chart(df_filtered)
    base = chart.encode(x=alt.X("date:T", title="Year"))
    
    # Tooltip
    tooltip = [
        alt.Tooltip("date:T", title="Date", format="%b %Y"),
        alt.Tooltip("anomaly_rolling:Q", title="Anomaly (3m avg)", format=".2f"),
        alt.Tooltip("t2m_anomaly_c_mean:Q", title="Raw Anomaly", format=".2f")
    ]
    
    # Pre-2020 line (tan)
    line_pre = base.transform_filter(alt.datum.year < 2020).mark_line(
        color="#a2957cb2", strokeWidth=2.5
    ).encode(
        y=alt.Y("anomaly_rolling:Q", title="Temperature Anomaly (°C)"),
        tooltip=tooltip
    )
    
    # Post-2020 line (red)
    line_post = base.transform_filter(alt.datum.year >= 2020).mark_line(
        color="#d43939", strokeWidth=2.5
    ).encode(
        y="anomaly_rolling:Q",
        tooltip=tooltip
    )
    
    # Calculate means for average lines
    import datetime as dt
    cut = dt.date(2020, 1, 1)
    min_pre = df_filtered.filter(pl.col("year") < 2020).select(pl.min("date")).to_series()[0]
    max_post = df_filtered.select(pl.max("date")).to_series()[0]
    
    mean_pre = float(df_filtered.filter(pl.col("year") < 2020)["anomaly_rolling"].mean())
    mean_post = float(df_filtered.filter(pl.col("year") >= 2020)["anomaly_rolling"].mean())
    
    # Average lines for each period
    rule_pre = base.mark_rule(color="#a2957c81", strokeDash=[4, 2], strokeWidth=1.5).encode(
        x=alt.datum(min_pre),
        x2=alt.datum(cut),
        y=alt.datum(mean_pre),
    )
    
    rule_post = base.mark_rule(color="#d4393981", strokeDash=[4, 2], strokeWidth=1.5).encode(
        x=alt.datum(cut),
        x2=alt.datum(max_post),
        y=alt.datum(mean_post),
    )
    
    chart_main = alt.layer(line_pre, line_post, rule_pre, rule_post).properties(
        width=800, 
        height=400,
        title="3-month rolling average of Global Temperature Anomalies (2000-2025)"
    )
    
    # Add note at the bottom
    note = alt.Chart({"values": [{}]}).mark_text(
        align="left",
        baseline="top",
        fontSize=10,
        color="gray",
        dx=-400,
        dy=10
    ).encode(
        text=alt.value("Note: 3-month rolling average of anomalies (relative to 1991-2020 baseline). Data aggregated globally from ERA5-Land ~0.1° grid.")
    ).properties(width=800, height=20)
    
    final_chart = alt.vconcat(chart_main, note, spacing=5).configure_concat(spacing=0)
    
    save_chart(final_chart, "gr2rolling3m_anomalies.svg")


# === GRAPH 3: Monthly Anomaly Heatmap ===

def graph3_monthly_heatmap(df):
    """Heatmap showing temperature anomalies by month and year."""
    print("\nGenerating Graph 3: Monthly anomaly heatmap...")
    
    df_filtered = df.filter((pl.col("year") >= 2000))
    
    # Tooltip
    tooltip = [
        alt.Tooltip("year:O", title="Year"),
        alt.Tooltip("month(date):O", title="Month"),
        alt.Tooltip("t2m_anomaly_c_mean:Q", title="Anomaly (°C)", format=".2f")
    ]
    
    # AI: Asked how to change color scheme to carbon design system palette
    heat_map = alt.Chart(df_filtered).mark_rect(opacity=0.9).encode(
        alt.X("month(date):O", title="Month"),
        alt.Y("year:O", title="Year"),
        alt.Color("t2m_anomaly_c_mean:Q", 
                  title="Temp Anomaly (°C)",
                  scale=alt.Scale(
                      domainMid=0,
                      range=[
                          "#003a6d",  # Cyan 80 (very cold)
                          "#0072c3",  # Cyan 60
                          "#1192e8",  # Cyan 50
                          "#82cfff",  # Cyan 30
                          "#e5f6ff",  # Cyan 10 (cool)
                          "#fff1f1",  # Red 10 (neutral-warm)
                          "#ff8389",  # Red 40
                          "#fa4d56",  # Red 50
                          "#da1e28",  # Red 60
                          "#a2191f"   # Red 70 (very hot)
                      ]
                  )),
        tooltip=tooltip
    ).properties(
        width=800, 
        height=400,
        title="Monthly Temperature Anomalies (2000-2025)"
    )
    
    # Add note at the bottom
    note = alt.Chart({"values": [{}]}).mark_text(
        align="left",
        baseline="top",
        fontSize=10,
        color="gray",
        dx=-400,
        dy=10
    ).encode(
        text=alt.value("Note: Monthly anomalies relative to 1991-2020 baseline. Data aggregated globally from ERA5-Land.")
    ).properties(width=800, height=20)
    
    final_chart = alt.vconcat(heat_map, note, spacing=5).configure_concat(spacing=0)
    
    save_chart(final_chart, "gr3heat_map_moth_anomalies.svg")


# === GRAPH 4: World Map Anomalies ===

def graph4_world_map(df):
    """Spatial map of 2024 temperature anomalies."""
    print("\nGenerating Graph 4: World map anomalies...")
    
    # Bin to ~0.5° resolution for performance
    df_binned = df.with_columns([
        (pl.col("latitude") * 2).round() / 2,
        (pl.col("longitude") * 2).round() / 2
    ]).group_by(["latitude", "longitude"]).agg(
        pl.mean("t2m_anomaly_c").alias("anomaly_mean")
    )
    
    print(f"  Binned to {df_binned.shape} cells (~0.5° resolution)")
    
    # Tooltip
    tooltip = [
        alt.Tooltip("latitude:Q", title="Latitude", format=".2f"),
        alt.Tooltip("longitude:Q", title="Longitude", format=".2f"),
        alt.Tooltip("mean(anomaly_mean):Q", title="2024 Anomaly (°C)", format=".2f")
    ]
    
    # Temperature raster
    chart = alt.Chart(df_binned).mark_rect().encode(
        x=alt.X("longitude:Q", title="Longitude", bin=alt.Bin(maxbins=100)),
        y=alt.Y("latitude:Q", title="Latitude", bin=alt.Bin(maxbins=100)),
        color=alt.Color(
            "mean(anomaly_mean):Q",
            title="Temp Anomaly (°C)",
            scale=alt.Scale(
                domainMid=0.5,
                range=[
                    "#003a6d", "#0072c3", "#1192e8", "#82cfff", "#e5f6ff",
                    "#fff1f1", "#ff8389", "#fa4d56", "#da1e28", "#a2191f"
                ]
            )
        ),
        tooltip=tooltip
    )
    
    # Country borders
    countries = alt.topo_feature(
        "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json",
        "countries",
    )
    background = alt.Chart(countries).mark_geoshape(
        fill="#ffffff", 
        fillOpacity=0, 
        stroke="#666666", 
        strokeWidth=0.5
    )
    
    chart_main = (chart + background).project(type="equirectangular").properties(
        width=800, 
        height=400, 
        title="Global Temperature Anomalies Map (2024)"
    )
    
    # Add note at the bottom
    note = alt.Chart({"values": [{}]}).mark_text(
        align="left",
        baseline="top",
        fontSize=10,
        color="gray",
        dx=-400,
        dy=10
    ).encode(
        text=alt.value("Note: 2024 annual mean anomalies relative to 1991-2020 baseline. Data from ERA5-Land ~0.1° grid.")
    ).properties(width=800, height=20)
    
    final_chart = alt.vconcat(chart_main, note, spacing=5).configure_concat(spacing=0)
    
    save_chart(final_chart, "gr4worldmapanomalies.svg")


# === GRAPH 5: Cluster Maps by Country ===

def graph5_cluster_maps(df_clusters):
    """Create maps for each study country showing cluster locations."""
    if df_clusters is None:
        print("\nSkipping Graph 5: Cluster maps (no data)")
        return
    
    print("\nGenerating Graph 5: Cluster maps by country...")
    
    # AI: Asked how to import the map at 50m boundary resolution
    countries_url = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json"
    
    for country in ["Georgia", "Gambia", "Madagascar", "Malawi", "State of Palestine", "Sierra Leone"]:
        df_country = df_clusters.filter(pl.col("country_str") == country)
        if len(df_country) == 0:
            continue
        
        # Convert to pandas for Altair
        df_country_pd = df_country.to_pandas()
        
        # Country border
        cid = COUNTRY_ID_MAP.get(country)
        countries = alt.topo_feature(countries_url, "countries")
        background = alt.Chart(countries).transform_filter(
            alt.datum.id == str(cid)
        ).mark_geoshape(fill="#f3f4f6", stroke="#959090", strokeWidth=0.5)
        
        # Cluster points
        points = alt.Chart(df_country_pd).mark_circle(
            size=35, color="#b41f1f62", opacity=0.8
        ).encode(
            longitude="longitude:Q",
            latitude="latitude:Q",
            tooltip=[
                alt.Tooltip("country_str:N", title="Country"),
                alt.Tooltip("longitude:Q", format=".4f"),
                alt.Tooltip("latitude:Q", format=".4f"),
            ]
        )
        
        chart = (background + points).project(type="mercator").properties(
            width=800, height=300, title=f"Survey Clusters in {country}"
        )
        
        # Save with sanitized filename
        filename = f"gr5a{country.replace(' ', '')}.svg"
        save_chart(chart, filename)


# === GRAPH 5B: Madagascar Overlay (Temperature + Clusters) ===

def graph5b_madagascar_overlay(df_clusters, spatial_data):
    """Madagascar clusters overlaid on temperature anomaly map."""
    if df_clusters is None:
        print("\nSkipping Graph 5b: Madagascar overlay (no cluster data)")
        return
        
    print("\nGenerating Graph 5b: Madagascar temperature overlay...")
    
    # Filter clusters for Madagascar
    clusters_filtered = df_clusters.filter(pl.col("country_str") == "Madagascar")
    clusters_pd = clusters_filtered.to_pandas()
    
    # Get Madagascar bounds
    lat_min = float(clusters_filtered["latitude"].min())
    lat_max = float(clusters_filtered["latitude"].max())
    lon_min = float(clusters_filtered["longitude"].min())
    lon_max = float(clusters_filtered["longitude"].max())
    
    # Add padding
    lat_pad = (lat_max - lat_min) * 0.2
    lon_pad = (lon_max - lon_min) * 0.2
    
    # Filter temperature data to Madagascar region
    temp_filtered = spatial_data.filter(
        (pl.col("latitude") >= lat_min - lat_pad) &
        (pl.col("latitude") <= lat_max + lat_pad) &
        (pl.col("longitude") >= lon_min - lon_pad) &
        (pl.col("longitude") <= lon_max + lon_pad) &
        pl.col("t2m_anomaly_c").is_not_null()
    )
    
    # Bin to 0.2° for performance
    temp_binned = temp_filtered.with_columns([
        (pl.col("latitude") * 5).round() / 5,
        (pl.col("longitude") * 5).round() / 5
    ]).group_by(["latitude", "longitude"]).agg(
        pl.mean("t2m_anomaly_c").alias("anomaly_2024_mean")
    )
    
    temp_pd = temp_binned.to_pandas()
    
    print(f"  Rendering {len(temp_pd):,} grid cells for Madagascar")
    
    # Temperature layer
    temp_layer = alt.Chart(temp_pd).mark_square(size=50, opacity=1.0).encode(
        longitude="longitude:Q",
        latitude="latitude:Q",
        color=alt.Color(
            "anomaly_2024_mean:Q",
            title="Temp Anomaly (°C)",
            scale=alt.Scale(scheme="magma")
        ),
        tooltip=[
            alt.Tooltip("latitude:Q", title="Lat", format=".2f"),
            alt.Tooltip("longitude:Q", title="Lon", format=".2f"),
            alt.Tooltip("anomaly_2024_mean:Q", title="Anomaly (°C)", format=".2f")
        ]
    )
    
    # Country border
    countries = alt.topo_feature(
        "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json", "countries"
    )
    border = alt.Chart(countries).transform_filter(
        alt.datum.id == str(COUNTRY_ID_MAP["Madagascar"])
    ).mark_geoshape(fill=None, fillOpacity=0, stroke="#333333", strokeWidth=1.5)
    
    # Cluster points
    points = alt.Chart(clusters_pd).mark_circle(
        size=20, opacity=0.5, stroke="#ffffff", strokeWidth=1.5
    ).encode(
        longitude="longitude:Q",
        latitude="latitude:Q",
        color=alt.Color(
            'cluster_type:N',
            scale=alt.Scale(domain=['Survey Cluster'], range=['#1e40af']),
            legend=alt.Legend(title='')
        ),
        tooltip=[
            alt.Tooltip("country_str:N", title="Country"),
            alt.Tooltip("longitude:Q", format=".4f"),
            alt.Tooltip("latitude:Q", format=".4f")
        ]
    ).transform_calculate(cluster_type='"Survey Cluster"')
    
    chart_main = (temp_layer + border + points).project(
        type="equirectangular"
    ).properties(
        width=800,
        height=500,
        title="Survey Clusters on Temperature Anomaly Map - Madagascar (2024)"
    )
    
    # Add note at the bottom
    note = alt.Chart({"values": [{}]}).mark_text(
        align="left",
        baseline="top",
        fontSize=10,
        color="gray",
        dx=-400,
        dy=10
    ).encode(
        text=alt.value("Note: 2024 annual mean anomalies at ~0.1° resolution. Cluster locations shown as dark blue circles.")
    ).properties(width=800, height=20)
    
    final_chart = alt.vconcat(chart_main, note, spacing=5).configure_view(strokeWidth=0)
    
    save_chart(final_chart, "gr5bMadagascar.svg")


# === GRAPH 6: Discipline vs Temperature (Point Plot with CI) ===

def graph6_discipline_temperature(df):
    """Point plot showing mean temperature by discipline type with confidence intervals."""
    print("\nGenerating Graph 6: Discipline vs temperature...")
    
    # Calculate statistics for each discipline type
    df_clean = df[['t_6m_before_interv', 'nonviolent_discipline', 'psychological_aggression', 
                    'physical_punishment', 'severe_physical']].copy()
    df_clean = df_clean.dropna(subset=['t_6m_before_interv'])
    
    stats_list = []
    for disc_type, disc_col in [
        ('Nonviolent Discipline', 'nonviolent_discipline'),
        ('Psychological Aggression', 'psychological_aggression'),
        ('Physical Punishment', 'physical_punishment'),
        ('Severe Physical Punishment', 'severe_physical')
    ]:
        temps = df_clean[df_clean[disc_col] == 1]['t_6m_before_interv']
        n = len(temps)
        mean = temps.mean()
        std = temps.std()
        se = std / (n ** 0.5)
        ci_95 = 1.96 * se
        
        stats_list.append({
            'Discipline_Type': disc_type,
            'Mean_Temp': mean,
            'CI_Lower': mean - ci_95,
            'CI_Upper': mean + ci_95,
            'N': n
        })
    
    df_stats = pd.DataFrame(stats_list)
    
    # Color scheme: Yellow to Red gradient (severity)
    colors = [
        "#fef3c7",  # Light yellow (nonviolent)
        "#fcd34d",  # Yellow (psychological)
        "#f97316",  # Orange (physical)
        "#b91c1c"   # Dark red (severe physical)
    ]
    
    discipline_order = [
        'Nonviolent Discipline',
        'Psychological Aggression',
        'Physical Punishment',
        'Severe Physical Punishment'
    ]
    
    # Error bars
    error_bars = alt.Chart(df_stats).mark_errorbar(extent='ci').encode(
        y=alt.Y('Discipline_Type:N',
                title='Discipline Type',
                sort=discipline_order,
                axis=alt.Axis(labelLimit=200)),
        x=alt.X('CI_Lower:Q', title='Mean Temperature Exposure (°C)', scale=alt.Scale(zero=False)),
        x2='CI_Upper:Q'
    )
    
    # Points
    points = alt.Chart(df_stats).mark_point(filled=True, size=150).encode(
        y=alt.Y('Discipline_Type:N', sort=discipline_order),
        x=alt.X('Mean_Temp:Q', scale=alt.Scale(zero=False)),
        color=alt.Color(
            'Discipline_Type:N',
            title='Discipline Type',
            scale=alt.Scale(domain=discipline_order, range=colors),
            legend=alt.Legend(orient='right')
        ),
        tooltip=[
            alt.Tooltip('Discipline_Type:N', title='Type'),
            alt.Tooltip('Mean_Temp:Q', title='Mean Temp (°C)', format='.2f'),
            alt.Tooltip('CI_Lower:Q', title='95% CI Lower', format='.2f'),
            alt.Tooltip('CI_Upper:Q', title='95% CI Upper', format='.2f'),
            alt.Tooltip('N:Q', title='Sample Size', format=',')
        ]
    )
    
    chart = (error_bars + points).properties(
        width=600,
        height=300,
        title='Mean Temperature Exposure 6 months before interview, by discipline type'
    )
    
    # Add note at the bottom
    note = alt.Chart({"values": [{}]}).mark_text(
        align="left",
        baseline="top",
        fontSize=10,
        color="gray",
        dx=-300,
        dy=10
    ).encode(
        text=alt.value("Note: Points show mean temperature; error bars show 95% confidence intervals. Gradient from 31.3°C to 32.0°C.")
    ).properties(width=600, height=30)
    
    final_chart = alt.vconcat(chart, note, spacing=5)
    
    save_chart(final_chart, "gr6AggressionTemp.svg")


# === GRAPH 7: ECDI vs Temperature (Point Plot with CI) ===

def graph7_ecdi_temperature(df):
    """Point plot showing mean temperature by ECDI status with confidence intervals."""
    print("\nGenerating Graph 7: ECDI vs temperature...")
    
    # ECDI domains to analyze
    ecdi_domains = [
        ('Overall ECDI', 'ecdi_track'),
        ('Literacy-Numeracy', 'ecdi_litnum_track'),
        ('Physical', 'ecdi_physical_track'),
        ('Socio-Emotional', 'ecdi_se_track'),
        ('Approaches to Learning', 'ecdi_learning_track')
    ]
    
    stats_list = []
    
    for domain_label, domain_col in ecdi_domains:
        if domain_col not in df.columns:
            continue
            
        # Filter to non-missing data
        df_domain = df[['t_from_birth_to_interview', domain_col]].dropna()
        
        # For both on-track and not-on-track
        for status_val, status_label in [(1, 'On Track'), (0, 'Not On Track')]:
            temps = df_domain[df_domain[domain_col] == status_val]['t_from_birth_to_interview']
            
            if len(temps) > 0:
                n = len(temps)
                mean = temps.mean()
                std = temps.std()
                se = std / (n ** 0.5)
                ci_95 = 1.96 * se
                
                stats_list.append({
                    'Domain': domain_label,
                    'Status': status_label,
                    'Mean_Temp': mean,
                    'CI_Lower': mean - ci_95,
                    'CI_Upper': mean + ci_95,
                    'N': n
                })
    
    df_stats = pd.DataFrame(stats_list)
    
    domain_order = [
        'Overall ECDI',
        'Literacy-Numeracy',
        'Physical',
        'Socio-Emotional',
        'Approaches to Learning'
    ]
    
    # Color by status
    status_colors = {
        'On Track': '#10b981',      # Green
        'Not On Track': '#ef4444'   # Red
    }
    
    # Error bars
    error_bars = alt.Chart(df_stats).mark_errorbar(extent='ci').encode(
        y=alt.Y('Domain:N',
                title='ECDI Domain',
                sort=domain_order,
                axis=alt.Axis(labelLimit=250)),
        x=alt.X('CI_Lower:Q', 
                title='Mean Temperature Exposure (°C)', 
                scale=alt.Scale(zero=False)),
        x2='CI_Upper:Q',
        yOffset='Status:N'
    )
    
    # Points
    points = alt.Chart(df_stats).mark_point(filled=True, size=100).encode(
        y=alt.Y('Domain:N', sort=domain_order),
        x=alt.X('Mean_Temp:Q', scale=alt.Scale(zero=False)),
        yOffset='Status:N',
        color=alt.Color(
            'Status:N',
            title='Development Status',
            scale=alt.Scale(
                domain=['On Track', 'Not On Track'],
                range=[status_colors['On Track'], status_colors['Not On Track']]
            ),
            legend=alt.Legend(orient='right')
        ),
        shape=alt.Shape('Status:N', 
                       scale=alt.Scale(
                           domain=['On Track', 'Not On Track'],
                           range=['circle', 'square']
                       ))
    )
    
    # Add darker separator lines between domains for better visibility
    separator_data = pd.DataFrame({
        'y_pos': [0.5, 1.5, 2.5, 3.5],
        'x_start': [df_stats['Mean_Temp'].min() - 0.2] * 4,
        'x_end': [df_stats['Mean_Temp'].max() + 0.2] * 4
    })
    
    separators = alt.Chart(separator_data).mark_rule(
        color='#999999',  # Darker gray for visibility
        strokeWidth=1.5,
        strokeDash=[3, 3]
    ).encode(
        y=alt.Y('y_pos:Q', scale=alt.Scale(domain=[-0.5, 4.5]), axis=None),
        x='x_start:Q',
        x2='x_end:Q'
    )
    
    chart = alt.layer(separators, error_bars, points).resolve_scale(
        y='independent'
    ).properties(
        width=700,
        height=400,
        title='Temperature Exposure by Child Development Status (ECDI Domains)'
    )
    
    # Add note at the bottom
    note = alt.Chart({"values": [{}]}).mark_text(
        align="left",
        baseline="top",
        fontSize=10,
        color="gray",
        dx=-350,
        dy=10
    ).encode(
        text=alt.value("Note: Points show mean temperature for children on-track vs not-on-track. Green circles = on track, red squares = not on track. Error bars = 95% CI.")
    ).properties(width=700, height=40)
    
    final_chart = alt.vconcat(chart, note, spacing=5).configure_view(strokeWidth=0)
    
    save_chart(final_chart, "gr7ECDITemp.svg")


# === GRAPH 8: Temperature Distribution by Country ===

def graph8_temp_distribution(df):
    """Box plots of temperature distribution by country."""
    print("\nGenerating Graph 8: Temperature distributions...")
    
    # Filter to relevant columns
    df_plot = df[['country', 't_from_birth_to_interview']].dropna()
    
    chart = alt.Chart(df_plot).mark_boxplot(size=30, color='#fcd34d', opacity=0.7).encode(
        x=alt.X('t_from_birth_to_interview:Q', title='Temperature (°C)'),
        y=alt.Y('country:N', title='Country')
    ).properties(
        width=800, 
        height=300,
        title="Avg. Temperature Exposition for children from date of birth by Country"
    )
    
    # Add note at the bottom
    note = alt.Chart({"values": [{}]}).mark_text(
        align="left",
        baseline="top",
        fontSize=10,
        color="gray",
        dx=-400,
        dy=10
    ).encode(
        text=alt.value("Note: Temperature exposure from birth to interview date. Box shows median and quartiles, whiskers extend to 1.5×IQR.")
    ).properties(width=800, height=40)
    
    final_chart = alt.vconcat(chart, note, spacing=5)
    
    save_chart(final_chart, "gr8TempDistrib.svg")


# === MAIN EXECUTION ===

def main():
    """Generate all graphs for the static visualization project."""

    print("Generating all visualizations for static project")

    
    # Load data
    monthly_temp, spatial_temp = load_climate_data()
    df_disc = load_mics_discipline_data()
    df_ecdi = load_mics_ecdi_data()
    df_clusters = load_cluster_data()
    
    # Generate graphs
    graph1_temperature_time_series(monthly_temp)
    graph2_rolling_anomalies(monthly_temp)
    graph3_monthly_heatmap(monthly_temp)
    graph4_world_map(spatial_temp)
    graph5_cluster_maps(df_clusters)
    graph5b_madagascar_overlay(df_clusters, spatial_temp)
    graph6_discipline_temperature(df_disc)
    graph7_ecdi_temperature(df_ecdi)
    graph8_temp_distribution(df_ecdi)
    

    print("All graphs generated successfully!")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")



if __name__ == "__main__":
    main()
