# src/data_cleaning.py
# Cleans and merges all datasets into one analysis-ready DataFrame

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import CHR_COLS, TARGET_COL, FEATURE_COLS, MERGED_FILEPATH


def clean_chr(df):
    """
    Clean the County Health Rankings DataFrame.

    Steps:
    - Keep county-level rows only (statecode != 0, countycode != 0)
    - Rename raw variable codes to human-readable column names
    - Standardize FIPS code to zero-padded 5-character string
    - Keep only relevant columns

    Parameters
    ----------
    df : pd.DataFrame
        Raw CHR DataFrame from load_chr_csv().

    Returns
    -------
    pd.DataFrame
        Cleaned county-level DataFrame.
    """
    # Drop national and state summary rows
    df = df[(df['statecode'] != 0) & (df['countycode'] != 0)].copy()

    # Standardize FIPS to 5-char zero-padded string
    df['fipscode'] = df['fipscode'].astype(str).str.zfill(5)

    # Rename raw columns
    available = {k: v for k, v in CHR_COLS.items() if k in df.columns}
    df = df.rename(columns=available)

    keep_cols = ['fipscode', 'state', 'county'] + list(available.values())
    df = df[[c for c in keep_cols if c in df.columns]]

    print(f'CHR cleaned: {len(df)} counties.')
    return df


def clean_epa(df):
    """
    Clean the EPA AQI DataFrame.

    Steps:
    - Build a FIPS code from State FIPS + County FIPS columns
    - Rename columns to snake_case
    - Keep only FIPS and AQI summary fields

    Parameters
    ----------
    df : pd.DataFrame
        Raw EPA DataFrame from load_epa_csv().

    Returns
    -------
    pd.DataFrame
        Cleaned EPA DataFrame with a fipscode column.
    """
    df = df.copy()
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

    # Build 5-character FIPS
    state_col  = 'state_fips'
    county_col = 'county_fips'

    # AI generated: FIPS construction from separate state/county columns with fallback
    if state_col in df.columns and county_col in df.columns:
        df['fipscode'] = (
            df[state_col].astype(str).str.zfill(2) +
            df[county_col].astype(str).str.zfill(3)
        )
    else:
        # Fallback: try to find FIPS-like column
        fips_candidates = [c for c in df.columns if 'fips' in c]
        if fips_candidates:
            df['fipscode'] = df[fips_candidates[0]].astype(str).str.zfill(5)
        else:
            raise KeyError('Cannot find FIPS columns in EPA dataset.')

    # Keep only FIPS and AQI summary columns
    aqi_cols = [c for c in df.columns if 'aqi' in c or 'days' in c]
    keep = ['fipscode'] + aqi_cols
    df = df[[c for c in keep if c in df.columns]].copy()

    print(f'EPA cleaned: {len(df)} counties.')
    return df


def merge_datasets(chr_df, epa_df=None):
    """
    Merge CHR data with EPA AQI data on county FIPS codes.
    EPA is merged as a left join so counties without AQI data are retained.

    Parameters
    ----------
    chr_df : pd.DataFrame
        Cleaned CHR DataFrame.
    epa_df : pd.DataFrame or None
        Cleaned EPA DataFrame. If None, only CHR data is used.

    Returns
    -------
    pd.DataFrame
        Merged DataFrame.
    """
    if epa_df is not None:
        merged = chr_df.merge(epa_df, on='fipscode', how='left')
        print(f'Merged CHR + EPA: {len(merged)} rows.')
    else:
        merged = chr_df.copy()
        print('No EPA data provided — using CHR only.')

    return merged


def drop_missing(df, subset=None):
    """
    Drop rows with missing values in key analysis columns.

    Parameters
    ----------
    df : pd.DataFrame
    subset : list or None
        Columns to check for NaN. Defaults to TARGET_COL + FEATURE_COLS.

    Returns
    -------
    pd.DataFrame
        DataFrame with NaN rows removed.
    """
    cols = subset or ([TARGET_COL] + FEATURE_COLS)
    cols = [c for c in cols if c in df.columns]
    before = len(df)
    df = df.dropna(subset=cols).copy()
    print(f'Dropped {before - len(df)} rows with missing values. Remaining: {len(df)}.')
    return df


def save_merged(df, filepath=None):
    """Save the merged DataFrame to CSV."""
    path = filepath or MERGED_FILEPATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f'Merged dataset saved to {path}.')


def run_cleaning_pipeline(chr_raw, epa_raw=None):
    """
    Run the full cleaning and merging pipeline.

    Parameters
    ----------
    chr_raw : pd.DataFrame
    epa_raw : pd.DataFrame or None

    Returns
    -------
    pd.DataFrame
        Clean, merged, analysis-ready DataFrame.
    """
    chr_clean = clean_chr(chr_raw)
    epa_clean = clean_epa(epa_raw) if epa_raw is not None else None
    merged    = merge_datasets(chr_clean, epa_clean)
    final     = drop_missing(merged)
    save_merged(final)
    return final
