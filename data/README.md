# Data Directory

This directory contains scripts for data acquisition and processing, as well as the raw and processed data files.

## Scripts

### `climate_data.py`
Downloads and processes ERA5-Land climate reanalysis data:
- Downloads monthly temperature data from Copernicus Climate Data Store (CDS)
- Calculates temperature anomalies relative to 1991-2020 baseline
- Aggregates global statistics and spatial data for visualization
- **Run from data/ directory:** `python climate_data.py`

### `data_pipeline.py`
Processes household survey data (MICS) merged with climate data:
- Reads Stata files with MICS discipline and ECDI data
- Creates discipline indicators (physical punishment, psychological aggression, etc.)
- Creates temperature bins for non-parametric analysis
- **Saves processed CSV files WITHOUT sensitive geocoded coordinates**
- **Run from data/ directory:** `python data_pipeline.py`

## Data Structure

```
data/
├── raw/                           # Raw climate data (NetCDF files)
│   ├── era5_tmean_*.nc           # ERA5-Land monthly temperature
│   └── ...
├── processed/                     # Processed data
│   ├── MICS_*.dta                # Raw MICS Stata files (LOCAL ONLY, .gitignored)
│   ├── Countries-Cluser.csv      # Cluster coordinates (LOCAL ONLY, .gitignored)
│   ├── global_monthly_stats_*.parquet      # Climate time series
│   ├── spatial_anomalies_*.parquet         # Spatial temperature data
│   ├── discipline_analysis_clean.csv       # Processed discipline data (no coords)
│   ├── ecdi_analysis_clean.csv            # Processed ECDI data (no coords)
│   └── cluster_summary.csv                # Country-level cluster counts
└── regressions/                   # Regression results from Stata
    └── results_stata.txt
```

## Important Notes

### Data Privacy

**The following files contain sensitive geocoded household locations and are .gitignored:**
- `processed/MICS_*.dta` - Raw MICS Stata files with coordinates
- `processed/Countries-Cluser.csv` - Cluster location file
- `processed/*_TEMPERATURE_*.dta` - Merged MICS-temperature files

These files remain **local only** and are NOT committed to GitHub.

**The following processed files are safe for GitHub** (no coordinates):
- `discipline_analysis_clean.csv` - Aggregate discipline data by country/temperature
- `ecdi_analysis_clean.csv` - Aggregate ECDI data by country/temperature  
- `cluster_summary.csv` - Country-level cluster counts only

### Data Sources

1. **ERA5-Land Climate Reanalysis**
   - Source: Copernicus Climate Data Store
   - Coverage: 1991-2025, monthly aggregates
   - Resolution: ~0.1° (~10km)
   - Variables: 2m temperature

2. **MICS (Multiple Indicator Cluster Surveys)**
   - Source: UNICEF
   - Countries: Georgia, Gambia, Madagascar, Malawi, Sierra Leone, State of Palestine
   - Surveys: 2017-2020
   - Modules: Discipline, Early Childhood Development (ECDI)

## Running the Pipeline

1. **Download climate data** (one-time):
   ```bash
   cd data/
   python climate_data.py
   ```

2. **Process MICS data** (after placing raw Stata files in `processed/`):
   ```bash
   cd data/
   python data_pipeline.py
   ```

3. **Generate visualizations** (from project root):
   ```bash
   cd src/
   python generate_graphs.py
   ```

All outputs will be ready for the HTML visualization in `static_viz/`.

