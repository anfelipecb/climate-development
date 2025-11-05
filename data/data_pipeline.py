"""
Data Pipeline for MICS + ERA5 Temperature Analysis

This script processes household survey data (MICS) merged with climate data (ERA5-Land).
It reads raw Stata files, performs cleaning and filtering, and saves processed data
to CSV files for visualization.

IMPORTANT: This pipeline does NOT include sensitive geocoded cluster coordinates in 
the processed output files that will be committed to GitHub.
"""

from pathlib import Path
import pandas as pd
import numpy as np

# Study countries
STUDY_COUNTRIES = [
    "Georgia", 
    "Gambia",  # Note: In data might be "The Gambia"
    "State of Palestine", 
    "Madagascar", 
    "Malawi", 
    "Sierra Leone"
]

def load_mics_discipline_data(raw_path: Path) -> pd.DataFrame:
    """
    Load MICS discipline data with temperature linkage.
    
    Expected file: MICS_FINAL_Compl_TEMPERATURE_25Nov2024.dta
    Contains: discipline module responses + temperature exposure variables
    """
    print("Loading MICS discipline data...")
    df = pd.read_stata(raw_path)
    
    # Filter to study countries
    # Handle both "Gambia" and "The Gambia"
    df_filtered = df[
        df["country"].isin(STUDY_COUNTRIES) | 
        (df["country"] == "The Gambia")
    ].copy()
    
    print(f"  Total rows: {len(df):,}")
    print(f"  Study countries rows: {len(df_filtered):,}")
    
    return df_filtered


def load_mics_ecdi_data(raw_path: Path) -> pd.DataFrame:
    """
    Load MICS early childhood development (ECDI) data with temperature linkage.
    
    Expected file: data_NGP_Dec2024.dta
    Contains: ECDI indicators + temperature exposure variables
    """
    print("Loading MICS ECDI data...")
    df = pd.read_stata(raw_path)
    
    # Filter to study countries
    df_filtered = df[
        df["country"].isin(STUDY_COUNTRIES) |
        (df["country"] == "The Gambia")
    ].copy()
    
    print(f"  Total rows: {len(df):,}")
    print(f"  Study countries rows: {len(df_filtered):,}")
    
    return df_filtered


def load_cluster_locations(raw_path: Path) -> pd.DataFrame:
    """
    Load cluster location data.
    
    Expected file: Countries-Cluser.csv
    Contains: country, cluster ID, latitude, longitude
    
    NOTE: This function loads the data but coordinates will NOT be saved
    to processed outputs that get committed to GitHub.
    """
    print("Loading cluster location data...")
    df = pd.read_csv(raw_path)
    
    # Filter to study countries
    df_filtered = df[
        df["country_str"].isin(STUDY_COUNTRIES) |
        (df["country_str"] == "The Gambia")
    ].copy()
    
    print(f"  Total clusters: {len(df):,}")
    print(f"  Study countries clusters: {len(df_filtered):,}")
    
    return df_filtered


def create_discipline_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create binary discipline indicators from MICS discipline module.
    
    Following UNICEF (2017) categorization:
    - Physical punishment: shook, spanked
    - Severe physical punishment: hit with object, hit head/limbs, beat up
    - Psychological aggression: shouted, called names
    - Nonviolent discipline: took away privileges, explained, gave alternative task
    """
    print("Creating discipline indicators...")
    
    df = df.copy()
    
    # Check which columns exist
    disc_cols = [col for col in df.columns if col.startswith('disc')]
    print(f"  Found {len(disc_cols)} discipline columns")
    
    # Physical punishment (mild)
    if 'discshook' in df.columns and 'discspank' in df.columns:
        df['physical_punishment'] = (
            (df['discshook'] == 'Yes') | (df['discspank'] == 'Yes')
        ).astype(int)
    
    # Severe physical punishment
    severe_cols = ['discstrike', 'dischithead', 'dischitlimb', 'discbeathard']
    if all(col in df.columns for col in severe_cols):
        df['severe_physical'] = (
            (df['discstrike'] == 'Yes') | 
            (df['dischithead'] == 'Yes') | 
            (df['dischitlimb'] == 'Yes') | 
            (df['discbeathard'] == 'Yes')
        ).astype(int)
    
    # Psychological aggression
    if 'discshout' in df.columns and 'disccallname' in df.columns:
        df['psychological_aggression'] = (
            (df['discshout'] == 'Yes') | (df['disccallname'] == 'Yes')
        ).astype(int)
    
    # Nonviolent discipline
    nonviol_cols = ['discprivileges', 'discwhywrong', 'discnewtask']
    if all(col in df.columns for col in nonviol_cols):
        df['nonviolent_discipline'] = (
            (df['discprivileges'] == 'Yes') | 
            (df['discwhywrong'] == 'Yes') | 
            (df['discnewtask'] == 'Yes')
        ).astype(int)
    
    return df


def create_temperature_bins(df: pd.DataFrame, temp_col: str, bin_col_name: str) -> pd.DataFrame:
    """
    Create 1°C temperature bins for non-parametric analysis.
    Reference category: <26°C
    """
    print(f"Creating temperature bins for {temp_col}...")
    
    df = df.copy()
    
    bin_edges = [-np.inf, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, np.inf]
    bin_labels = [
        '<26°C', '26-27°C', '27-28°C', '28-29°C', '29-30°C',
        '30-31°C', '31-32°C', '32-33°C', '33-34°C', '34-35°C', '>35°C'
    ]
    
    df[bin_col_name] = pd.cut(
        df[temp_col],
        bins=bin_edges,
        labels=bin_labels,
        include_lowest=True
    )
    
    # Show distribution
    if bin_col_name in df.columns:
        print(f"  Distribution:")
        print(df[bin_col_name].value_counts().sort_index())
    
    return df


def prepare_discipline_analysis_data(df: pd.DataFrame, output_path: Path):
    """
    Prepare cleaned discipline data for visualization.
    
    Excludes sensitive location data but keeps:
    - Country identifier
    - Temperature exposures
    - Discipline indicators
    - Relevant covariates
    """
    print("\nPreparing discipline analysis data...")
    
    # Select columns for analysis (NO coordinates)
    analysis_cols = [
        'country',
        't_from_birth_to_interview',
        't_6m_before_interv',
        'physical_punishment',
        'severe_physical',
        'psychological_aggression',
        'nonviolent_discipline',
    ]
    
    # Add optional covariates if they exist
    optional_cols = ['agech', 'sexch', 'windex5', 'urban', 'edlevelmom']
    for col in optional_cols:
        if col in df.columns:
            analysis_cols.append(col)
    
    # Filter to columns that exist
    available_cols = [col for col in analysis_cols if col in df.columns]
    
    df_analysis = df[available_cols].copy()
    
    # Drop rows with missing temperature data
    if 't_6m_before_interv' in df_analysis.columns:
        df_analysis = df_analysis.dropna(subset=['t_6m_before_interv'])
    
    # Save to CSV
    df_analysis.to_csv(output_path, index=False)
    print(f"  Saved {len(df_analysis):,} rows to {output_path.name}")
    print(f"  Columns: {list(df_analysis.columns)}")


def prepare_ecdi_analysis_data(df: pd.DataFrame, output_path: Path):
    """
    Prepare cleaned ECDI data for visualization.
    
    Excludes sensitive location data but keeps:
    - Country identifier
    - Temperature exposures
    - ECDI indicators
    - Relevant covariates
    """
    print("\nPreparing ECDI analysis data...")
    
    # Select columns for analysis (NO coordinates)
    analysis_cols = [
        'country',
        't_from_birth_to_interview',
        't_6m_before_interv',
    ]
    
    # Add ECDI indicators if they exist
    ecdi_cols = [
        'ecdi_track',
        'ecdi_litnum_track',
        'ecdi_physical_track',
        'ecdi_se_track',
        'ecdi_learning_track'
    ]
    for col in ecdi_cols:
        if col in df.columns:
            analysis_cols.append(col)
    
    # Add optional covariates
    optional_cols = ['agech', 'sexch', 'windex5', 'urban', 'edlevelmom', 
                     'water_improved', 'sanitation_improved']
    for col in optional_cols:
        if col in df.columns:
            analysis_cols.append(col)
    
    # Filter to columns that exist
    available_cols = [col for col in analysis_cols if col in df.columns]
    
    df_analysis = df[available_cols].copy()
    
    # Drop rows with missing temperature or ECDI data
    if 't_from_birth_to_interview' in df_analysis.columns:
        df_analysis = df_analysis.dropna(subset=['t_from_birth_to_interview'])
    
    # Save to CSV
    df_analysis.to_csv(output_path, index=False)
    print(f"  Saved {len(df_analysis):,} rows to {output_path.name}")
    print(f"  Columns: {list(df_analysis.columns)}")


def prepare_cluster_summary(df: pd.DataFrame, output_path: Path):
    """
    Prepare cluster summary WITHOUT coordinates.
    
    This creates a country-level summary suitable for GitHub.
    Actual coordinates stay in local data/processed/ and are .gitignored.
    """
    print("\nPreparing cluster summary (no coordinates)...")
    
    summary = df.groupby('country_str').agg(
        n_clusters=('cluster', 'nunique'),
        # We can include aggregate stats but not individual coords
    ).reset_index()
    
    summary.to_csv(output_path, index=False)
    print(f"  Saved summary to {output_path.name}")
    print(summary)


def main():
    """
    Main pipeline: Load, clean, and prepare data for visualization.
    """
    import time
    start_time = time.time()
    
    # Paths - resolve relative to script location
    script_dir = Path(__file__).parent
    raw_dir = script_dir / "processed"  # Raw Stata files are in processed/
    output_dir = script_dir / "processed"
    
    print("="*60)
    print("MICS + ERA5 Data Pipeline")
    print("="*60)
    
    # 1. Load discipline data
    print("\n1. Processing discipline data...")
    discipline_file = raw_dir / "MICS_FINAL_Compl_TEMPERATURE_25Nov2024.dta"
    if discipline_file.exists():
        df_disc = load_mics_discipline_data(discipline_file)
        df_disc = create_discipline_indicators(df_disc)
        
        # Create temperature bins
        if 't_6m_before_interv' in df_disc.columns:
            df_disc = create_temperature_bins(
                df_disc, 
                't_6m_before_interv', 
                'temp_bin_6m'
            )
        
        # Save for visualization
        prepare_discipline_analysis_data(
            df_disc,
            output_dir / "discipline_analysis_clean.csv"
        )
    else:
        print(f"  WARNING: {discipline_file} not found")
    
    # 2. Load ECDI data
    print("\n2. Processing ECDI data...")
    ecdi_file = raw_dir / "data_NGP_Dec2024.dta"
    if ecdi_file.exists():
        df_ecdi = load_mics_ecdi_data(ecdi_file)
        
        # Create temperature bins
        if 't_from_birth_to_interview' in df_ecdi.columns:
            df_ecdi = create_temperature_bins(
                df_ecdi,
                't_from_birth_to_interview',
                'temp_bin_birth'
            )
        
        # Save for visualization
        prepare_ecdi_analysis_data(
            df_ecdi,
            output_dir / "ecdi_analysis_clean.csv"
        )
    else:
        print(f"  WARNING: {ecdi_file} not found")
    
    # 3. Load cluster locations
    print("\n3. Processing cluster locations...")
    cluster_file = raw_dir / "Countries-Cluser.csv"
    if cluster_file.exists():
        df_clusters = load_cluster_locations(cluster_file)
        
        # Save summary only (no coordinates for GitHub)
        prepare_cluster_summary(
            df_clusters,
            output_dir / "cluster_summary.csv"
        )
        
        print("\n  NOTE: Actual cluster coordinates are kept locally in")
        print(f"        {cluster_file}")
        print("        They are .gitignored and will NOT be committed to GitHub")
    else:
        print(f"  WARNING: {cluster_file} not found")
    
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print(f"Pipeline completed in {total_time:.1f} seconds")
    print("="*60)
    print("\nProcessed files ready for visualization:")
    print("  - discipline_analysis_clean.csv")
    print("  - ecdi_analysis_clean.csv")
    print("  - cluster_summary.csv")
    print("\nThese files exclude sensitive geocoded coordinates.")


if __name__ == "__main__":
    main()

