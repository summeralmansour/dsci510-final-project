# src/visualization.py
# All chart generation functions using matplotlib and seaborn

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import (
    RESULTS_DIR, TARGET_COL, FEATURE_COLS,
    CORR_HEATMAP_FILE, STATE_CHART_FILE, SCATTER_FILE, CLUSTER_FILE,
    PURPLE_MAIN, PURPLE_DARK, ACCENT_COLOR
)

CLUSTER_COLORS = ['#27AE60', '#F39C12', '#E74C3C']
CLUSTER_LABELS = ['Low Risk', 'Moderate Risk', 'High Risk']


def _save(fig, filepath):
    """Save figure and close it."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {filepath}')


def plot_correlation_heatmap(corr_matrix, filepath=None):
    """
    Plot a correlation heatmap for all numeric health indicators.

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        Correlation matrix (output of compute_correlation_matrix).
    filepath : str or None
        Save path. Defaults to CORR_HEATMAP_FILE from config.
    """
    path = filepath or CORR_HEATMAP_FILE
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        corr_matrix, annot=True, fmt='.2f', cmap='RdPu',
        ax=ax, linewidths=0.5, annot_kws={'size': 9}
    )
    ax.set_title('Correlation Heatmap of County Health Indicators',
                 fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    _save(fig, path)


def plot_state_comparison(state_avg, filepath=None, top_n=10):
    """
    Bar chart showing the top N healthiest and least healthy states.

    Parameters
    ----------
    state_avg : pd.Series
        Per-state average premature death rate (sorted ascending).
    filepath : str or None
    top_n : int
        Number of states to show on each side.
    """
    path = filepath or STATE_CHART_FILE
    top    = state_avg.head(top_n)
    bottom = state_avg.tail(top_n)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    top.plot(kind='barh', ax=axes[0], color=PURPLE_MAIN, alpha=0.85)
    axes[0].set_title(f'{top_n} Healthiest States\n(Lowest Premature Death Rate)',
                      fontweight='bold')
    axes[0].set_xlabel('Avg Premature Death Rate')

    bottom.plot(kind='barh', ax=axes[1], color=ACCENT_COLOR, alpha=0.85)
    axes[1].set_title(f'{top_n} Least Healthy States\n(Highest Premature Death Rate)',
                      fontweight='bold')
    axes[1].set_xlabel('Avg Premature Death Rate')

    fig.suptitle('Premature Death Rate by State', fontsize=13, fontweight='bold')
    plt.tight_layout()
    _save(fig, path)


def plot_scatter_predictors(df, filepath=None):
    """
    Scatter plots of physical inactivity and uninsured rate vs premature death.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain TARGET_COL, 'physical_inactivity', 'uninsured_rate'.
    filepath : str or None
    """
    path = filepath or SCATTER_FILE
    pairs = [
        ('physical_inactivity', PURPLE_MAIN),
        ('uninsured_rate',      '#3FA8A8'),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, (col, color) in zip(axes, pairs):
        valid = df[[col, TARGET_COL]].dropna()
        ax.scatter(valid[col], valid[TARGET_COL],
                   alpha=0.3, color=color, s=10)

        # AI generated: numpy polyfit trend line overlay on scatter plot
        m, b = np.polyfit(valid[col], valid[TARGET_COL], 1)
        x_line = np.linspace(valid[col].min(), valid[col].max(), 100)
        ax.plot(x_line, m * x_line + b, 'r-', linewidth=2)

        r = valid[col].corr(valid[TARGET_COL])
        ax.text(0.05, 0.92, f'r = {r:.2f}',
                transform=ax.transAxes, fontsize=11, color='red')

        label = col.replace('_', ' ').title()
        ax.set_xlabel(label)
        ax.set_ylabel('Premature Death Rate')
        ax.set_title(f'{label} vs Premature Death', fontweight='bold')

    fig.suptitle('Key Predictors of Premature Death Rate',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    _save(fig, path)


def plot_clusters(cluster_df, features=None, filepath=None):
    """
    Scatter plot + bar chart showing K-Means cluster results.

    Parameters
    ----------
    cluster_df : pd.DataFrame
        Must have 'cluster', 'physical_inactivity', TARGET_COL columns.
    features : list or None
        Feature columns to use in the bar chart.
    filepath : str or None
    """
    path     = filepath or CLUSTER_FILE
    feat     = features or FEATURE_COLS
    feat     = [c for c in feat if c in cluster_df.columns]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Scatter
    for c in sorted(cluster_df['cluster'].unique()):
        mask = cluster_df['cluster'] == c
        label = CLUSTER_LABELS[c] if c < len(CLUSTER_LABELS) else f'Cluster {c}'
        axes[0].scatter(
            cluster_df.loc[mask, 'physical_inactivity'],
            cluster_df.loc[mask, TARGET_COL],
            alpha=0.4, color=CLUSTER_COLORS[c % len(CLUSTER_COLORS)],
            label=label, s=12
        )
    axes[0].set_xlabel('Physical Inactivity Rate')
    axes[0].set_ylabel('Premature Death Rate')
    axes[0].set_title('K-Means Clusters (k=3)', fontweight='bold')
    axes[0].legend()

    # Bar chart of cluster means
    means = cluster_df.groupby('cluster')[feat + [TARGET_COL]].mean()
    means.index = CLUSTER_LABELS[:len(means)]
    means.T.plot(kind='bar', ax=axes[1],
                 color=CLUSTER_COLORS[:len(means)], alpha=0.85)
    axes[1].set_title('Average Values by Cluster', fontweight='bold')
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=30, ha='right')
    axes[1].legend(title='Cluster')

    fig.suptitle('County Health Risk Clustering', fontsize=13, fontweight='bold')
    plt.tight_layout()
    _save(fig, path)
