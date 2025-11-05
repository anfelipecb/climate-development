from pathlib import Path
from datetime import datetime
import cdsapi
import xarray as xr
import pandas as pd
import requests
import zipfile


def extract_netcdf_from_zip(zip_path: Path) -> Path:
    """
    Extract NetCDF file from ZIP archive if needed.
    CDS API sometimes returns ZIP files instead of direct NetCDF.
    
    Args:
        zip_path: Path to potential ZIP file
        
    Returns:
        Path to extracted NetCDF file or original path if not a ZIP
    """
    # Check if it's actually a ZIP file
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List all NetCDF files in the archive
            nc_files = [f for f in zip_ref.namelist() if f.endswith('.nc')]
            
            if not nc_files:
                raise ValueError(f"No NetCDF files found in {zip_path}")
            
            if len(nc_files) > 1:
                print(f"Warning: Multiple NetCDF files found, using first one: {nc_files[0]}")
            
            # Extract the NetCDF file
            extracted_name = zip_path.stem + '_extracted.nc'
            extracted_path = zip_path.parent / extracted_name
            
            if extracted_path.exists():
                print(f"Extracted file already exists: {extracted_path}")
                return extracted_path
            
            print(f"Extracting {nc_files[0]} from ZIP archive...")
            with zip_ref.open(nc_files[0]) as source:
                with open(extracted_path, 'wb') as target:
                    target.write(source.read())
            
            return extracted_path
            
    except zipfile.BadZipFile:
        # Not a ZIP file, return original path
        return zip_path


def download_monthly_variable(
    output_dir: Path,
    start_year: int,
    end_year: int,
    dataset_name: str,
    variable: str,
    file_suffix: str,
    product_type: str = 'monthly_averaged_reanalysis'
) -> Path:
    """
    Generic download function for ERA5 monthly variables.
    Handles both direct NetCDF and ZIP-wrapped NetCDF responses.

    Args:
        output_dir: Directory to save the NetCDF file
        start_year: Start year for data
        end_year: End year for data
        dataset_name: ERA5 dataset ID (e.g. 'reanalysis-era5-single-levels-monthly-means')
        variable: Variable name (e.g., '2m_temperature')
        file_suffix: Suffix for output filename (e.g., 'tmean', 'tmin', 'tmax')
        product_type: Product type for the dataset
    """
    out_file = output_dir / f'era5_{file_suffix}_{start_year}_{end_year}_monthly.nc'
    extracted_file = output_dir / f'era5_{file_suffix}_{start_year}_{end_year}_monthly_extracted.nc'

    # Check if already extracted
    if extracted_file.exists():
        print(f"Extracted file {extracted_file} already exists. Using it.")
        return extracted_file
    
    # Check if original file exists
    if out_file.exists():
        print(f"File {out_file} already exists. Checking if it needs extraction...")
        return extract_netcdf_from_zip(out_file)

    client = cdsapi.Client()
    print(f"Downloading {file_suffix} data to {out_file}...")
    years = [str(year) for year in range(start_year, end_year + 1)]

    client.retrieve(
        dataset_name,
        {
            'product_type': product_type,
            'variable': variable,
            'year': years,
            'month': [f'{month:02d}' for month in range(1, 13)],
            'time': '00:00',
            'format': 'netcdf',
        },
        str(out_file)
    )

    # Extract if it's a ZIP file
    return extract_netcdf_from_zip(out_file)

def download_world_geojson(out_dir: Path) -> Path:
    """Download world countries GeoJSON."""
    output = out_dir / "world_countries.geojson"
    
    if output.exists():
        print(f"GeoJSON exists: {output}")
        return output
    
    url = "https://public.opendatasoft.com/explore/dataset/country_shapes/download/?format=geojson"
    print(f"Downloading world GeoJSON to {output}...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output.write_bytes(response.content)
    return output


### Processing with xarray for raster datasets

def load_and_clean(path: Path) -> xr.Dataset:
    """
    Load NetCDF with chunking for memory efficiency.
    Standardize coordinates and convert temperature to Celsius.
    """
    print("  Loading NetCDF with chunking...")
    ds = xr.open_dataset(
        path, 
        chunks={'time': 60, 'latitude': 400, 'longitude': 400}
    )
    
    # Standardize time coordinate naming
    if 'valid_time' in ds.coords:
        ds = ds.rename({'valid_time': 'time'})
    elif 'date' in ds.coords and 'time' not in ds.coords:
        ds = ds.rename({'date': 'time'})
    
    # Convert longitude from 0-360 to -180-180 for proper mapping
    if "longitude" in ds.coords:
        # Step 1: Relabel coordinates
        ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180))
        # Step 2: Sort to reorder the data array to match new coordinates
        ds = ds.sortby("longitude")
        print("  Correcting longitude to -180/180 format...")
    
    # Convert Kelvin to Celsius
    for var in list(ds.data_vars):
        if "units" in ds[var].attrs and ds[var].attrs["units"].lower().startswith("k"):
            ds[var] = ds[var] - 273.15
            ds[var].attrs["units"] = "C"

    return ds

def monthly_anomaly_from_monthly(ds_monthly: xr.Dataset, baseline_start: int, baseline_end: int) -> xr.Dataset:
    """
    Calculate temperature anomalies relative to baseline period.
    Returns dataset with mean temperature and anomaly values.
    """
    print(f"  Computing climatology for {baseline_start}-{baseline_end}...")
    var_name = list(ds_monthly.data_vars)[0]
    t2m = ds_monthly[var_name]
    
    clim = (
        t2m.sel(time=slice(f"{baseline_start}-01-01", f"{baseline_end}-12-31"))
        .groupby("time.month")
        .mean("time")
    )
    
    print("  Computing anomalies...")
    anom = t2m.groupby("time.month") - clim
    
    return xr.Dataset(
        {
            "t2m_mean_c": t2m.astype("float32"),
            "t2m_anomaly_c": anom.astype("float32"),
        }
    )


def extract_monthly_extrema(ds_min: xr.Dataset, ds_max: xr.Dataset) -> xr.Dataset:
    """
    Extract min and max from monthly extrema datasets.
    Assumes variable names are standardized after load_and_clean.
    """
    # Get the first variable from each dataset (should be t2m after cleaning)
    var_min = list(ds_min.data_vars)[0]
    var_max = list(ds_max.data_vars)[0]
    
    return xr.Dataset({
        "t2m_min_c": ds_min[var_min].astype("float32"),
        "t2m_max_c": ds_max[var_max].astype("float32"),
    })


def compute_global_monthly_stats(ds: xr.Dataset, columns: list[str]) -> pd.DataFrame:
    """
    Aggregate temperature statistics globally for each month.
    Used for time series visualizations.
    """
    print("  Aggregating global statistics...")
    
    stats_list = []
    for col in columns:
        var = ds[col]
        stats_list.append(
            xr.Dataset({
                f"{col}_mean": var.mean(dim=['latitude', 'longitude']),
                f"{col}_median": var.median(dim=['latitude', 'longitude']),
                f"{col}_min": var.min(dim=['latitude', 'longitude']),
                f"{col}_max": var.max(dim=['latitude', 'longitude']),
            })
        )
    
    ds_stats = xr.merge(stats_list)
    ds_stats_computed = ds_stats.compute()
    
    pdf = ds_stats_computed.to_dataframe().reset_index()
    pdf["year"] = pdf["time"].dt.year.astype("int16")
    pdf["month"] = pdf["time"].dt.month.astype("int8")
    pdf = pdf.drop(columns=["time"])
    
    stat_cols = [c for c in pdf.columns if c not in ["year", "month"]]
    pdf = pdf[["year", "month"] + stat_cols]
    
    return pdf


def compute_spatial_anomalies_recent(ds: xr.Dataset, columns: list[str], 
                                      start_year: int, end_year: int) -> pd.DataFrame:
    """
    Extract spatial data for recent years only.
    Processes year-by-year to avoid memory issues.
    """
    print(f"  Processing {start_year}-{end_year} year-by-year...")
    
    dfs = []
    for year in range(start_year, end_year + 1):
        print(f"    Year {year}...")
        ds_year = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31"))
        ds_computed = ds_year[columns].compute()
        
        pdf = ds_computed.to_dataframe().reset_index()
        pdf["year"] = pdf["time"].dt.year.astype("int16")
        pdf["month"] = pdf["time"].dt.month.astype("int8")
        
        cols = ["latitude", "longitude", "year", "month"] + columns
        dfs.append(pdf[cols])
    
    print("  Concatenating years...")
    result = pd.concat(dfs, ignore_index=True)
    
    # Sort by spatial coordinates for better performance in visualization
    result = result.sort_values(['latitude', 'longitude', 'year', 'month']).reset_index(drop=True)
    
    return result


def save_parquet_pandas(df: pd.DataFrame, path: Path):
    """Save DataFrame to compressed parquet file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, compression='snappy')
    
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  Saved {len(df):,} rows ({size_mb:.1f} MB)")


### MAIN PIPELINE

def main():
    import time
    start_time = time.time()
    
    raw_data_dir = Path("./raw")
    processed_data_dir = Path("./processed")
    start_year = 1991
    end_year = 2025
    baseline_start = 1991
    baseline_end = 2020
    
    # Spatial mapping parameters
    spatial_year_start = 2024  # Start year for spatial data
    spatial_year_end = 2024    # End year for spatial data

    raw_data_dir.mkdir(parents=True, exist_ok=True)
    processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing ERA5-Land data: {start_year}-{end_year}")
    print(f"Baseline period: {baseline_start}-{baseline_end}")
    print(f"Spatial subset: {spatial_year_start}-{spatial_year_end}\n")

    # Download monthly mean temperature
    print("Step 1: Downloading data...")
    step_start = time.time()
    tmean_nc = download_monthly_variable(
        raw_data_dir, start_year, end_year,
        dataset_name='reanalysis-era5-land-monthly-means',
        variable='2m_temperature',
        file_suffix='tmean',
        product_type='monthly_averaged_reanalysis'
    )
    print(f"Completed in {time.time()-step_start:.1f}s\n")

    # Load NetCDF and calculate anomalies
    print("Step 2: Loading and calculating anomalies...")
    step_start = time.time()
    ds_monthly_raw = load_and_clean(tmean_nc)
    ds_monthly = monthly_anomaly_from_monthly(ds_monthly_raw, baseline_start, baseline_end)
    print(f"Completed in {time.time()-step_start:.1f}s\n")

    # Create global time series for visualization
    print("Step 3: Aggregating global monthly statistics...")
    step_start = time.time()
    df_global = compute_global_monthly_stats(ds_monthly, ["t2m_mean_c", "t2m_anomaly_c"])
    global_pq = processed_data_dir / f"global_monthly_stats_{start_year}_{end_year}.parquet"
    save_parquet_pandas(df_global, global_pq)
    print(f"Completed in {time.time()-step_start:.1f}s\n")

    # Extract spatial data for mapping (default: 2024 only)
    print(f"Step 4: Extracting spatial data ({spatial_year_start}-{spatial_year_end})...")
    step_start = time.time()
    df_spatial = compute_spatial_anomalies_recent(
        ds_monthly, 
        ["t2m_mean_c", "t2m_anomaly_c"],
        spatial_year_start,
        spatial_year_end
    )
    spatial_pq = processed_data_dir / f"spatial_anomalies_{spatial_year_start}_{spatial_year_end}.parquet"
    save_parquet_pandas(df_spatial, spatial_pq)
    print(f"Completed in {time.time()-step_start:.1f}s\n")

    total_time = time.time() - start_time
    print(f"Pipeline finished in {total_time/60:.1f} minutes")
    print(f"Output files:")
    print(f"  - {global_pq.name}")
    print(f"  - {spatial_pq.name}")


if __name__ == "__main__":
    main()