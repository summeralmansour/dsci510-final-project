# main.py
# Runs the full project pipeline from data collection to chart generation.
# Usage: python main.py

import os
import sys

from config import CHR_FILEPATH, EPA_FILEPATH

from src.data_collection import (
    download_chr_data, download_epa_aqi_data,
    load_chr_csv, load_epa_csv, fetch_cdc_places_api
)
from src.data_cleaning import run_cleaning_pipeline
from src.analysis import (
    compute_correlation_matrix, compute_correlations,
    run_kmeans, state_averages, cluster_summary
)
from src.visualization import (
    plot_correlation_heatmap, plot_state_comparison,
    plot_scatter_predictors, plot_clusters
)


def main():
    print('=' * 60)
    print('DSCI 510 Final Project — County Health Outcomes Analysis')
    print('Author: Summer Almansour')
    print('=' * 60)

    # ── Step 1: Collect data ──────────────────────────────────────
    print('\n[1/4] Collecting data...')
    download_chr_data()
    try:
        download_epa_aqi_data()
        epa_raw = load_epa_csv()
    except Exception as e:
        print(f'  EPA download failed ({e}). Proceeding without AQI data.')
        epa_raw = None

    # Demonstrate CDC PLACES API call (single state for speed)
    print('  Fetching sample from CDC PLACES API (California)...')
    try:
        cdc_df = fetch_cdc_places_api(state_abbr='CA', limit=100)
        print(f'  CDC PLACES sample: {len(cdc_df)} records.')
    except Exception as e:
        print(f'  CDC PLACES API unavailable: {e}')

    # ── Step 2: Clean and merge ───────────────────────────────────
    print('\n[2/4] Cleaning and merging data...')
    chr_raw = load_chr_csv()
    df = run_cleaning_pipeline(chr_raw, epa_raw)
    print(f'  Final dataset: {len(df)} counties.')

    # ── Step 3: Analysis ──────────────────────────────────────────
    print('\n[3/4] Running analysis...')

    corr_matrix = compute_correlation_matrix(df)
    corr_with_target = compute_correlations(df)
    print('\nTop correlations with Premature Death Rate:')
    print(corr_with_target.head(6).to_string())

    state_avg  = state_averages(df)
    cluster_df, _, _ = run_kmeans(df)

    print('\nCluster summary:')
    print(cluster_summary(cluster_df).to_string())

    # ── Step 4: Visualizations ────────────────────────────────────
    print('\n[4/4] Generating charts...')
    plot_correlation_heatmap(corr_matrix)
    plot_state_comparison(state_avg)
    plot_scatter_predictors(df)
    plot_clusters(cluster_df)

    print('\nDone! Charts saved to results/ folder.')


if __name__ == '__main__':
    main()
