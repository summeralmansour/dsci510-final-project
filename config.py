# config.py — all project constants, paths, and URLs

import os

# ── Directory paths ────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
SRC_DIR     = os.path.join(BASE_DIR, 'src')

# ── Data file names ────────────────────────────────────────────────────────
CHR_FILENAME  = 'county_health_rankings_2025.csv'
CHR_FILEPATH  = os.path.join(DATA_DIR, CHR_FILENAME)

EPA_FILENAME  = 'epa_air_quality_2023.csv'
EPA_FILEPATH  = os.path.join(DATA_DIR, EPA_FILENAME)

MERGED_FILENAME = 'merged_county_health.csv'
MERGED_FILEPATH = os.path.join(DATA_DIR, MERGED_FILENAME)

# ── Data source URLs ───────────────────────────────────────────────────────
# County Health Rankings 2025 analytic supplement (direct download)
CHR_URL = (
    'https://www.countyhealthrankings.org/sites/default/files/media/document/'
    'analytic_supplement_20260325_1_.csv'
)

# CDC PLACES API — county-level chronic disease measures (no API key required)
CDC_PLACES_API_URL = 'https://data.cdc.gov/resource/cwsq-ngmh.json'
CDC_API_LIMIT      = 1000  # records per page

# EPA Air Quality Annual Summary 2023 (direct download)
EPA_AQI_URL = (
    'https://aqs.epa.gov/aqsweb/airdata/annual_aqi_by_county_2023.zip'
)

# ── Column mappings — CHR raw codes → human-readable names ────────────────
CHR_COLS = {
    'v005_rawvalue': 'premature_death',
    'v060_rawvalue': 'diabetes_prevalence',
    'v070_rawvalue': 'physical_inactivity',
    'v049_rawvalue': 'uninsured_rate',
    'v044_rawvalue': 'primary_care_ratio',
    'v011_rawvalue': 'adult_obesity',
    'v009_rawvalue': 'adult_smoking',
}

# ── Analysis settings ──────────────────────────────────────────────────────
TARGET_COL       = 'premature_death'
FEATURE_COLS     = ['physical_inactivity', 'uninsured_rate', 'adult_obesity', 'adult_smoking']
N_CLUSTERS       = 3
RANDOM_STATE     = 42

# ── Result file names ──────────────────────────────────────────────────────
CORR_HEATMAP_FILE   = os.path.join(RESULTS_DIR, 'correlation_heatmap.png')
STATE_CHART_FILE    = os.path.join(RESULTS_DIR, 'state_comparison.png')
SCATTER_FILE        = os.path.join(RESULTS_DIR, 'scatter_predictors.png')
CLUSTER_FILE        = os.path.join(RESULTS_DIR, 'kmeans_clusters.png')

# ── Chart style ────────────────────────────────────────────────────────────
PURPLE_MAIN  = '#7b3fa8'
PURPLE_DARK  = '#3D1A6E'
ACCENT_COLOR = '#E74C8B'
