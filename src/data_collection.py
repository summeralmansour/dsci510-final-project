# src/data_collection.py
# Handles all data fetching: file download and CDC PLACES API calls

import os
import io
import zipfile
import requests
import pandas as pd

# Import constants from config
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import (
    DATA_DIR, CHR_FILEPATH, CHR_URL,
    EPA_FILEPATH, EPA_AQI_URL,
    CDC_PLACES_API_URL, CDC_API_LIMIT
)


def ensure_data_dir():
    """Create data directory if it does not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def download_chr_data(force=False):
    """
    Download the County Health Rankings 2025 analytic supplement CSV.

    Parameters
    ----------
    force : bool
        Re-download even if the file already exists.

    Returns
    -------
    str
        Path to the downloaded CSV file.
    """
    ensure_data_dir()
    if os.path.exists(CHR_FILEPATH) and not force:
        print(f'CHR data already exists: {CHR_FILEPATH}')
        return CHR_FILEPATH

    print('Downloading County Health Rankings data...')
    response = requests.get(CHR_URL, timeout=60)
    response.raise_for_status()

    with open(CHR_FILEPATH, 'wb') as f:
        f.write(response.content)

    print(f'Saved to {CHR_FILEPATH}')
    return CHR_FILEPATH


def download_epa_aqi_data(force=False):
    """
    Download EPA Annual AQI by County (2023) from aqs.epa.gov.
    The file is delivered as a ZIP — this function extracts the CSV inside.

    Parameters
    ----------
    force : bool
        Re-download even if the file already exists.

    Returns
    -------
    str
        Path to the extracted CSV file.
    """
    ensure_data_dir()
    if os.path.exists(EPA_FILEPATH) and not force:
        print(f'EPA data already exists: {EPA_FILEPATH}')
        return EPA_FILEPATH

    print('Downloading EPA Air Quality data...')
    response = requests.get(EPA_AQI_URL, timeout=60)
    response.raise_for_status()

    # AI generated: in-memory ZIP extraction to avoid writing temp files
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        csv_names = [n for n in z.namelist() if n.endswith('.csv')]
        if not csv_names:
            raise ValueError('No CSV found inside EPA ZIP archive.')
        with z.open(csv_names[0]) as csv_file:
            content = csv_file.read()

    with open(EPA_FILEPATH, 'wb') as f:
        f.write(content)

    print(f'Saved to {EPA_FILEPATH}')
    return EPA_FILEPATH


def fetch_cdc_places_api(state_abbr=None, limit=CDC_API_LIMIT):
    """
    Fetch county-level health measures from the CDC PLACES public API.
    No API key is required for this endpoint.

    Parameters
    ----------
    state_abbr : str or None
        Two-letter state abbreviation to filter results (e.g. 'CA').
        If None, fetches all states (uses pagination).
    limit : int
        Number of records per API page request.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: StateAbbr, CountyFIPS, MeasureId, Data_Value.
    """
    # AI generated: pagination loop to collect all records across multiple API pages
    all_records = []
    offset = 0

    while True:
        params = {
            '$limit':  limit,
            '$offset': offset,
            '$select': 'stateabbr,countyfips,measureid,data_value',
        }
        if state_abbr:
            params['$where'] = f"stateabbr='{state_abbr}'"

        print(f'  Fetching CDC PLACES records {offset}–{offset + limit}...')
        response = requests.get(CDC_PLACES_API_URL, params=params, timeout=30)
        response.raise_for_status()

        records = response.json()
        if not records:
            break

        all_records.extend(records)
        offset += limit

        # If we got fewer records than requested, we've reached the end
        if len(records) < limit:
            break

    df = pd.DataFrame(all_records)
    print(f'CDC PLACES API: fetched {len(df)} records.')
    return df


def load_chr_csv(filepath=None):
    """
    Load the County Health Rankings CSV into a DataFrame.

    Parameters
    ----------
    filepath : str or None
        Path to the CSV. Defaults to CHR_FILEPATH from config.

    Returns
    -------
    pd.DataFrame
    """
    path = filepath or CHR_FILEPATH
    df = pd.read_csv(path, dtype={'fipscode': str})
    print(f'Loaded CHR data: {df.shape[0]} rows, {df.shape[1]} columns.')
    return df


def load_epa_csv(filepath=None):
    """
    Load the EPA AQI CSV into a DataFrame.

    Parameters
    ----------
    filepath : str or None
        Path to the CSV. Defaults to EPA_FILEPATH from config.

    Returns
    -------
    pd.DataFrame
    """
    path = filepath or EPA_FILEPATH
    df = pd.read_csv(path)
    print(f'Loaded EPA data: {df.shape[0]} rows, {df.shape[1]} columns.')
    return df
