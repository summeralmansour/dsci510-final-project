# src/analysis.py
# Correlation analysis and K-Means clustering

import os
import sys
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import TARGET_COL, FEATURE_COLS, N_CLUSTERS, RANDOM_STATE


def compute_correlations(df, target=TARGET_COL):
    """
    Compute Pearson correlations between all numeric columns and the target.

    Parameters
    ----------
    df : pd.DataFrame
    target : str
        Column name of the outcome variable.

    Returns
    -------
    pd.Series
        Correlation values sorted by absolute magnitude (descending).
    """
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if target not in numeric_cols:
        raise ValueError(f'Target column "{target}" not found in DataFrame.')

    corr = df[numeric_cols].corr()[target].drop(target)
    corr_sorted = corr.reindex(corr.abs().sort_values(ascending=False).index)
    return corr_sorted


def compute_correlation_matrix(df):
    """
    Return the full correlation matrix for numeric columns.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Correlation matrix.
    """
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    return df[numeric_cols].corr()


def run_kmeans(df, features=None, n_clusters=N_CLUSTERS, random_state=RANDOM_STATE):
    """
    Run K-Means clustering on the specified feature columns.
    Features are standardized before clustering.

    Parameters
    ----------
    df : pd.DataFrame
    features : list or None
        Feature column names. Defaults to FEATURE_COLS from config.
    n_clusters : int
    random_state : int

    Returns
    -------
    pd.DataFrame
        Input DataFrame with an added 'cluster' column (0=Low Risk, 1=Moderate, 2=High).
    KMeans
        Fitted KMeans object.
    StandardScaler
        Fitted scaler.
    """
    feature_cols = features or FEATURE_COLS
    feature_cols = [c for c in feature_cols if c in df.columns]

    cluster_df = df.dropna(subset=feature_cols + [TARGET_COL]).copy()

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(cluster_df[feature_cols])

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_df['cluster_raw'] = kmeans.fit_predict(X_scaled)

    # AI generated: re-label clusters by ascending premature death rate so 0 = healthiest
    order = (
        cluster_df.groupby('cluster_raw')[TARGET_COL]
        .mean()
        .sort_values()
        .index
    )
    label_map = {old: new for new, old in enumerate(order)}
    cluster_df['cluster'] = cluster_df['cluster_raw'].map(label_map)
    cluster_df = cluster_df.drop(columns='cluster_raw')

    print(f'K-Means complete. Cluster sizes:')
    print(cluster_df['cluster'].value_counts().sort_index().to_string())
    return cluster_df, kmeans, scaler


def state_averages(df, target=TARGET_COL):
    """
    Compute per-state average of the target column.

    Parameters
    ----------
    df : pd.DataFrame
    target : str

    Returns
    -------
    pd.Series
        State averages sorted ascending (healthiest first).
    """
    return df.groupby('state')[target].mean().sort_values()


def cluster_summary(cluster_df, features=None, target=TARGET_COL):
    """
    Return mean values per cluster for features and target.

    Parameters
    ----------
    cluster_df : pd.DataFrame
        Output of run_kmeans() — must have a 'cluster' column.
    features : list or None
    target : str

    Returns
    -------
    pd.DataFrame
        Mean values per cluster.
    """
    feature_cols = features or FEATURE_COLS
    cols = [c for c in feature_cols + [target] if c in cluster_df.columns]
    summary = cluster_df.groupby('cluster')[cols].mean().round(4)
    summary.index = ['Low Risk', 'Moderate Risk', 'High Risk'][:len(summary)]
    return summary
