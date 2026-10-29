# Japan IDWR Surveillance Explorer

Interactive explorer for weekly sentinel surveillance reports by prefecture from Japan's Infectious Disease Weekly Report (IDWR), for the 19 sentinel diseases, 2026 weeks 1 to 42. Pick a disease, up to six prefectures and an IDWR week to see:

- **Spatial Statistics:** global Moran's I, LISA clusters, a Moran scatterplot, and Moran's I by week
- **Chart:** weekly reports per sentinel site against the epidemic threshold (1.0) and the caution (10) and warning (30) levels, with EARS C2 alerts
- **Prefecture Map:** Kanto and Kansai, or your selected prefectures, with the rest of Japan faded
- **Japan Map:** all 47 prefectures with a ranked table
- **Alerts:** C2 by prefecture, alert outcomes, and the New Year check
- **Summary Table:** each prefecture's peak and first C2 alert. For influenza only: first week at 1.0, lead time and false alarms

The app file is `app.py`. Its version is in the file header and on screen, never in the file name.

## Layout

```
app.py                            the Streamlit app
requirements.txt
.streamlit/config.toml            theme, minimal toolbar, static serving
data/idwr_weekly.csv              weekly table written by the IDWR alert report R script (required)
data/prefecture_population.csv    2020 census population by prefecture (e-Stat), reference only
data/prefecture_names.csv         pref_code with English and Japanese names
static/japan_prefectures_display.geojson  map outlines (dataofjapan/land; small outlying islands dropped, simplified)
static/prefecture_labels.csv      label position for each prefecture
static/world_110m.json            Plotly world outline file, served locally so maps draw without the CDN
static/prefecture_neighbors.json  spatial weights built from the full-resolution boundaries
tools/build_neighbors.py          rebuilds the neighbors file (run locally; needs geopandas)
tests/test_app.py                 Streamlit AppTest script
sample/idwr_weekly_sample.csv     synthetic table for layout work only; do not upload
```

## Data contract for `data/idwr_weekly.csv`

One row per prefecture per ISO week per disease. No national row.

| column | type | note |
|---|---|---|
| year | int | ISO year |
| week | int | ISO week |
| week_start | date | Monday, YYYY-MM-DD |
| pref_code | int | 1 Hokkaido to 47 Okinawa (JIS X 0401) |
| prefecture | text | English name, as in `data/prefecture_names.csv` |
| disease | text | "Influenza", ... |
| per_sentinel | float | reports per sentinel site |
| sentinels | int | recommended; reporting sentinel sites that week |
| c2 | float | optional; EARS C2 from the R script |

Rows with a code outside 1 to 47 are dropped and reported on screen. If `c2` is missing, or New Year weeks are left out of the baselines (the default), the app computes C2 with the R report's rules: baseline weeks t-9 to t-3, two-week guard, population SD with a floor of 0.1, at least 5 baseline weeks, alert at 3 or more.

## Run locally

```
pip install -r requirements.txt
streamlit run app.py                    # needs data/idwr_weekly.csv
JIE_SAMPLE=1 streamlit run app.py       # layout work only, with the synthetic sample
JIE_SAMPLE=1 python -m pytest tests -q
```

Without `data/idwr_weekly.csv` and without `JIE_SAMPLE=1`, the app shows a message and stops. With the sample, the title, a banner and every chart and map are marked SAMPLE DATA.

AppTest does not render the page. After any visual change, look at the app in a browser, and retake screenshots used in slides or write-ups whenever the version changes.

## Deploy

1. Add `data/idwr_weekly.csv` from the R script.
2. Upload everything except the `sample/` folder at `https://github.com/SpatialHealthInformatics/japan-influenza-explorer/upload/main`.
3. On https://share.streamlit.io choose the repository, branch `main`, main file `app.py`. Do not set `JIE_SAMPLE`.
4. Open the app after one to two minutes and link it from the influenza page on the portfolio site.

## Sources

- IDWR weekly sentinel reports by prefecture, Japan Institute for Health Security (JIHS).
- Prefecture boundaries: dataofjapan/land (GitHub). For display, islands under 5 km2 or more than 150 km from a prefecture's main island are dropped and the outlines simplified at 0.004 degrees; Okinawa is drawn in an inset. Spatial weights come from the full-resolution file, because simplifying dropped two real borders (Tochigi-Saitama, Tottori-Hiroshima).
- Population: 2020 Population Census, e-Stat.
- EARS C2: Hutwagner et al., 2003.


The 1.0 epidemic level, the 10 and 30 levels, onset, lead time and false alarms apply to influenza only. Public IDWR data only.
