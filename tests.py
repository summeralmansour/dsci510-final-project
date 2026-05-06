# tests.py
# Unit tests for data loading and analysis functions.
# Run with: python tests.py

import os
import sys
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from src.data_cleaning import clean_chr, drop_missing, merge_datasets
from src.analysis import (
    compute_correlations, compute_correlation_matrix,
    run_kmeans, state_averages, cluster_summary
)


def make_sample_chr():
    """Create a small synthetic CHR-style DataFrame for testing."""
    return pd.DataFrame({
        'statecode':            [1, 1, 1, 2, 2],
        'countycode':           [1, 2, 3, 1, 2],
        'fipscode':             ['01001', '01002', '01003', '02001', '02002'],
        'state':                ['AL', 'AL', 'AL', 'AK', 'AK'],
        'county':               ['A County', 'B County', 'C County', 'D County', 'E County'],
        'v005_rawvalue':        [3000, 2500, 4000, 1800, 2200],
        'v060_rawvalue':        [0.12, 0.10, 0.15, 0.09, 0.11],
        'v070_rawvalue':        [0.30, 0.25, 0.35, 0.20, 0.28],
        'v049_rawvalue':        [0.15, 0.12, 0.18, 0.10, 0.13],
        'v044_rawvalue':        [80,   90,   70,   110,  95 ],
        'v011_rawvalue':        [0.38, 0.35, 0.42, 0.30, 0.36],
        'v009_rawvalue':        [0.18, 0.15, 0.22, 0.12, 0.16],
    })


def make_sample_analysis_df():
    """Create a clean DataFrame ready for analysis functions."""
    np.random.seed(42)
    n = 50
    return pd.DataFrame({
        'state':               np.random.choice(['AL', 'CA', 'TX', 'NY'], n),
        'county':              [f'County {i}' for i in range(n)],
        'premature_death':     np.random.uniform(1500, 5000, n),
        'physical_inactivity': np.random.uniform(0.15, 0.45, n),
        'uninsured_rate':      np.random.uniform(0.05, 0.25, n),
        'adult_obesity':       np.random.uniform(0.25, 0.50, n),
        'adult_smoking':       np.random.uniform(0.10, 0.30, n),
        'diabetes_prevalence': np.random.uniform(0.07, 0.20, n),
    })


class TestDataCleaning(unittest.TestCase):

    def test_clean_chr_removes_state_rows(self):
        """clean_chr should drop rows where statecode or countycode == 0."""
        raw = make_sample_chr()
        # Add a state-level summary row
        summary = raw.iloc[0].copy()
        summary['countycode'] = 0
        raw = pd.concat([raw, pd.DataFrame([summary])], ignore_index=True)
        cleaned = clean_chr(raw)
        self.assertTrue((cleaned['fipscode'].str.len() == 5).all())
        # County 0 rows should be gone
        original_county_count = len(make_sample_chr())
        self.assertEqual(len(cleaned), original_county_count)

    def test_clean_chr_renames_columns(self):
        """clean_chr should rename raw v-codes to human-readable names."""
        cleaned = clean_chr(make_sample_chr())
        self.assertIn('premature_death',     cleaned.columns)
        self.assertIn('physical_inactivity', cleaned.columns)
        self.assertNotIn('v005_rawvalue',    cleaned.columns)

    def test_clean_chr_fips_zero_padded(self):
        """FIPS codes should be 5-character zero-padded strings."""
        cleaned = clean_chr(make_sample_chr())
        self.assertTrue(all(len(f) == 5 for f in cleaned['fipscode']))

    def test_drop_missing_removes_nan_rows(self):
        """drop_missing should remove rows with NaN in key columns."""
        df = make_sample_analysis_df()
        df.loc[0, 'premature_death'] = np.nan
        df.loc[1, 'physical_inactivity'] = np.nan
        cleaned = drop_missing(df)
        self.assertEqual(len(cleaned), len(df) - 2)

    def test_merge_datasets_preserves_chr_rows(self):
        """merge_datasets with no EPA data should return CHR rows unchanged."""
        chr_clean = clean_chr(make_sample_chr())
        merged = merge_datasets(chr_clean, epa_df=None)
        self.assertEqual(len(merged), len(chr_clean))


class TestAnalysis(unittest.TestCase):

    def setUp(self):
        self.df = make_sample_analysis_df()

    def test_compute_correlations_returns_series(self):
        """compute_correlations should return a pandas Series."""
        corr = compute_correlations(self.df)
        self.assertIsInstance(corr, pd.core.series.Series)

    def test_compute_correlations_excludes_target(self):
        """Correlation series should not include the target column itself."""
        corr = compute_correlations(self.df)
        self.assertNotIn('premature_death', corr.index)

    def test_compute_correlation_matrix_is_square(self):
        """Correlation matrix should be square."""
        matrix = compute_correlation_matrix(self.df)
        self.assertEqual(matrix.shape[0], matrix.shape[1])

    def test_run_kmeans_adds_cluster_column(self):
        """run_kmeans should add a 'cluster' column to the DataFrame."""
        cluster_df, _, _ = run_kmeans(self.df)
        self.assertIn('cluster', cluster_df.columns)

    def test_run_kmeans_cluster_values(self):
        """Cluster labels should be 0, 1, 2 only."""
        cluster_df, _, _ = run_kmeans(self.df)
        unique_clusters = set(cluster_df['cluster'].unique())
        self.assertTrue(unique_clusters.issubset({0, 1, 2}))

    def test_state_averages_sorted(self):
        """state_averages should return values in ascending order."""
        avgs = state_averages(self.df)
        self.assertTrue((avgs.values == sorted(avgs.values)).all())

    def test_cluster_summary_shape(self):
        """cluster_summary should have one row per cluster."""
        cluster_df, _, _ = run_kmeans(self.df)
        summary = cluster_summary(cluster_df)
        self.assertEqual(len(summary), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
