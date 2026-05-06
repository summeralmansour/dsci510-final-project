# Analyzing U.S. County-Level Health Outcomes
**DSCI 510 – Spring 2026 | University of Southern California**
**Author: Summer Almansour**

---

## Introduction

This project analyzes the relationship between U.S. county-level health outcomes and key behavioral, environmental, and socioeconomic factors. Using data from the County Health Rankings, the CDC PLACES API, and the EPA Air Quality Annual Summary, the project explores which factors most strongly predict premature death rates across U.S. counties, and whether counties cluster into distinct health risk profiles.

---

## Data Sources

| # | Dataset | Source URL | Type | Key Fields | Est. Size |
|---|---------|-----------|------|-----------|-----------|
| 1 | County Health Rankings 2025 | countyhealthrankings.org | CSV File | Premature death, diabetes, physical inactivity, uninsured rate, obesity, smoking | ~3,200 counties |
| 2 | CDC PLACES API | data.cdc.gov/resource/cwsq-ngmh.json | API (JSON) | Chronic disease measures by county — obesity, smoking, checkup rates | 500+ measures, 3,100+ counties |
| 3 | EPA Air Quality Annual Summary | aqs.epa.gov/aqsweb/airdata | CSV File (ZIP) | Median AQI, days good/unhealthy, max AQI per county | ~1,000+ counties |

---

## Analysis

The project performs the following analyses:

1. **Correlation Analysis** — Pearson correlation between each behavioral/environmental factor and premature death rate to identify the strongest predictors.
2. **State-Level Comparison** — Average premature death rates aggregated by state to identify healthiest and least healthy states.
3. **Scatter Plot Regression** — Scatter plots with trend lines for the two strongest predictors (physical inactivity, uninsured rate) vs premature death rate.
4. **K-Means Clustering (k=3)** — Counties are grouped into Low Risk, Moderate Risk, and High Risk clusters based on standardized behavioral features.

---

## Summary of Results

- **Physical inactivity** (r=0.42) and **diabetes prevalence** (r=0.40) are the strongest predictors of premature death rate.
- **Healthiest states**: ID, HI, CO, WA, UT — characterized by lower inactivity rates and better access to care.
- **Least healthy states**: WV, LA, AL, MS, GA — higher poverty, physical inactivity, and uninsured rates.
- **K-Means clustering** identified three distinct county health profiles:
  - **Low Risk** (640 counties): avg premature death rate 2,327
  - **Moderate Risk** (1,344 counties): avg premature death rate 2,823
  - **High Risk** (859 counties): avg premature death rate 3,468

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/summeralmansour/dsci510-final-project.git
cd dsci510-final-project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables (optional)
```bash
cp .env.example .env
# Edit .env with your API keys if needed
```

### 4. Run the full pipeline
```bash
python main.py
```

This will:
- Download the County Health Rankings CSV from countyhealthrankings.org
- Download the EPA AQI CSV from aqs.epa.gov
- Fetch a sample from the CDC PLACES API
- Clean and merge all datasets
- Run correlation analysis and K-Means clustering
- Save all charts to the `results/` folder

### 5. Run the Jupyter notebook (optional)
```bash
jupyter notebook results.ipynb
```

### 6. Run unit tests
```bash
python tests.py
```

---

## Project Structure

```
dsci510-final-project/
├── src/
│   ├── data_collection.py   # Data downloading and API calls
│   ├── data_cleaning.py     # Pandas cleaning and merging
│   ├── analysis.py          # Correlation analysis and K-Means clustering
│   └── visualization.py     # Matplotlib/Seaborn chart functions
├── docs/
│   ├── Summer_Almansour_progress_report.pdf
│   └── Summer_Almansour_presentation.pdf
├── data/                    # Empty — data is downloaded at runtime
├── results/                 # Generated charts (gitignored)
├── config.py                # All constants, paths, and URLs
├── main.py                  # Runs full pipeline end-to-end
├── tests.py                 # Unit tests
├── results.ipynb            # Jupyter notebook
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

---

## AI Usage

This project used AI assistance (Claude by Anthropic) during development.

---

## API Keys

This project uses the CDC PLACES public API which does not require a key. If you wish to use a personal API key for higher rate limits, add it to your `.env` file as `CDC_API_KEY`. See `.env.example` for the full list of optional environment variables.
