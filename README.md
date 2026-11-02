# Japan IDWR Surveillance Explorer

**Open the app:** https://japan-idwr-explorer.streamlit.app

An interactive explorer for weekly sentinel surveillance reports by prefecture from Japan's Infectious Disease Weekly Report (IDWR). It covers the 19 sentinel diseases, 2026 weeks 1 to 42. The app is available in English and Japanese (日本語). Use the language switch at the top of the sidebar.

Pick a disease, up to six prefectures and an IDWR week to see:

- **Spatial Statistics:** global Moran's I, LISA clusters, a Moran scatterplot, and Moran's I by week
- **Chart:** weekly reports per sentinel site against the epidemic threshold (1.0) and the caution (10) and warning (30) levels, with EARS C2 alerts
- **Prefecture Map:** Kanto and Kansai, or your selected prefectures, with the rest of Japan faded
- **Japan Map:** all 47 prefectures with a ranked table
- **Alerts:** C2 by prefecture, alert outcomes, and the New Year check
- **Summary Table:** each prefecture's peak and first C2 alert. For influenza only: first week at 1.0, lead time and false alarms

The 1.0 epidemic level, the 10 and 30 levels, onset, lead time and false alarms apply to influenza only.

## Data

This app uses public IDWR data only. The TriNetX data used in the JSPID comparison is not public, so it is not included. If it becomes available for sharing, it will be added here.

The weekly table has one row per prefecture, ISO week and disease, with reports per sentinel site. It follows the rules of the IDWR alert report: EARS C2 with baseline weeks t-9 to t-3, a two-week guard, a population standard deviation with a floor of 0.1, at least 5 baseline weeks, and an alert at 3 or more.

## Sources

- IDWR weekly sentinel reports by prefecture, Japan Institute for Health Security (JIHS).
- Prefecture boundaries: dataofjapan/land (GitHub). For display, small outlying islands are dropped and the outlines simplified. Okinawa is drawn in an inset. Spatial weights come from the full-resolution boundaries.
- Population: 2020 Population Census, e-Stat.
- EARS C2: Hutwagner et al., 2003.

Copyright 2026 SpatialHealthInformatics
