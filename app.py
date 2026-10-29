# =============================================================================
# Japan IDWR Surveillance Explorer (Streamlit web app)
# Author:   Genie Tang (gtang10@jh.edu)
# Script:   app.py
# Version:  v2
#
# Version log
#   v2 (2026-10-29): Map labels for Osaka, Wakayama, Kanagawa and Chiba moved off the
#       borders and onto open sea or their own land (static/prefecture_labels.csv).
#   v1 (2026-10-29): New app for all 19 IDWR sentinel diseases, built from the
#       Japan Influenza Surveillance Explorer v12. data/idwr_weekly.csv now holds
#       2026 weeks 1 to 42 for every disease, read from the week 42 yearly
#       prefecture file (teiten-tougai). EARS C2, the maps and the spatial
#       statistics work for every disease. The 1.0 epidemic level, the 10 and 30
#       levels, the onset, lead time and false-alarm measures apply to
#       influenza only, so other diseases show alerts without them. Each disease
#       carries a note on its sentinel scheme.
#   v12 (2026-10-28, influenza app): The red outlines for prefectures with a C2 alert are off
#       by default on the Prefecture Map and Japan Map. In a rising week most
#       prefectures alert (35 of 47 in 2026 week 41), so the red lines crowded
#       the maps. A switch above each map turns them back on; alerts still
#       show in the hover text, the ranked table and the Alerts tab.
#       Maps restyled to match the JSPID map slides: warm colors (cream to
#       dark red), light blue sea, thin gray borders, prefecture names and
#       values on the map, neighbors faded in their own color, small outlying
#       islands left off, Okinawa in an inset. Selected prefectures are
#       outlined in dark blue. Maps use Plotly geo with the world outline file
#       bundled in static/, as in the capstone.
#   v11 (2026-10-28): The third tab is named "Prefecture Map" (was "Map"), so
#       it reads clearly next to "Japan Map". A caption under each map of all
#       of Japan explains the small outlying islands (Tokyo's Izu and
#       Ogasawara islands, Kagoshima's Amami islands, Okinawa). Map outlines
#       are thinner (selected prefectures 1.4 px, alerting prefectures 1.6 px)
#       so they don't hide small prefectures.
#   v10 (2026-10-28): Moran scatterplot labels for the selected prefectures
#       alternate above and below their points, so neighboring labels (Nara and
#       Osaka) no longer overlap. The fourth Spatial Statistics card names the
#       neighbor rule in full: shared border, plus three sea links.
#   v9 (2026-10-28): Real data. data/idwr_weekly.csv holds IDWR reports per
#       sentinel site for all 47 prefectures, 2026 weeks 20 to 41, from the
#       prefecture table written by the IDWR alert report R script (v14,
#       2026-10-20). Summary Table follows the Weeks shown range and uses the
#       R script's onset rule (start of the unbroken run at or above 1.0 that
#       contains the peak); first alert counts from 8 weeks before the onset.
#       Checked against the R output: first alert, onset and lead agree for
#       all 47 prefectures (43 alert first, 3 same week, 1 after; median 2).
#   v8 (2026-10-28): Data notice in a lavender box (light and dark theme
#       colors from the handoff, section 9): the full notice at the top of the
#       About the Data tab, and the one-line version under the app title.
#   v7 (2026-10-28): The app runs only on the real table (data/idwr_weekly.csv).
#       The synthetic sample sits in sample/, outside data/, and loads only
#       when the environment variable JIE_SAMPLE=1 is set; it is then marked on
#       the title, in a banner and across every chart and map. New Year weeks
#       (52, 53, 1) are left out of C2 baselines by default, and the Alerts tab
#       reports how many alerts in weeks 2 to 8 that removes. Geography check:
#       rows outside prefecture codes 1 to 47 (for example a national row) are
#       dropped and reported. False alarms sit next to the lead in the Summary
#       Table. About the Data states that the alerts are retrospective.
#   v6 (2026-10-28): Layout, styling and controls follow the course capstone
#       (capstone.py v48): page title and subtitle with the version; sidebar
#       with "Add a prefecture" and an Add button, the selected list, and
#       Display options; Title Case tabs (Spatial Statistics, Chart,
#       Prefecture Map, Japan Map, Alerts, Summary Table, User Guide, About the
#       Data; Japan Map takes the place of the capstone's World Map); white tiles with a color swatch on the Chart tab; four
#       tinted cards in the portfolio colors on Spatial Statistics; Century
#       Gothic with Didact Gothic as the fallback in the page and in every
#       chart; one chart or one panel per prefecture; a week-range slider;
#       a download button for the plotted data; an alert-threshold slider and
#       one panel per prefecture on the Alerts tab; a Reset map view button
#       above every map with a hint below it; selected prefectures outlined in
#       orange, alerting prefectures in red; 999 permutations for Moran's I
#       and LISA.
#   v5 (2026-10-28): Tabs reordered to follow the capstone. Summary table with
#       the season peak, first week at 1.0, first C2 alert and the lead.
#   v4 (2026-10-28): Kanto, Kansai, and Kanto and Kansai side by side, with
#       the rest of Japan faded; five IDWR color bands.
#   v3 (2026-10-28): EARS C2 matches the IDWR alert report R script (weeks
#       t-9 to t-3, two-week guard, population SD floored at 0.1, at least 5
#       baseline weeks), checked to 14 decimal places against the R output.
#       False-alarm count. Epidemic threshold line at 1.0. Optional sentinels
#       column. Spatial weights from the full-resolution boundaries with
#       Hokkaido-Aomori, Okinawa-Kagoshima and Fukuoka-Yamaguchi links.
#       Option to drop New Year weeks from C2 baselines.
#   v2 (2026-10-28): numpy seeded for global Moran's I; allowed-button toolbars.
#   v1 (2026-10-28): First version.
#
# How to run locally
#   pip install -r requirements.txt
#   streamlit run app.py
#
# Data contract: data/idwr_weekly.csv, written by the IDWR alert report R
# script, one row per prefecture per week per disease. Required columns:
# year, week, week_start, pref_code, prefecture, disease, per_sentinel.
# Optional: sentinels, c2, alert. Without that file the app reads
# nothing: it stops with a message. For layout work only, JIE_SAMPLE=1 loads
# sample/idwr_weekly_sample.csv, a synthetic file that must never be deployed.
# =============================================================================

from pathlib import Path
import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import streamlit as st

VERSION = "v2"
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"
IDWR_URL = "https://id-info.jihs.go.jp/surveillance/idwr/"
SAMPLE_PATH = ROOT / "sample" / "idwr_weekly_sample.csv"
ALLOW_SAMPLE = os.environ.get("JIE_SAMPLE") == "1"

FONT_STACK = "Century Gothic, CenturyGothic, AppleGothic, Didact Gothic, sans-serif"
pio.templates["appfont"] = go.layout.Template(layout=dict(font=dict(family=FONT_STACK)))
pio.templates.default = "plotly_white+appfont"

# One fixed color per prefecture, kept while it is selected. The palette passes
# a colorblind separation check for adjacent pairs, so the selection is capped at six.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
MAX_SELECT = len(PALETTE)
INK, INK_SOFT, GRID = "#1f2933", "#52514e", "#e6e6e2"
SELECT_OUTLINE = "#eb6834"
ALERT_RED = "#b03030"

# Data notice (handoff section 9). Wording is fixed; change it only in the same
# version that adds a newly shareable source, so the app never states something
# that is no longer true.
NOTICE_FULL = ("This app uses public IDWR data only. The TriNetX pediatric influenza data used in the JSPID "
               "comparison is not included, because it is not public data. If it becomes available for "
               "sharing, it will be added here.")
NOTICE_LINE = "Public IDWR data only. The TriNetX comparison is not included."
NOTICE_COLORS = {"light": ("#efe9fb", "#d3c8f2", "#2e2557"), "dark": ("#2a2547", "#4a4177", "#e6e0fa")}

EPIDEMIC = 1.0
THRESHOLDS = {"Influenza": {"Epidemic": 1, "Caution": 10, "Warning": 30}}
CHANGED = ("Sentinel scheme changed in April 2025, when acute respiratory infection (ARI) surveillance began and "
           "the number of sentinel sites fell. Trends need care, because the size of the gap between the old and "
           "new systems is not yet clear.")
PEDIATRIC = ("Pediatric sentinel scheme, not part of the April 2025 ARI change. To be confirmed with JIHS.")
DISEASE_NOTES = {
    "Influenza": CHANGED, "COVID-19": CHANGED,
    "RSV infection": PEDIATRIC, "Group A streptococcal pharyngitis": PEDIATRIC,
    "Herpangina": PEDIATRIC, "Mycoplasma pneumonia": PEDIATRIC,
}
DEFAULT_NOTE = "Sentinel scheme not yet checked for this disease."
HOLIDAY_WEEKS = {52, 53, 1}
FA_WINDOW = 4  # weeks after an alert in which a crossing of 1.0 counts as "followed"
C2_BASELINE, C2_GUARD, C2_MIN_WEEKS, C2_SD_FLOOR = 7, 2, 5, 0.1
PERMUTATIONS = 999

# Warm map colors, the same as the JSPID map slides: cream, orange, red, dark red.
SEQ_SCALE = [[0, "#fee08b"], [0.3, "#fc8d59"], [0.6, "#e34a33"], [0.85, "#b30000"], [1, "#67000d"]]
# Five bands: under the epidemic threshold, then steps of 10 up to the warning level.
LEVEL_EDGES = [-np.inf, 1, 10, 20, 30, np.inf]
LEVEL_LABELS = ["Under 1.0", "1.0 to 9.99", "10.0 to 19.99", "20.0 to 29.99", "30.0 and over"]
LEVEL_COLORS = ["#fee08b", "#fc8d59", "#e34a33", "#b30000", "#67000d"]
SEA = "#d6eaf8"           # light blue sea, as on the JSPID maps
BORDER = "#555555"        # thin dark gray prefecture borders
FADE_OPACITY = 0.35       # prefectures outside the chosen area keep their color, faded
MAP_SELECT = "#1D3F73"    # dark blue outline for selected prefectures on the warm maps
MAP_ALERT = "#111111"     # black outline for C2 alerts on the warm maps
ISLANDS_NOTE = ("Small outlying islands are left off the maps (for example Ogasawara and Amami); "
                "Okinawa is shown in the inset box.")
CLUSTER_COLORS = {"High-High": "#b03030", "Low-Low": "#1f63a8", "High-Low": "#e8a0a0",
                  "Low-High": "#9dc3ea", "Not significant": "#e9ecef"}
CLUSTER_ORDER = list(CLUSTER_COLORS)
VIEWS = {
    "All Japan": dict(codes=list(range(1, 48)), lon=(128.2, 149.2), lat=(30.3, 45.75)),
    "Kanto (Tokyo area)": dict(codes=[8, 9, 10, 11, 12, 13, 14], lon=(138.3, 141.05), lat=(34.85, 37.15)),
    "Kansai (Osaka area)": dict(codes=[25, 26, 27, 28, 29, 30], lon=(134.2, 136.95), lat=(33.4, 35.85)),
}

# Toolbars: an explicit list of allowed buttons, so only buttons that act on the
# click can appear and Plotly's "Share chart" upload button cannot return.
CHARTCFG = {"displayModeBar": True, "displaylogo": False, "scrollZoom": False,
            "modeBarButtons": [["toImage", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"]],
            "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "japan_idwr_chart"}}
MAPCFG = {"displayModeBar": True, "displaylogo": False, "scrollZoom": True,
          "modeBarButtons": [["toImage", "zoomInGeo", "zoomOutGeo", "resetGeo"]],
          "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "japan_idwr_map"}}
# Plotly downloads a world outline file for every geo map from its CDN. A copy
# ships in static/ and Streamlit serves it (enableStaticServing), so the maps
# draw even where the CDN is blocked.
if (STATIC_DIR / "world_110m.json").exists():
    MAPCFG["topojsonURL"] = "app/static/"
OKINAWA = 47
INSET = dict(lon=(126.95, 128.45), lat=(26.0, 26.95), x=(0.70, 0.97), y=(0.03, 0.30))


# ---- Data loading and cleaning ----------------------------------------------
def ears_c2(x: np.ndarray, skip: np.ndarray) -> np.ndarray:
    """EARS C2 for one weekly series on a complete date grid (gaps are NaN).

    Baseline = weeks t-9 to t-3, so weeks t-2 and t-1 form the two-week guard.
    Population SD with a floor of 0.1; at least 5 baseline weeks. Weeks flagged
    in `skip` count as missing in the baseline. Same rules as the R alert report.
    """
    c2 = np.full(len(x), np.nan)
    base = np.where(skip, np.nan, x)
    for i in range(C2_BASELINE + C2_GUARD, len(x)):
        if np.isnan(x[i]):
            continue
        ref = base[i - C2_BASELINE - C2_GUARD: i - C2_GUARD]
        ref = ref[~np.isnan(ref)]
        if len(ref) < C2_MIN_WEEKS:
            continue
        c2[i] = (x[i] - ref.mean()) / max(ref.std(ddof=0), C2_SD_FLOOR)
    return c2


def alert_outcomes(x: np.ndarray, alert: np.ndarray) -> np.ndarray:
    """Classify each alert week: 'above 1.0', 'followed' (1.0 reached within
    4 weeks), 'false' (not reached), or 'pending' (too few weeks to tell)."""
    out = np.full(len(x), "", dtype=object)
    for i in np.where(alert)[0]:
        if x[i] >= EPIDEMIC:
            out[i] = "above 1.0"
        elif np.nanmax(x[i: i + FA_WINDOW + 1]) >= EPIDEMIC:
            out[i] = "followed"
        elif i + FA_WINDOW >= len(x):
            out[i] = "pending"
        else:
            out[i] = "false"
    return out


ONSET_LOOKBACK = 8  # weeks before the onset in which a C2 alert counts as the season's first alert


def onset_and_first_alert(x: np.ndarray, alert: np.ndarray, c2: np.ndarray):
    """Return (onset index, first alert index) for one prefecture over a window.

    Onset: the first week of the unbroken run at or above 1.0 that contains the
    peak, so a single isolated week at 1.0 earlier on is not counted. Same rule
    as the IDWR alert report R script (v14) for the 2026 prefecture table.
    First alert: the first C2 alert from 8 weeks before the onset onward. None
    when C2 had too little history before the onset to be judged.
    """
    if not np.isfinite(x).any():
        return None, None
    pk = int(np.nanargmax(x))
    if not x[pk] >= EPIDEMIC:
        return None, None
    on = pk
    while on > 0 and x[on - 1] >= EPIDEMIC:
        on -= 1
    has = np.where(~np.isnan(c2))[0]
    if not len(has) or has[0] >= on:
        return on, None
    cand = np.where(alert & (np.arange(len(x)) >= on - ONSET_LOOKBACK))[0]
    return on, (int(cand[0]) if len(cand) else None)


@st.cache_data(show_spinner="Loading IDWR weekly reports...")
def load_weekly(drop_holidays: bool, threshold: float, allow_sample: bool):
    """Return (weekly frame, is_sample, c2 taken from the R output, geography notes).

    1. Read the weekly table (one row per prefecture, week and disease).
    2. Floor reports per sentinel at zero.
    3. Put each prefecture on a complete weekly grid, so a missing week shows
       as a gap and cannot shift the C2 baseline.
    4. Use the R script's c2 column when present; otherwise compute C2 here.
    5. Alert when C2 reaches the threshold; classify each alert.

    Geography: only prefecture codes 1 to 47 are kept. A national row (or any
    other code) is dropped and reported, so it can never enter a sum, a map
    or the spatial weights. Names are checked against data/prefecture_names.csv.
    """
    real = DATA_DIR / "idwr_weekly.csv"
    if real.exists():
        path = real
    elif allow_sample:
        path = SAMPLE_PATH
    else:
        raise FileNotFoundError("data/idwr_weekly.csv")
    raw = pd.read_csv(path, parse_dates=["week_start"])
    notes = []
    bad = ~raw["pref_code"].between(1, 47)
    if bad.any():
        notes.append(f"{int(bad.sum())} rows with codes outside 1 to 47 were dropped "
                     f"({', '.join(sorted(raw.loc[bad, 'prefecture'].astype(str).unique()))}).")
        raw = raw[~bad]
    names = pd.read_csv(DATA_DIR / "prefecture_names.csv").set_index("pref_code")["prefecture"]
    given = raw.drop_duplicates("pref_code").set_index("pref_code")["prefecture"]
    mismatch = [c for c in given.index if given[c] != names.get(c)]
    if mismatch:
        notes.append("Names differ from the code list for codes " + ", ".join(map(str, mismatch))
                     + "; the code list names are used.")
        raw["prefecture"] = raw["pref_code"].map(names)
    missing = sorted(set(names.index) - set(given.index))
    if missing:
        notes.append(f"{len(missing)} prefectures have no rows: " + ", ".join(names[c] for c in missing) + ".")
    raw["per_sentinel"] = raw["per_sentinel"].clip(lower=0)
    use_r_c2 = "c2" in raw.columns and not drop_holidays

    parts = []
    for (dis, code), g in raw.groupby(["disease", "pref_code"], sort=False):
        g = g.set_index("week_start").sort_index()
        g = g.reindex(pd.date_range(g.index.min(), g.index.max(), freq="7D"))
        g.index.name = "week_start"
        g["disease"], g["pref_code"] = dis, code
        g["prefecture"] = g["prefecture"].ffill().bfill()
        iso = g.index.isocalendar()
        g["year"] = g["year"].fillna(iso["year"]).astype(int)
        g["week"] = g["week"].fillna(iso["week"]).astype(int)
        x = g["per_sentinel"].to_numpy(dtype=float)
        if not use_r_c2:
            skip = g["week"].isin(HOLIDAY_WEEKS).to_numpy() if drop_holidays else np.zeros(len(g), bool)
            g["c2"] = ears_c2(x, skip)
        g["alert"] = (g["c2"] >= threshold).fillna(False).astype(bool)
        g["alert_outcome"] = alert_outcomes(x, g["alert"].to_numpy()) if dis in THRESHOLDS else "not rated"
        parts.append(g.reset_index())
    df = pd.concat(parts, ignore_index=True)
    df["week_label"] = df["year"].astype(str) + "-W" + df["week"].astype(str).str.zfill(2)
    df["season"] = np.where(df["week"] >= 36, df["year"], df["year"] - 1)
    return df, path == SAMPLE_PATH, use_r_c2, notes


@st.cache_data
def week_check(df: pd.DataFrame) -> int:
    """Number of weeks whose year-week label differs from the ISO week of week_start."""
    w = df.drop_duplicates("week_start")[["week_start", "year", "week"]].dropna()
    iso = w["week_start"].dt.isocalendar()
    bad = ((iso["year"].to_numpy() != w["year"].to_numpy()) | (iso["week"].to_numpy() != w["week"].to_numpy())
           | (w["week_start"].dt.dayofweek.to_numpy() != 0))
    return int(bad.sum())


@st.cache_data
def load_geo():
    # Display boundaries: dataofjapan/land, small outlying islands dropped, simplified.
    with open(STATIC_DIR / "japan_prefectures_display.geojson", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_labels() -> pd.DataFrame:
    """Label position for each prefecture (a point inside its largest island)."""
    return pd.read_csv(STATIC_DIR / "prefecture_labels.csv").set_index("pref_code")


@st.cache_data
def load_neighbors() -> dict:
    with open(STATIC_DIR / "prefecture_neighbors.json", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f)["neighbors"].items()}


@st.cache_data
def load_population() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "prefecture_population.csv")


@st.cache_data
def pref_bounds() -> dict:
    """lon/lat bounding box of each prefecture, used to zoom to a selection."""
    out = {}
    for f in load_geo()["features"]:
        pts = []

        def walk(c):
            if isinstance(c[0], (int, float)):
                pts.append(c)
            else:
                for part in c:
                    walk(part)
        walk(f["geometry"]["coordinates"])
        a = np.array(pts)
        out[int(f["properties"]["pref_code"])] = (a[:, 0].min(), a[:, 0].max(), a[:, 1].min(), a[:, 1].max())
    return out


def fit_view(codes):
    b = np.array([pref_bounds()[c] for c in codes])
    lon0, lon1, lat0, lat1 = b[:, 0].min(), b[:, 1].max(), b[:, 2].min(), b[:, 3].max()
    pad_lon, pad_lat = max(0.25, (lon1 - lon0) * 0.08), max(0.2, (lat1 - lat0) * 0.08)
    return dict(lon=(lon0 - pad_lon, lon1 + pad_lon), lat=(lat0 - pad_lat, lat1 + pad_lat))


@st.cache_data(show_spinner="Running Moran's I and LISA...")
def spatial_stats(values: tuple, codes: tuple):
    """Global Moran's I and local Moran (LISA) on reports per sentinel for one week.

    Weights: prefectures that share a border (queen contiguity, full-resolution
    boundaries) plus three sea links, row-standardized. 999 permutations.
    """
    from libpysal.weights import W
    from esda.moran import Moran, Moran_Local
    nb = load_neighbors()
    w = W({k: nb[k] for k in codes}, id_order=list(codes), silence_warnings=True)
    w.transform = "r"
    y = np.array(values, dtype=float)
    # esda's global Moran has no seed argument, so the permutation draw is
    # seeded through numpy to make the p-value repeat between runs.
    np.random.seed(12345)
    gm = Moran(y, w, permutations=PERMUTATIONS)
    lm = Moran_Local(y, w, permutations=PERMUTATIONS, seed=12345)
    z = (y - y.mean()) / y.std()
    labels = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
    out = pd.DataFrame({"pref_code": codes, "value": y, "z": z, "lag": w.sparse @ z, "p": lm.p_sim,
                        "cluster": [labels[q] if p < 0.05 else "Not significant" for q, p in zip(lm.q, lm.p_sim)]})
    return out, float(gm.I), float(gm.p_sim), float(gm.EI)


@st.cache_data(show_spinner="Running Moran's I for every week...")
def moran_by_week(frame: pd.DataFrame, codes: tuple):
    from libpysal.weights import W
    from esda.moran import Moran
    nb = load_neighbors()
    w = W({k: nb[k] for k in codes}, id_order=list(codes), silence_warnings=True)
    w.transform = "r"
    np.random.seed(12345)
    rows = []
    for lbl, grp in frame.groupby("week_label", sort=False):
        vals = grp.set_index("pref_code").reindex(list(codes))["per_sentinel"]
        if vals.isna().any() or vals.std() == 0:
            continue
        mi = Moran(vals.to_numpy(), w, permutations=PERMUTATIONS)
        rows.append(dict(week_label=lbl, week_start=grp["week_start"].iloc[0], I=mi.I, p=mi.p_sim))
    return pd.DataFrame(rows)


def show(fig, **kw):
    """st.plotly_chart, with a SAMPLE DATA mark across the figure when the sample is loaded."""
    if is_sample:
        fig.add_annotation(text="SAMPLE DATA, NOT REAL", xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, textangle=-20, opacity=0.18,
                           font=dict(size=46, color="#b03030"))
    st.plotly_chart(fig, **kw)


def theme_mode():
    """'dark' when the viewer's theme or the app's configured base theme is dark.
    st.context.theme reports the theme the viewer picked (it can read 'light' on the
    very first run); theme.base covers an app deployed with a dark base theme."""
    try:
        if st.context.theme.type == "dark":
            return "dark"
    except Exception:  # older Streamlit without st.context.theme
        pass
    return "dark" if st.get_option("theme.base") == "dark" else "light"


def notice(text, small=False):
    """Lavender notice box with thin border and rounded corners, in theme colors."""
    bg, border, ink = NOTICE_COLORS[theme_mode()]
    size, pad = ("0.88rem", "8px 14px") if small else ("0.98rem", "14px 18px")
    st.markdown(f"<div style='background:{bg}; border:1px solid {border}; border-radius:10px; color:{ink}; "
                f"padding:{pad}; font-size:{size}; line-height:1.45; margin:4px 0 12px 0'>{text}</div>",
                unsafe_allow_html=True)


def fmt(value, decimals):
    return "n/a" if pd.isna(value) else f"{value:,.{decimals}f}"


# ---- Map helpers --------------------------------------------------------------
def geo_axes(lon, lat, domain=None, fit=False):
    """Plotly geo subplot: light blue sea, no base land or coastlines (the prefecture
    shapes draw the land), Mercator projection, fixed lon/lat window."""
    g = dict(projection_type="mercator", showland=False, showcoastlines=False, showcountries=False, showlakes=False, showframe=False,
             showocean=True, oceancolor=SEA, bgcolor=SEA)
    if fit:
        g["fitbounds"] = "locations"   # fit the map to the prefectures drawn in it
    else:
        g.update(lonaxis_range=list(lon), lataxis_range=list(lat))
    if domain:
        g["domain"] = domain
    return g


def base_map(view, codes_in_view, height):
    """Empty figure with the map window for a view. All Japan adds an Okinawa inset."""
    v = VIEWS[view] if view in VIEWS else fit_view(codes_in_view)
    fig = go.Figure()
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor=SEA,
                      geo=geo_axes(v["lon"], v["lat"], dict(x=[0, 1], y=[0, 1])), showlegend=False)
    inset = view == "All Japan"
    if inset:
        fig.update_layout(geo2=geo_axes(INSET["lon"], INSET["lat"], dict(x=list(INSET["x"]), y=list(INSET["y"])),
                                        fit=True))
        fig.add_shape(type="rect", xref="paper", yref="paper", x0=INSET["x"][0], x1=INSET["x"][1],
                      y0=INSET["y"][0], y1=INSET["y"][1], line=dict(color="#7b8794", width=1, dash="dash"))
        fig.add_annotation(xref="paper", yref="paper", x=(INSET["x"][0] + INSET["x"][1]) / 2, y=INSET["y"][1],
                           yanchor="bottom", text="Okinawa (inset)", showarrow=False,
                           font=dict(size=11, color="#52514e"))
    return fig, inset


def add_choro(fig, inset, df, **kw):
    """Add a choropleth layer; with an inset, Okinawa goes to the inset map."""
    parts = [(df[df["pref_code"] != OKINAWA], "geo"), (df[df["pref_code"] == OKINAWA], "geo2")] if inset else [(df, "geo")]
    for part, g in parts:
        if part.empty:
            continue
        k = dict(kw)
        for key in ("z", "text", "customdata"):
            if key in k and k[key] is not None:
                k[key] = np.asarray(k[key])[df.index.get_indexer(part.index)]
        if g == "geo2":
            k["showscale"] = False
        fig.add_trace(go.Choropleth(geojson=geo, locations=part["pref_code"], featureidkey="properties.pref_code",
                                    geo=g, **k))


def add_outline(fig, inset, codes, color, width):
    df = pd.DataFrame({"pref_code": list(codes)})
    add_choro(fig, inset, df, z=[1] * len(df), colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
              showscale=False, hoverinfo="skip", marker_line_color=color, marker_line_width=width)


def add_labels(fig, inset, df, size):
    """Prefecture name and value written on the map, as on the JSPID slides."""
    if df.empty:
        return
    lab = load_labels()
    for part, g in ([(df[df["pref_code"] != OKINAWA], "geo"), (df[df["pref_code"] == OKINAWA], "geo2")]
                    if inset else [(df, "geo")]):
        if part.empty:
            continue
        pts = lab.loc[part["pref_code"]]
        fig.add_trace(go.Scattergeo(
            lon=pts["lon"], lat=pts["lat"], mode="text", geo=g, hoverinfo="skip",
            text=[f"{n} {v:.1f}" for n, v in zip(part["prefecture"], part["per_sentinel"])],
            textfont=dict(size=size, color="#111111", family=FONT_STACK, weight="bold", shadow="0 0 3px #ffffff")))


def prefecture_map(m, codes_in_view, view, height, scale_mode, cap, alert_lines=False):
    """Map of reports per sentinel in the JSPID slide style: warm colors, light blue
    sea, thin gray borders, names and values on the map. Prefectures outside the
    chosen area keep their color but are faded. All Japan has an Okinawa inset."""
    fig, inset = base_map(view, codes_in_view, height)
    m = m.reset_index(drop=True)
    if scale_mode == "IDWR levels":
        z = pd.cut(m["per_sentinel"], LEVEL_EDGES, labels=False, right=False).to_numpy(dtype=float)
        scale = [[i / (len(LEVEL_COLORS) - 1), c] for i, c in enumerate(LEVEL_COLORS)]
        zmin, zmax, showscale = 0, len(LEVEL_COLORS) - 1, False
    else:
        z, scale, zmin, zmax, showscale = m["per_sentinel"].to_numpy(dtype=float), SEQ_SCALE, 0, cap, True
    sent = m["sentinels"].fillna(-1) if has_sentinels else pd.Series(-1, index=m.index)
    custom = np.stack([m["per_sentinel"], m["c2"].fillna(0), np.where(m["alert"], "yes", "no"), sent], axis=-1)
    hover = ("<b>%{text}</b><br>Reports per sentinel: %{customdata[0]:.2f}"
             + ("<br>Sentinel sites: %{customdata[3]}" if has_sentinels else "")
             + "<br>C2: %{customdata[1]:.1f}<br>Alert: %{customdata[2]}<extra></extra>")
    inn = m["pref_code"].isin(codes_in_view).to_numpy()
    for mask, opacity, line in ((~inn, FADE_OPACITY, "#9aa1a9"), (inn, 1.0, BORDER)):
        if not mask.any():
            continue
        part = m[mask]
        add_choro(fig, inset, part, z=z[mask], zmin=zmin, zmax=zmax, colorscale=scale,
                  showscale=showscale and opacity == 1.0, marker_opacity=opacity,
                  colorbar=dict(title=dict(text="per sentinel", side="right"), thickness=12, len=0.6, x=0.99),
                  text=part["prefecture"].to_numpy(), customdata=custom[mask], hovertemplate=hover,
                  marker_line_color=line, marker_line_width=0.6)
    inside = m[inn]
    if alert_lines and inside["alert"].any():
        add_outline(fig, inset, inside.loc[inside["alert"], "pref_code"], MAP_ALERT, 1.6)
    chosen_here = inside[inside["prefecture"].isin(chosen)]
    if len(chosen_here):
        add_outline(fig, inset, chosen_here["pref_code"], MAP_SELECT, 1.8)
    if view == "All Japan":
        top = inside.nlargest(8, "per_sentinel")["pref_code"].tolist()
        lab_codes = set(top) | set(chosen_here["pref_code"]) | {OKINAWA}
        add_labels(fig, inset, inside[inside["pref_code"].isin(lab_codes)], 10)
    else:
        add_labels(fig, inset, inside, 12)
    return fig


def map_with_reset(fig, name, label="⟲  Reset map view"):
    """Draw a map with a Reset button above it and a hint below it.

    The button bumps a counter that forms part of the chart's key and its
    uirevision. Plotly keeps a user's zoom while uirevision holds the same
    value, so changing it is what returns the view to the start."""
    cnt_key = f"_mapreset_{name}"
    st.session_state.setdefault(cnt_key, 0)
    _, right = st.columns([3, 1.6])
    with right:
        if st.button(label, key=f"btn_{name}", width="stretch", help="Zoom back out to the starting view"):
            st.session_state[cnt_key] += 1
    fig.update_layout(uirevision=f"{name}-{st.session_state[cnt_key]}")
    show(fig, width="stretch", config=MAPCFG, key=f"{name}_{st.session_state[cnt_key]}")
    st.caption("Scroll or drag to zoom and pan. Press Reset map view above to return to the starting view.")


def level_legend():
    sw = "".join(f"<span style='display:inline-block;width:13px;height:13px;background:{c};"
                 f"border:1px solid #cfd4da;border-radius:2px;margin:0 5px 0 14px;vertical-align:-1px'></span>{lab}"
                 for c, lab in zip(LEVEL_COLORS, LEVEL_LABELS))
    st.markdown(f"<div style='font-size:0.88rem;color:{INK_SOFT}'>Reports per sentinel site{sw}</div>",
                unsafe_allow_html=True)


def ranked_table(m, codes_in_view, title):
    keep = ["prefecture", "per_sentinel"] + (["sentinels"] if has_sentinels else []) + ["c2", "alert", "population_2020"]
    t = m[m["pref_code"].isin(codes_in_view)][keep].sort_values("per_sentinel", ascending=False).reset_index(drop=True)
    t.index += 1
    t = t.rename(columns={"prefecture": "Prefecture", "per_sentinel": "Reports per sentinel",
                          "sentinels": "Sentinel sites", "c2": "C2", "alert": "Alert",
                          "population_2020": "Population (2020)"})
    st.markdown(f"**{title}**")
    st.dataframe(t, width="stretch", height=min(380, 38 + 35 * len(t)),
                 column_config={"Reports per sentinel": st.column_config.NumberColumn(format="%.2f"),
                                "C2": st.column_config.NumberColumn(format="%.1f"),
                                "Population (2020)": st.column_config.NumberColumn(format="localized")})


# ---- Page layout -------------------------------------------------------------
st.set_page_config(page_title="Japan IDWR Surveillance Explorer", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
    /* Century Gothic where it is installed; Didact Gothic, a free look-alike,
       for everyone else. The same pair the portfolio site uses. */
    @import url('https://fonts.googleapis.com/css2?family=Didact+Gothic&display=swap');
    html, body, [class*="st-"], .stApp, button, input, select, textarea {
        font-family: "Century Gothic", CenturyGothic, AppleGothic, "Didact Gothic", sans-serif;
    }
    /* Streamlit draws its icons with a ligature font. The rule above would turn
       them into their literal names, such as keyboard_double_arrow_left, so the
       icon elements get their own font back. */
    [data-testid="stIconMaterial"], span[data-testid="stIconMaterial"],
    .material-icons, .material-symbols-rounded, .material-symbols-outlined {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    }
    .block-container {padding-top: 2.2rem; padding-bottom: 2rem;}
    .tile {border: 1px solid #e6e6e2; border-radius: 12px; padding: 14px 16px 12px 16px;
           background: #ffffff; height: 100%;}
    .tile .name {font-size: 0.95rem; font-weight: 600; color: #1f2933; display: flex;
                 align-items: center; gap: 8px;}
    .tile .swatch {width: 12px; height: 12px; border-radius: 3px; display: inline-block;}
    .tile .big {font-size: 1.9rem; font-weight: 600; color: #1f2933; margin-top: 4px; line-height: 1.1;}
    .tile .sub {font-size: 0.8rem; color: #52514e; margin-top: 6px; line-height: 1.35;}
    /* Cards in the portfolio site's style: a pastel fill, a border a shade
       deeper, and a 6px edge in the card's own color. */
    .stile {border-radius: 10px; padding: 16px 18px 14px 18px; height: 100%; min-height: 152px;
            box-sizing: border-box; border: 1px solid transparent; border-left-width: 6px;}
    .stile .name {font-size: 0.95rem; font-weight: 600;}
    .stile .big {font-size: 1.9rem; font-weight: 600; margin-top: 4px; line-height: 1.1; color: #14212B;}
    .stile .sub {font-size: 0.8rem; color: #4B5963; margin-top: 6px; line-height: 1.35;}
    </style>
    """,
    unsafe_allow_html=True,
)

# The data load depends on two controls further down (New Year weeks, alert
# threshold). Their last values are in session state at the top of each rerun.
st.session_state.setdefault("drop_holidays", True)
drop_holidays = st.session_state["drop_holidays"]
threshold = st.session_state.get("ears_thr", 3.0)
try:
    weekly, is_sample, use_r_c2, geo_notes = load_weekly(drop_holidays, threshold, ALLOW_SAMPLE)
except FileNotFoundError:
    st.title("Weekly IDWR Reports by Prefecture in Japan")
    st.error("The weekly IDWR table is not loaded yet. Add data/idwr_weekly.csv, written by the IDWR "
             "alert report R script, and reload the page.")
    st.stop()
except Exception as err:  # malformed file
    st.error(f"Could not read the weekly IDWR table: {err}")
    st.stop()
geo = load_geo()
pop = load_population()
has_sentinels = "sentinels" in weekly.columns

st.session_state.setdefault("prefs", ["Tokyo", "Osaka", "Nara", "Okinawa"])
st.session_state.setdefault("colors", {})


def assign_colors(selected):
    """Give each selected prefecture a palette color it keeps for the session."""
    colors = st.session_state.colors
    for p in list(colors):
        if p not in selected:
            del colors[p]
    for p in selected:
        if p not in colors:
            colors[p] = next(c for c in PALETTE if c not in colors.values())
    return {p: colors[p] for p in selected}


def add_prefecture():
    """Button callback: move the picked prefecture into the selected list."""
    pick = st.session_state.get("to_add")
    if pick and pick not in st.session_state.prefs:
        if len(st.session_state.prefs) >= MAX_SELECT:
            st.session_state.limit_hit = True
        else:
            st.session_state.prefs = st.session_state.prefs + [pick]
    st.session_state.to_add = None


diseases = sorted(weekly["disease"].unique())
with st.sidebar:
    st.header("Prefectures")
    all_prefs = list(weekly.drop_duplicates("pref_code").sort_values("pref_code")["prefecture"])
    st.selectbox("Add a prefecture", [p for p in all_prefs if p not in st.session_state.prefs],
                 index=None, placeholder="Type or pick a prefecture", key="to_add")
    st.button("Add", width="stretch", on_click=add_prefecture, key="add_pref")
    chosen = st.multiselect("Selected prefectures (click x to remove)", all_prefs, key="prefs",
                            max_selections=MAX_SELECT)
    if st.session_state.pop("limit_hit", False):
        st.warning(f"Up to {MAX_SELECT} prefectures can be compared at once. Remove one first.")

    st.header("Display options")
    disease = st.selectbox("Disease", diseases,
                           index=diseases.index("Influenza") if "Influenza" in diseases else 0)
    d = weekly[weekly["disease"] == disease]
    st.caption(DISEASE_NOTES.get(disease, DEFAULT_NOTE))
    if d["per_sentinel"].median() < 0.1:
        st.warning("Most prefecture weeks have almost no reports for this disease, so C2 alerts are not reliable.")
    if disease not in THRESHOLDS:
        st.caption("The 1.0 level, onset, lead time and false alarms apply to influenza only. The minimum SD of "
                   "0.1 was set for influenza and has not been tested for this disease.")
    weeks = d.drop_duplicates("week_start").sort_values("week_start")
    week_labels = list(weeks["week_label"])
    map_week = st.select_slider("IDWR week (maps and cards)", options=week_labels, value=week_labels[-1],
                                help="Weeks run Monday to Sunday.")
    start_wk, end_wk = st.select_slider("Weeks shown (charts)", options=week_labels,
                                        value=(week_labels[0], week_labels[-1]))
    layout_choice = st.radio("Chart layout", ["One chart", "One panel per prefecture"], horizontal=True,
                             key="layout", help="Separate panels help when one prefecture's values dwarf the others.")
    show_alerts = st.toggle("Mark C2 alerts on the chart", value=True)
    log_scale = st.toggle("Log scale (y-axis)", value=False)
    st.toggle("Leave New Year weeks out of C2 baselines", key="drop_holidays",
              help="Clinic closures around New Year lower reports in weeks 52, 53 and 1. On by default. "
                   "Turn off to use every week, as the R alert report does now.")
    if is_sample:
        st.error("SAMPLE DATA. These are synthetic values for layout only, not IDWR reports.")

start_ts = weeks.loc[weeks["week_label"] == start_wk, "week_start"].iloc[0]
end_ts = weeks.loc[weeks["week_label"] == end_wk, "week_start"].iloc[0]
in_window = (d["week_start"] >= start_ts) & (d["week_start"] <= end_ts)
week_row = d[d["week_label"] == map_week]
m_week = week_row.merge(pop[["pref_code", "population_2020"]], on="pref_code", how="left")
cap = float(np.nanpercentile(d["per_sentinel"], 98))
thr_lines = THRESHOLDS.get(disease, {})
rated = disease in THRESHOLDS
colors = assign_colors(chosen)

# ---- Header ------------------------------------------------------------------
st.title("Weekly IDWR Reports by Prefecture in Japan" + (" (SAMPLE DATA)" if is_sample else ""))
st.markdown(
    "<p style='opacity:0.78; font-size:1.05rem; margin-top:-0.4rem'>"
    "Pick prefectures in the sidebar and compare reports per sentinel site by week, with "
    "EARS C2 alerts and spatial clustering. Source: Japan Institute for Health Security, "
    f"Infectious Disease Weekly Report (<a href='{IDWR_URL}'>IDWR</a>). App {VERSION}.</p>",
    unsafe_allow_html=True)
notice(NOTICE_LINE, small=True)
if is_sample:
    st.error("**Sample data, not real.** Every number, chart and map on this page comes from a synthetic file "
             "made for layout. Nothing here describes disease in Japan. Load data/idwr_weekly.csv from the "
             "R script before sharing or deploying.")
for note in geo_notes:
    st.warning("Geography check: " + note)

(tab_spatial, tab_chart, tab_pmap, tab_jmap, tab_alerts, tab_table, tab_help, tab_about) = st.tabs(
    ["Spatial Statistics", "Chart", "Prefecture Map", "Japan Map", "Alerts", "Summary Table",
     "User Guide", "About the Data"])

# ---- Spatial statistics tab -----------------------------------------------------
with tab_spatial:
    st.markdown(f"**Do prefectures with high {disease.lower()} reports sit next to each other?** "
                "Global Moran's I measures that for the whole country; local Moran (LISA) finds the clusters.")
    codes = tuple(sorted(load_neighbors()))
    vals = week_row.set_index("pref_code").reindex(list(codes))["per_sentinel"]
    try:
        if vals.isna().any() or vals.std() == 0:
            st.info(f"{map_week} has missing or identical values, so spatial statistics are not computed.")
        else:
            sp, I, p_I, EI = spatial_stats(tuple(vals.to_numpy()), codes)
            sp = sp.merge(week_row[["pref_code", "prefecture"]], on="pref_code", how="left")
            p_txt = "< 0.001" if p_I < 0.001 else f"{p_I:.3f}"
            verdict = "Similar levels sit together" if I > 0.1 and p_I < 0.05 else "No clear spatial pattern"
            hh = int((sp["cluster"] == "High-High").sum())
            cards = [
                ("Global Moran's I", f"{I:.3f}", "#FBE7E6", "#F0CBC8", "#A33E50",
                 f"{verdict}<br>Expected {EI:.3f} under no pattern"),
                ("Permutation p-value", p_txt, "#E3F2F3", "#C3E0E2", "#16707E",
                 f"{PERMUTATIONS} random re-assignments<br>of the values to prefectures"),
                ("High-High prefectures", f"{hh}", "#FFF7D1", "#F7E08A", "#8C6D00",
                 "High reports whose neighbors<br>also have high reports"),
                ("Prefectures in analysis", f"{len(sp)}", "#F1EBF8", "#DACDEC", "#6A4C9C",
                 f"Week {map_week}<br>Neighbors: shared border, plus<br>3 sea links (Okinawa, Hokkaido, Kyushu)"),
            ]
            for col, (name, big, fill, edge, accent, sub) in zip(st.columns(4), cards):
                col.markdown(
                    f"<div class='stile' style='background:{fill}; border-color:{edge}; border-left-color:{accent}'>"
                    f"<div class='name' style='color:{accent}'>{name}</div><div class='big'>{big}</div>"
                    f"<div class='sub'>{sub}</div></div>", unsafe_allow_html=True)
            st.write("")

            left, right = st.columns([3, 2])
            with left:
                fig, inset = base_map("All Japan", list(range(1, 48)), 470)
                for cat in CLUSTER_ORDER:
                    sub = sp[sp["cluster"] == cat].reset_index(drop=True)
                    if sub.empty:
                        continue
                    add_choro(fig, inset, sub, z=[CLUSTER_ORDER.index(cat)] * len(sub),
                              text=sub["prefecture"].to_numpy(), showscale=False,
                              colorscale=[[0, CLUSTER_COLORS[cat]], [1, CLUSTER_COLORS[cat]]],
                              marker_line_color=BORDER, marker_line_width=0.5,
                              customdata=sub[["value", "p"]].to_numpy(),
                              hovertemplate="<b>%{text}</b><br>" + cat + "<br>Reports per sentinel: %{customdata[0]:.2f}"
                                            "<br>p = %{customdata[1]:.3f}<extra></extra>")
                sel_codes = sp[sp["prefecture"].isin(chosen)]["pref_code"]
                if len(sel_codes):
                    add_outline(fig, inset, sel_codes, SELECT_OUTLINE, 1.6)
                st.markdown(f"**LISA clusters** · reports per sentinel site · {map_week} · p below 0.05")
                map_with_reset(fig, "lisa")
                counts = sp["cluster"].value_counts().reindex(CLUSTER_ORDER).fillna(0).astype(int)
                st.caption("  ·  ".join(f"{c}: {n}" for c, n in counts.items())
                           + ". Selected prefectures are outlined in orange. " + ISLANDS_NOTE)
            with right:
                fig2 = go.Figure()
                for cat in CLUSTER_ORDER:
                    sub = sp[sp["cluster"] == cat]
                    if sub.empty:
                        continue
                    fig2.add_trace(go.Scatter(
                        x=sub["z"], y=sub["lag"], mode="markers", name=cat, text=sub["prefecture"],
                        marker=dict(color=CLUSTER_COLORS[cat], size=9, line=dict(color="#6b7280", width=0.5)),
                        hovertemplate="<b>%{text}</b><br>z = %{x:.2f}<br>spatial lag = %{y:.2f}<extra></extra>"))
                # Labels alternate above and below their points, in order along the x-axis,
                # so two prefectures with close values do not print on top of each other.
                lab = sp[sp["prefecture"].isin(chosen)].sort_values("z").reset_index(drop=True)
                for i, r in lab.iterrows():
                    fig2.add_annotation(x=r["z"], y=r["lag"], text=r["prefecture"], showarrow=True,
                                        arrowhead=0, ax=0, ay=-24 if i % 2 == 0 else 26,
                                        font=dict(size=11, color=INK), bgcolor="rgba(255,255,255,0.8)")
                xs = np.array([sp["z"].min(), sp["z"].max()])
                fig2.add_trace(go.Scatter(x=xs, y=I * xs, mode="lines", line=dict(color=INK, width=1.5, dash="dot"),
                                          name=f"Slope = Moran's I ({I:.2f})", hoverinfo="skip"))
                fig2.add_hline(y=0, line_color=GRID)
                fig2.add_vline(x=0, line_color=GRID)
                fig2.update_layout(height=470, plot_bgcolor="white", paper_bgcolor="white",
                                   margin=dict(l=10, r=10, t=10, b=10),
                                   xaxis=dict(title="Standardized reports per sentinel (z)", gridcolor=GRID, zeroline=False),
                                   yaxis=dict(title="Spatial lag of z (neighbors' mean)", gridcolor=GRID, zeroline=False),
                                   legend=dict(orientation="h", y=-0.25, font=dict(size=11)))
                st.markdown("**Moran scatterplot**")
                show(fig2, width="stretch", config=CHARTCFG)

            ms = moran_by_week(d[["week_label", "week_start", "pref_code", "per_sentinel"]], codes)
            fig3 = go.Figure(go.Scatter(
                x=ms["week_start"], y=ms["I"], mode="lines+markers", line=dict(color=PALETTE[0], width=2),
                marker=dict(color=np.where(ms["p"] < 0.05, PALETTE[1], "#bdbdbd"), size=8),
                customdata=ms[["week_label", "p"]].values,
                hovertemplate="%{customdata[0]}<br>I = %{y:.2f}<br>p = %{customdata[1]:.3f}<extra></extra>"))
            fig3.add_hline(y=0, line=dict(color=GRID))
            fig3.add_vline(x=week_row["week_start"].iloc[0].timestamp() * 1000, line=dict(color="#9aa1a9", width=1))
            fig3.update_layout(height=280, plot_bgcolor="white", paper_bgcolor="white",
                               margin=dict(l=10, r=10, t=10, b=10),
                               xaxis=dict(showgrid=False, linecolor=GRID),
                               yaxis=dict(title="Global Moran's I", gridcolor=GRID, zeroline=False))
            st.markdown("**Global Moran's I by week** · orange points: p below 0.05 · gray line: map week")
            show(fig3, width="stretch", config=CHARTCFG)
            st.caption(
                "Method: reports per sentinel site for the map week. Spatial weights: prefectures that share a "
                "border (queen contiguity on the full-resolution boundaries), plus Hokkaido-Aomori and "
                "Okinawa-Kagoshima (nearest prefecture by distance) and Fukuoka-Yamaguchi (Kanmon Strait), "
                f"row-standardized. Global Moran's I and local Moran from PySAL esda with {PERMUTATIONS} "
                f"permutations. Expected I under no spatial pattern: {EI:.3f}. High-High: a high-reporting "
                "prefecture with high-reporting neighbors; Low-Low: the reverse; High-Low and Low-High are "
                "spatial outliers. Sentinel reports reflect care-seeking and reporting practice, so the "
                "clusters describe the reported data.")
    except ImportError:
        st.info("Install libpysal and esda (see requirements.txt) to enable this tab.")

# ---- Chart tab -------------------------------------------------------------------
with tab_chart:
    if not chosen:
        st.info("Add at least one prefecture in the sidebar to see the chart.")
    else:
        view = d[in_window & d["prefecture"].isin(chosen)]
        tiles = st.columns(len(chosen))
        for col, p in zip(tiles, chosen):
            s = view[view["prefecture"] == p].dropna(subset=["per_sentinel"])
            if s.empty:
                col.markdown(f"<div class='tile'><div class='name'><span class='swatch' style='background:{colors[p]}'>"
                             f"</span>{p}</div><div class='sub'>No values in this window.</div></div>",
                             unsafe_allow_html=True)
                continue
            last = s.iloc[-1]
            peak = s.loc[s["per_sentinel"].idxmax()]
            col.markdown(
                f"<div class='tile'><div class='name'><span class='swatch' style='background:{colors[p]}'></span>{p}</div>"
                f"<div class='big'>{fmt(last['per_sentinel'], 2)}</div>"
                f"<div class='sub'>Reports per sentinel in {last['week_label']}<br>"
                f"Peak {fmt(peak['per_sentinel'], 2)} in {peak['week_label']}<br>"
                f"{int(s['alert'].sum())} C2 alert weeks in window</div></div>", unsafe_allow_html=True)
        st.markdown("")

        def add_thresholds(fig, **rc):
            for lab, v in thr_lines.items():
                fig.add_hline(y=v, line=dict(color="#c48a00" if lab == "Epidemic" else "#9aa1a9", width=1.2,
                                             dash="dash" if lab == "Epidemic" else "dot"),
                              annotation_text=f"{lab} ({v})", annotation_position="top left",
                              annotation_font=dict(size=11, color=INK_SOFT), **rc)

        hover = "%{y:.2f}"
        if layout_choice == "One chart":
            fig = go.Figure()
            for p in chosen:
                s = view[view["prefecture"] == p]
                fig.add_trace(go.Scatter(x=s["week_start"], y=s["per_sentinel"], name=p, mode="lines",
                                         line=dict(color=colors[p], width=2), hovertemplate=hover, connectgaps=False))
                a = s[s["alert"]]
                if show_alerts and len(a):
                    fig.add_trace(go.Scatter(x=a["week_start"], y=a["per_sentinel"], mode="markers", showlegend=False,
                                             marker=dict(color=colors[p], size=9, symbol="diamond",
                                                         line=dict(color="white", width=1)),
                                             customdata=a["c2"], hovertemplate="C2 alert (C2 = %{customdata:.1f})"
                                                                               "<extra>" + p + "</extra>"))
            add_thresholds(fig)
            fig.update_layout(height=520, hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white",
                              legend=dict(orientation="h", y=-0.14, title=None), margin=dict(l=10, r=20, t=20, b=10),
                              xaxis=dict(title=None, showgrid=False, linecolor=GRID),
                              yaxis=dict(title=None, gridcolor=GRID, zeroline=False,
                                         type="log" if log_scale else "linear"),
                              font=dict(color=INK))
        else:
            n = len(chosen)
            ncol = 2 if n > 1 else 1
            nrow = -(-n // ncol)
            fig = make_subplots(rows=nrow, cols=ncol, subplot_titles=chosen, shared_xaxes=True,
                                vertical_spacing=0.12, horizontal_spacing=0.08)
            for i, p in enumerate(chosen):
                s = view[view["prefecture"] == p]
                r, k = divmod(i, ncol)
                fig.add_trace(go.Scatter(x=s["week_start"], y=s["per_sentinel"], name=p, mode="lines",
                                         line=dict(color=colors[p], width=2), hovertemplate=hover,
                                         showlegend=False, connectgaps=False), row=r + 1, col=k + 1)
                a = s[s["alert"]]
                if show_alerts and len(a):
                    fig.add_trace(go.Scatter(x=a["week_start"], y=a["per_sentinel"], mode="markers", showlegend=False,
                                             marker=dict(color=colors[p], size=8, symbol="diamond",
                                                         line=dict(color="white", width=1)), hoverinfo="skip"),
                                  row=r + 1, col=k + 1)
            add_thresholds(fig, row="all", col="all")
            fig.update_layout(height=max(420, 280 * nrow), plot_bgcolor="white", paper_bgcolor="white",
                              hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10), font=dict(color=INK))
            fig.update_xaxes(showgrid=False, linecolor=GRID)
            fig.update_yaxes(gridcolor=GRID, zeroline=False, type="log" if log_scale else "linear")
            for ann in fig.layout.annotations:
                if ann.text in chosen:
                    ann.font.size, ann.font.color = 14, INK
        st.markdown(f"**{disease}: reports per sentinel site by week** · {start_wk} to {end_wk}")
        show(fig, width="stretch", config=CHARTCFG)
        st.caption("Hover for every prefecture's value in a week. Diamonds mark EARS C2 alerts. Dashed line: "
                   "epidemic threshold (1.0). Dotted lines: caution (10) and warning (30). Drag on the chart "
                   "to zoom; double-click to reset. Log scale hides weeks with zero reports.")
        csv = view[["prefecture", "week_label", "week_start", "disease", "per_sentinel", "c2", "alert"]].to_csv(index=False)
        st.download_button("Download the plotted data (CSV)", csv, file_name="japan_idwr_selected.csv",
                           mime="text/csv")

# ---- Map tab (Kanto, Kansai, selected prefectures) ------------------------------------------------------------
with tab_pmap:
    c_area, c_scale = st.columns([3, 2])
    area = c_area.radio("Area", ["Kanto and Kansai", "Kanto (Tokyo area)", "Kansai (Osaka area)",
                                 "Selected prefectures"], horizontal=True, key="pmap_area")
    pscale = c_scale.radio("Shade prefectures by", ["IDWR levels", "Continuous"] if rated else ["Continuous"], horizontal=True, key=f"pmap_scale_{rated}",
                           help="Five bands: under 1.0, then 1.0 to 9.99, 10 to 19.99, 20 to 29.99, and 30 and over.")
    p_alert = st.toggle("Outline prefectures with a C2 alert this week (black)", value=False, key="pmap_alert_lines")
    if area == "Kanto and Kansai":
        mc1, mc2 = st.columns(2)
        for col, v, nm in ((mc1, "Kanto (Tokyo area)", "kanto"), (mc2, "Kansai (Osaka area)", "kansai")):
            with col:
                st.markdown(f"**{v}** · {map_week}")
                map_with_reset(prefecture_map(m_week, VIEWS[v]["codes"], v, 460, pscale, cap, p_alert), nm)
        in_view = VIEWS["Kanto (Tokyo area)"]["codes"] + VIEWS["Kansai (Osaka area)"]["codes"]
    elif area == "Selected prefectures":
        in_view = m_week[m_week["prefecture"].isin(chosen)]["pref_code"].tolist()
        if not in_view:
            st.info("Add at least one prefecture in the sidebar to see this map.")
        else:
            st.markdown(f"**Selected prefectures** · reports per sentinel site · {map_week}")
            map_with_reset(prefecture_map(m_week, in_view, "selection", 540, pscale, cap, p_alert), "selection")
    else:
        in_view = VIEWS[area]["codes"]
        st.markdown(f"**{area}** · reports per sentinel site · {map_week}")
        map_with_reset(prefecture_map(m_week, in_view, area, 540, pscale, cap, p_alert), "area")
    if pscale == "IDWR levels":
        level_legend()
    st.caption("Prefectures outside the area are faded. Selected prefectures are outlined in dark blue"
               + ("; prefectures with a C2 alert this week in black" if p_alert else "")
               + ". Hover any prefecture for its numbers, including C2 and whether it alerted.")
    if in_view:
        ranked_table(m_week, in_view, f"Prefectures in this area ranked by reports per sentinel, {map_week}")

# ---- Japan map tab -----------------------------------------------------------------
with tab_jmap:
    jscale = st.radio("Shade prefectures by", ["IDWR levels", "Continuous"] if rated else ["Continuous"], horizontal=True, key=f"jmap_scale_{rated}",
                      help="Five bands: under 1.0, then 1.0 to 9.99, 10 to 19.99, 20 to 29.99, and 30 and over.")
    j_alert = st.toggle("Outline prefectures with a C2 alert this week (black)", value=False, key="jmap_alert_lines")
    st.markdown(f"**{disease}: reports per sentinel site in every prefecture** · {map_week}")
    map_with_reset(prefecture_map(m_week, list(range(1, 48)), "All Japan", 680, jscale, cap, j_alert), "japan")
    if jscale == "IDWR levels":
        level_legend()
    st.caption(("Five bands: under 1.0, then steps up to the warning level of 30. " if jscale == "IDWR levels" else
                f"One warm scale from cream to dark red; the darkest step starts at the 98th percentile of the "
                f"season ({cap:.1f}) so a few extreme values do not flatten the rest. ")
               + "Labels show the 8 highest prefectures, your selected prefectures and Okinawa. "
               + "Selected prefectures are outlined in dark blue"
               + ("; prefectures with a C2 alert this week in black. " if j_alert else ". ")
               + ISLANDS_NOTE)
    ranked_table(m_week, list(range(1, 48)), f"All prefectures ranked by reports per sentinel, {map_week}")

# ---- Alerts tab --------------------------------------------------------------------
with tab_alerts:
    st.markdown("**When would a surveillance system have raised an alert?** EARS C2 compares each week's "
                "reports per sentinel with the mean and standard deviation of weeks t-9 to t-3, leaving a "
                "two-week guard (t-2 and t-1). A week that many standard deviations above that baseline is an alert.")
    st.slider("Alert threshold (standard deviations above baseline)", 2.0, 5.0, 3.0, 0.5, key="ears_thr")
    if not chosen:
        st.info("Add at least one prefecture in the sidebar to see the alerts.")
    else:
        base = d[in_window & d["prefecture"].isin(chosen)]
        n = len(chosen)
        ncol = 2 if n > 1 else 1
        nrow = -(-n // ncol)
        fig = make_subplots(rows=nrow, cols=ncol, subplot_titles=chosen, shared_xaxes=True,
                            vertical_spacing=0.12, horizontal_spacing=0.08)
        rows = []
        for i, p in enumerate(chosen):
            s = base[base["prefecture"] == p]
            r, k = divmod(i, ncol)
            fig.add_trace(go.Scatter(x=s["week_start"], y=s["per_sentinel"], mode="lines",
                                     line=dict(color=colors[p], width=1.8), name=p, showlegend=False,
                                     hovertemplate="%{y:.2f}<extra></extra>"), row=r + 1, col=k + 1)
            al = s[s["alert"]]
            fig.add_trace(go.Scatter(x=al["week_start"], y=al["per_sentinel"], mode="markers",
                                     marker=dict(color=ALERT_RED, size=7), name="Alert", showlegend=(i == 0),
                                     customdata=al["c2"],
                                     hovertemplate="Alert: %{y:.2f} (C2 = %{customdata:.1f})<extra></extra>"),
                          row=r + 1, col=k + 1)
            c2w = s["c2"]
            o = al["alert_outcome"].value_counts()
            row = {
                "Prefecture": p, "Alert weeks in window": len(al), "Weeks in window": len(s),
                "First alert": al["week_label"].iloc[0] if len(al) else "none",
                "Largest C2": round(float(c2w.max()), 1) if c2w.notna().any() else None,
                "Week of largest C2": s.loc[c2w.idxmax(), "week_label"] if c2w.notna().any() else "none",
            }
            if rated:
                row.update({"Below 1.0, then crossed": int(o.get("followed", 0)),
                            "False alarms": int(o.get("false", 0)), "Pending": int(o.get("pending", 0))})
            rows.append(row)
        if EPIDEMIC and disease in THRESHOLDS:
            fig.add_hline(y=EPIDEMIC, line=dict(color="#c48a00", dash="dash", width=1.2), row="all", col="all")
        fig.update_layout(height=max(420, 280 * nrow), plot_bgcolor="white", paper_bgcolor="white",
                          hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10), font=dict(color=INK),
                          legend=dict(orientation="h", y=-0.08))
        fig.update_xaxes(showgrid=False, linecolor=GRID)
        fig.update_yaxes(gridcolor=GRID, zeroline=False)
        for ann in fig.layout.annotations:
            ann.font.size, ann.font.color = 14, INK
        st.markdown(f"**Reports per sentinel site with EARS C2 alerts** · threshold {threshold:g} SD · "
                    f"{start_wk} to {end_wk}")
        show(fig, width="stretch", config=CHARTCFG)
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

        # New Year check: alerts in weeks 2 to 8 with and without the holiday weeks in the baselines.
        other = load_weekly(not drop_holidays, threshold, ALLOW_SAMPLE)[0]
        other = other[(other["disease"] == disease) & (other["week_start"] >= start_ts) & (other["week_start"] <= end_ts)]
        post = lambda f: int((f["alert"] & f["week"].between(2, 8)).sum())
        kept, left_out = (post(other), post(d[in_window])) if drop_holidays else (post(d[in_window]), post(other))
        st.markdown(f"**New Year check, all 47 prefectures, {start_wk} to {end_wk}.** Alert weeks in weeks 2 to 8: "
                    f"{kept} with weeks 52, 53 and 1 kept in the baselines, {left_out} with them left out. "
                    f"This page uses the {'second' if drop_holidays else 'first'} rule.")
        st.caption(
            "Method: EARS C2 (CDC Early Aberration Reporting System). Baseline = the 7 weeks ending three weeks "
            "before the week being tested (t-9 to t-3), leaving a two-week guard (t-2 and t-1). C2 = (reports "
            "per sentinel - baseline mean) / baseline SD, using the population SD with a floor of 0.1 and at "
            "least 5 baseline weeks. These are the same rules as the IDWR alert report R script."
            + (f" Dashed line: epidemic threshold, 1.0. A false alarm is an alert below 1.0 with no week at 1.0 or "
               f"above in that week or the next {FA_WINDOW}; pending means fewer than {FA_WINDOW} weeks of "
               f"follow-up so far." if rated else
               " The 1.0 level, false alarms and lead times apply to influenza only, so they are not shown for "
               "this disease."))

# ---- Summary table tab -------------------------------------------------------------
with tab_table:
    st.write(f"Weeks {start_wk} to {end_wk} (set with Weeks shown in the sidebar). "
             "All 47 prefectures; click a column header to sort.")
    ds = d[in_window]
    if not rated:
        quick = []
        for (code, p), sq in ds.groupby(["pref_code", "prefecture"]):
            sq = sq.sort_values("week_start").reset_index(drop=True)
            xq = sq["per_sentinel"]
            hq = sq.loc[sq["week_label"] == map_week, "per_sentinel"]
            aq = sq[sq["alert"]]
            quick.append({"Prefecture": p,
                          f"Reports per sentinel, {map_week}": hq.iloc[0] if len(hq) else np.nan,
                          "Peak": xq.max() if xq.notna().any() else None,
                          "Peak week": sq.loc[xq.idxmax(), "week_label"] if xq.notna().any() else "",
                          "First C2 alert": aq["week_label"].iloc[0] if len(aq) else "",
                          "Largest C2": round(float(sq["c2"].max()), 1) if sq["c2"].notna().any() else None,
                          "Alert weeks": int(sq["alert"].sum())})
        st.info("Onset, lead time and false alarms use the influenza 1.0 level, so they are shown for influenza only.")
        st.dataframe(pd.DataFrame(quick), hide_index=True, width="stretch", height=600,
                     column_config={f"Reports per sentinel, {map_week}": st.column_config.NumberColumn(format="%.2f"),
                                    "Peak": st.column_config.NumberColumn(format="%.2f")})
    else:
        rows = []
        for (code, p), s in ds.groupby(["pref_code", "prefecture"]):
            s = s.sort_values("week_start").reset_index(drop=True)
            x = s["per_sentinel"]
            cw, aw = onset_and_first_alert(x.to_numpy(dtype=float), s["alert"].to_numpy(), s["c2"].to_numpy(dtype=float))
            pk = s.loc[x.idxmax()] if x.notna().any() else None
            here = s.loc[s["week_label"] == map_week, "per_sentinel"]
            rows.append({
                "Prefecture": p,
                f"Reports per sentinel, {map_week}": here.iloc[0] if len(here) else np.nan,
                "Peak": None if pk is None else pk["per_sentinel"],
                "Peak week": None if pk is None else pk["week_label"],
                "Onset (sustained 1.0)": None if cw is None else s.loc[cw, "week_label"],
                "First C2 alert": None if aw is None else s.loc[aw, "week_label"],
                "Lead (weeks)": None if (cw is None or aw is None) else cw - aw,
                "False alarms": int((s["alert_outcome"] == "false").sum()),
                "Alert weeks": int(s["alert"].sum()),
            })
        summ = pd.DataFrame(rows)
        summ["Lead (weeks)"] = pd.to_numeric(summ["Lead (weeks)"], errors="coerce")
        for col_name in ("Peak week", "Onset (sustained 1.0)", "First C2 alert"):
            summ[col_name] = summ[col_name].fillna("")
        leads = summ["Lead (weeks)"].dropna()
        cards = [
            ("Reached 1.0", f"{(summ['Onset (sustained 1.0)'] != '').sum()} of {len(summ)}",
             "#E3F2F3", "#C3E0E2", "#16707E", "Reports per sentinel site<br>of 1.0 or more in these weeks"),
            ("Alert came first", f"{int((leads > 0).sum())} of {len(leads)}", "#FBE7E6", "#F0CBC8", "#A33E50",
             "First C2 alert before<br>the onset week"),
            ("Median lead", f"{leads.median():.0f} weeks" if len(leads) else "n/a", "#FFF7D1", "#F7E08A", "#8C6D00",
             f"Range {leads.min():.0f} to {leads.max():.0f} weeks" if len(leads) else "No prefecture with a lead"),
            ("False alarms", f"{int(summ['False alarms'].sum())}", "#F1EBF8", "#DACDEC", "#6A4C9C",
             f"Alerts below 1.0 with no crossing<br>in the next {FA_WINDOW} weeks"),
        ]
        for col, (name, big, fill, edge, accent, sub) in zip(st.columns(4), cards):
            col.markdown(
                f"<div class='stile' style='background:{fill}; border-color:{edge}; border-left-color:{accent}'>"
                f"<div class='name' style='color:{accent}'>{name}</div><div class='big'>{big}</div>"
                f"<div class='sub'>{sub}</div></div>", unsafe_allow_html=True)
        st.write("")
        st.dataframe(summ, hide_index=True, width="stretch", height=600,
                     column_config={f"Reports per sentinel, {map_week}": st.column_config.NumberColumn(format="%.2f"),
                                    "Peak": st.column_config.NumberColumn(format="%.2f"),
                                    "Lead (weeks)": st.column_config.NumberColumn(format="%d")})
        st.caption("Onset = the first week of the unbroken run at or above 1.0 per sentinel that contains the peak. "
                   f"First C2 alert = the first alert from {ONSET_LOOKBACK} weeks before the onset onward; earlier alerts "
                   "count toward false alarms. Lead = onset week minus first alert week; positive means the alert came "
                   "first. Blank when C2 had too little history before the onset.")

# ---- User guide tab ----------------------------------------------------------------
with tab_help:
    st.markdown("""
**Getting started**
1. In the sidebar, pick a prefecture in **Add a prefecture** and press **Add**. You can also type straight into
   **Selected prefectures**. Remove a prefecture with the **x** on its tag. Up to six prefectures can be compared
   at once; each keeps its color while selected.
2. Move **IDWR week** to choose the week shown on the maps, the spatial statistics and the summary table.
3. Drag **Weeks shown** to choose the period on the chart and the alerts.
4. **One panel per prefecture** gives each prefecture its own panel, which helps when one prefecture's values
   dwarf the others. **Log scale** is another way to handle that.
5. **Leave New Year weeks out of C2 baselines** is on by default. Turn it off to use every week, as the R alert
   report does now. The Alerts tab shows how many alerts in weeks 2 to 8 each rule gives.

**Reading the results**
- **Spatial Statistics** tests whether high-reporting prefectures sit next to each other (global Moran's I),
  maps the clusters (LISA), and shows Moran's I for every week, so you can see clusters form through a season.
- **Chart**: the tiles show each prefecture's latest value in the window, its peak, and the number of alert
  weeks. The dashed line is the epidemic threshold (1.0); the dotted lines are the caution (10) and warning (30)
  levels.
- **Prefecture Map** shows Kanto and Kansai side by side, one of them, or only your selected prefectures, with
  the rest of Japan faded. **Japan Map** shades all 47 prefectures and ranks them in a table below. Both offer
  the five IDWR color bands or a continuous scale.
- **Alerts** runs EARS C2 on each selected prefecture and marks the weeks a surveillance system would have raised
  an alert. Move the threshold slider to see how the count changes.
- **Summary Table** gives every prefecture's peak, its onset week (sustained 1.0), its first C2 alert, the lead
  between them, and the number of false alarms next to the lead.
- **Download the plotted data** saves exactly what is on the chart as a CSV file.
""")

# ---- About the data tab ------------------------------------------------------------
with tab_about:
    n_bad = week_check(weekly)
    c2_source = ("the c2 column written by the R alert report" if use_r_c2 else
                 "C2 computed in this app with the R alert report's rules"
                 + (", New Year weeks left out of baselines" if drop_holidays else ""))
    notice(NOTICE_FULL)
    st.markdown(f"""
**Source.** Japan Institute for Health Security (JIHS, formerly NIID), Infectious Disease Weekly Report (IDWR),
weekly reports of sentinel-surveillance diseases by prefecture ([link]({IDWR_URL})). The unit is reports per
sentinel site per week. About 5,000 sentinel clinics and hospitals report influenza nationwide. The number differs
by prefecture and changes from week to week, so per-sentinel values, not raw counts, are comparable across
prefectures.

**How the data were prepared**
- The table is written by the IDWR alert report R script: one row per prefecture, week and disease.
- Each prefecture is placed on a complete weekly grid, so a missing week shows as a gap and cannot shift the C2
  baseline.
- Reports per sentinel are floored at zero.
- Weeks run Monday to Sunday. {"Every year-week label matches the ISO week of its start date." if n_bad == 0 else
  f"{n_bad} week labels do not match the ISO week of their start date; check how IDWR numbers weeks in 53-week years."}
- Geography: one row per prefecture (codes 1 to 47). A national row is never added to a sum; any row with
  another code is dropped. {"All 47 prefectures are present, with the expected names." if not geo_notes else " ".join(geo_notes)}
  The population table uses the same 47 codes and is shown for reference only; no rate in this app divides
  by it.
- This copy uses {c2_source}.

**Diseases and period.** This app covers the 19 sentinel-surveillance diseases in the JIHS provisional yearly
prefecture file (teiten-tougai), 2026 weeks 1 to 42. Pick the disease in the sidebar. Each disease has a note on
its sentinel scheme. Influenza and COVID-19 changed in April 2025, when acute respiratory infection (ARI)
surveillance began. The other schemes are being checked with JIHS. Public data only.

**Thresholds.** 1.0 report per sentinel site marks the start of the influenza epidemic season. IDWR uses 10 and 30
per sentinel as the caution and warning levels for public health center areas; this app draws them at prefecture
level for reference. These lines apply to influenza only.

**Limits of the data.** Sentinel reports reflect care-seeking and reporting practice, not incidence. The latest
week may be revised. Prefectures with few sentinels show more week-to-week noise. Clinic closures around New Year
lower reports in weeks 52 and 1.

**New Year weeks.** The clinic closures around New Year lower reports in weeks 52, 53 and 1, and the rebound
afterward can look like a sudden rise. By default this app leaves weeks 52, 53 and 1 out of every C2 baseline;
the remaining baseline weeks are used if at least 5 are left. The Alerts tab shows how many alerts in weeks 2 to 8
that removes. The R alert report keeps every week, so its January alerts can differ until it uses the same rule.

**These alerts are retrospective.** C2 here runs on the latest file, in which earlier weeks may have been revised
after first publication. A system running in real time would have seen the provisional values each week, and an
alert could have come later, earlier, or not at all. The alert threshold of 3 and the {FA_WINDOW}-week window used
to count false alarms were set while looking at these data. Lead times and false-alarm counts are therefore
best-case estimates for how C2 would perform on future seasons, not a measured real-time performance.

**Spatial statistics.** Global Moran's I and local Moran (LISA) from PySAL `esda`, {PERMUTATIONS} permutations.
Weights: queen contiguity on the full-resolution prefecture boundaries (dataofjapan/land), with Hokkaido-Aomori,
Okinawa-Kagoshima and Fukuoka-Yamaguchi added so every prefecture has a neighbor; row-standardized.
**Alerts.** EARS C2: 7-week baseline (t-9 to t-3), two-week guard, population SD floored at 0.1, at least 5
baseline weeks. **Maps.** Prefecture outlines from dataofjapan/land, simplified for display and bundled in
`static/`, so the maps need no outside download. Population from the 2020 Population Census (e-Stat), shown for
reference only.

**This copy.** {'SAMPLE DATA. Synthetic values for layout only. No real surveillance values are shown.' if is_sample else
 f'IDWR reports per sentinel site for all 47 prefectures, {week_labels[0]} to {week_labels[-1]}, from the prefecture '
 'table written by the IDWR alert report R script. C2 starts 9 weeks into the table, because each week needs 9 '
 'earlier weeks for its baseline and guard.'}

**Built with** Python, Streamlit, pandas, Plotly, PySAL (esda, libpysal). Code: `app.py` {VERSION}.
""")
