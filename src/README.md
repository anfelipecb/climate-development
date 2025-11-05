# Source Code Directory

This directory contains the production code for generating visualizations used in the static HTML story.

## Script

### `generate_graphs.py`
Main script that creates all visualizations for the project:
- Reads processed data from `data/processed/`
- Generates 14 publication-quality visualizations
- Saves all graphs as SVG files in `static_viz/`

**Usage:**
From root
```zsh
uv run src/generate_graphs.py
```

## Graphs Generated

The script produces the following visualizations:

### Climate Trends (Global)
1. `gr1temperature_time_series.svg` - Monthly temperature range and median (2010-2025)
2. `gr2rolling3m_anomalies.svg` - 3-month rolling average of temperature anomalies
3. `gr3heat_map_moth_anomalies.svg` - Heatmap of monthly anomalies by year
4. `gr4worldmapanomalies.svg` - Global spatial map of 2024 temperature anomalies

### Data Linkage (Country-Specific)
5. `gr5aGeorgia.svg` - Survey cluster locations in Georgia
6. `gr5aGambia.svg` - Survey cluster locations in Gambia
7. `gr5aMadagascar.svg` - Survey cluster locations in Madagascar
8. `gr5aMalawi.svg` - Survey cluster locations in Malawi
9. `gr5aPalestine.svg` - Survey cluster locations in State of Palestine
10. `gr5aSierraLEone.svg` - Survey cluster locations in Sierra Leone
11. `gr5bMadagascar.svg` - Madagascar clusters overlaid on temperature anomaly map

### Outcome Patterns
12. `gr6AggressionTemp.svg` - Mean temperature by discipline type with 95% confidence intervals
13. `gr7ECDITemp.svg` - Mean temperature by ECDI domain and on-track status
14. `gr8TempDistrib.svg` - Temperature exposure distribution by country (box plots)

## Dependencies

The script requires:
- `polars` - Fast dataframe library for large datasets
- `altair` - Declarative visualization library
- `pandas` - Data manipulation
- `vegafusion` - Altair extension for handling large datasets

Install with:
```bash
uv add polars altair pandas vegafusion
```
To sync 

```bash
uv sync
```

## Design Principles

### Chart Types
- **Time series**: Line charts with shaded confidence regions
- **Spatial data**: Choropleth maps with equirectangular projection
- **Distributions**: Box plots and binscatter plots
- **Patterns**: Heatmaps for temporal patterns

### Output Format
All graphs are saved as **SVG** (Scalable Vector Graphics):
- Resolution-independent (perfect for web and print)
- Small file sizes
- Embedded in HTML via `<img>` tags
- Styling consistent with overall page design

## Data Flow

```
data/processed/                        →    generate_graphs.py    →    static_viz/
├── global_monthly_stats_*.parquet         Creates visualizations       ├── gr1-gr14.svg
├── spatial_anomalies_*.parquet           using Altair/Polars          └── index.html
├── MICS_*.dta (Stata files)
└── Countries-Cluser.csv (local only)
```

## Notes

- **Cluster maps** (gr5a*, gr5b*) require `Countries-Cluser.csv` which is .gitignored
  - These maps are generated locally
  - Coordinates are NOT committed to GitHub since UNICEF's data agreement prohibits it
  - Generated SVG files ARE committed (contain only rendered image, not raw coordinates)

- **Performance**: Uses `vegafusion` for efficient rendering of large datasets
  - Spatial data is binned to ~0.5° resolution for web performance
  - Time series uses streaming aggregation

- **Reproducibility**: All graphs can be regenerated from processed data
  - Ensure processed data exists in `data/processed/`
  - Run `python generate_graphs.py` from the `src/` directory
  - All 14 SVG files will be created in `static_viz/`

