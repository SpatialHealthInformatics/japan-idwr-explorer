"""Update data/idwr_weekly.csv from the JIHS IDWR provisional yearly prefecture file.

Source (public): https://id-info.jihs.go.jp/surveillance/idwr/provisional/<year>/<WW>/<year>-<WW>-teiten-tougai.csv
The file is Shift-JIS (CP932). It holds one block per sentinel disease (19 blocks). Each block has a total row and
47 prefecture rows; every row carries (reports, reports per sentinel site) for weeks 1 to WW.

Run:
  python tools/update_idwr_data.py                 download the latest posted week and rewrite the data file
  python tools/update_idwr_data.py --file F.csv    use a file already on disk (no download)
  python tools/update_idwr_data.py --check         only report what would change; write nothing

Rules
  - The latest year's rows are replaced by the new file, so JIHS revisions are picked up. Rows of other years stay.
  - Nothing is written unless the file passes every check. A failed check exits with a message and a nonzero code.
  - The last line printed is "DATA_THROUGH <year>-W<ww>" (used by the GitHub workflow for the commit message).
"""
import argparse
import datetime as dt
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "idwr_weekly.csv"
NAMES = ROOT / "data" / "prefecture_names.csv"
BASE_URL = "https://id-info.jihs.go.jp/surveillance/idwr/provisional"
USER_AGENT = "japan-idwr-explorer-updater (+https://github.com/SpatialHealthInformatics/japan-idwr-explorer)"
LOOKBACK_WEEKS = 8
COLUMNS = ["year", "week", "week_start", "pref_code", "prefecture", "disease", "per_sentinel"]

# Japanese block title in the file -> disease name used in the app. File order is kept.
DISEASES = {
    "インフルエンザ": "Influenza",
    "ＲＳウイルス感染症": "RSV infection",
    "咽頭結膜熱": "Pharyngoconjunctival fever",
    "Ａ群溶血性レンサ球菌咽頭炎": "Group A streptococcal pharyngitis",
    "感染性胃腸炎": "Infectious gastroenteritis",
    "水痘": "Chickenpox",
    "手足口病": "Hand, foot and mouth disease",
    "伝染性紅斑": "Erythema infectiosum",
    "突発性発しん": "Exanthem subitum",
    "ヘルパンギーナ": "Herpangina",
    "流行性耳下腺炎": "Mumps",
    "急性出血性結膜炎": "Acute hemorrhagic conjunctivitis",
    "流行性角結膜炎": "Epidemic keratoconjunctivitis",
    "細菌性髄膜炎": "Bacterial meningitis",
    "無菌性髄膜炎": "Aseptic meningitis",
    "マイコプラズマ肺炎": "Mycoplasma pneumonia",
    "クラミジア肺炎": "Chlamydial pneumonia",
    "感染性胃腸炎（ロタウイルス）": "Rotavirus gastroenteritis",
    "COVID-19": "COVID-19",
}


class CheckFailed(Exception):
    pass


def prefectures():
    p = pd.read_csv(NAMES)
    if len(p) != 47:
        raise CheckFailed("data/prefecture_names.csv must have 47 rows")
    return p


def fetch(year, week):
    url = f"{BASE_URL}/{year}/{week:02d}/{year}-{week:02d}-teiten-tougai.csv"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise CheckFailed(f"JIHS answered HTTP {e.code} for {url}")
    except urllib.error.URLError as e:
        raise CheckFailed(f"Could not reach JIHS ({e.reason}) for {url}")
    if len(body) < 10000:
        raise CheckFailed(f"File from {url} is only {len(body)} bytes, too small to be the yearly file")
    return body


def fetch_latest(today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    for back in range(LOOKBACK_WEEKS + 1):
        y, w, _ = (today - dt.timedelta(weeks=back)).isocalendar()
        body = fetch(y, w)
        if body is not None:
            return y, w, body
    raise CheckFailed(f"No yearly file found on JIHS for the last {LOOKBACK_WEEKS + 1} weeks")


def parse(body, year, week):
    """Return a tidy DataFrame (COLUMNS) for one yearly file, or raise CheckFailed."""
    try:
        lines = body.decode("cp932").splitlines()
    except UnicodeDecodeError as e:
        raise CheckFailed(f"File is not Shift-JIS text: {e}")
    cells = [[c.strip() for c in ln.replace('"', "").split(",")] for ln in lines]
    m = re.match(r"(\d{4})年(\d{1,2})週", cells[1][0]) if len(cells) > 1 else None
    if not m or (int(m.group(1)), int(m.group(2))) != (year, week):
        raise CheckFailed(f"Header says {cells[1][0] if len(cells) > 1 else '?'}, expected {year}年{week}週")
    pref = prefectures()
    ja = pref["prefecture_ja"].tolist()
    starts = {}
    for i, c in enumerate(cells):
        if c and c[0] in DISEASES and all(x == "" for x in c[1:]):
            starts[c[0]] = i
    missing = [d for d in DISEASES if d not in starts]
    if missing:
        raise CheckFailed(f"Disease blocks missing in file: {', '.join(missing)}")
    out = []
    for jp, en in DISEASES.items():
        i = starts[jp]
        head = cells[i + 1]
        weeks = [int(re.match(r"(\d+)週", h).group(1)) for h in head[3::2] if re.match(r"\d+週", h)]
        if weeks != list(range(1, week + 1)):
            raise CheckFailed(f"{en}: week columns are not 1 to {week}")
        rows = cells[i + 3:i + 3 + 48]          # total row, then 47 prefectures
        if len(rows) != 48 or rows[0][0] != "総数":
            raise CheckFailed(f"{en}: total row not found")
        for code, (row, name) in enumerate(zip(rows[1:], ja), start=1):
            if row[0] != name:
                raise CheckFailed(f"{en}: row {code} is {row[0]}, expected {name}")
            if len(row) != 3 + 2 * week:
                raise CheckFailed(f"{en} {name}: {len(row)} cells, expected {3 + 2 * week}")
            for w in range(1, week + 1):
                tok = row[2 + 2 * w]             # per-sentinel value of week w
                try:
                    val = float(tok) if tok not in ("", "-") else float("nan")
                except ValueError:
                    raise CheckFailed(f"{en} {name} week {w}: '{tok}' is not a number")
                if val < 0:
                    raise CheckFailed(f"{en} {name} week {w}: negative value {val}")
                start = dt.date.fromisocalendar(year, w, 1)
                out.append((year, w, start.isoformat(), code, pref.loc[code - 1, "prefecture"], en, val))
    df = pd.DataFrame(out, columns=COLUMNS)
    if len(df) != 19 * 47 * week:
        raise CheckFailed(f"Expected {19 * 47 * week} rows, built {len(df)}")
    return df


def combine(new, year):
    """Replace the rows of `year` in the current data file with `new`; keep the other years."""
    order = {en: i for i, en in enumerate(DISEASES.values())}
    if DATA.exists():
        old = pd.read_csv(DATA)
        keep = old[old["year"] != year]
        prior = old[old["year"] == year]
        if len(prior) and prior["week"].max() > new["week"].max():
            raise CheckFailed(f"New file ends at week {new['week'].max()} but the data already has week "
                              f"{prior['week'].max()} for {year}; not overwriting with older data")
        df = pd.concat([keep, new], ignore_index=True)
    else:
        df = new
    df["_d"] = df["disease"].map(order)
    df = df.sort_values(["_d", "pref_code", "year", "week"]).drop(columns="_d").reset_index(drop=True)
    return df[COLUMNS]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", help="read this yearly file instead of downloading (name must be YYYY-WW-teiten-tougai.csv)")
    ap.add_argument("--check", action="store_true", help="report only; write nothing")
    a = ap.parse_args(argv)
    try:
        if a.file:
            m = re.match(r"(\d{4})-(\d{2})-teiten-tougai", Path(a.file).name)
            if not m:
                raise CheckFailed("File name must start with YYYY-WW-teiten-tougai")
            year, week, body = int(m.group(1)), int(m.group(2)), Path(a.file).read_bytes()
        else:
            year, week, body = fetch_latest()
        new = parse(body, year, week)
        df = combine(new, year)
    except CheckFailed as e:
        print(f"CHECK FAILED: {e}", file=sys.stderr)
        return 1
    text = df.to_csv(index=False, lineterminator="\n")
    old_text = DATA.read_text(encoding="utf-8") if DATA.exists() else ""
    changed = text != old_text
    through = f"{year}-W{week:02d}"
    print(f"Parsed {len(new)} rows for {through}; data file {'changes' if changed else 'is already current'}.")
    if changed and not a.check:
        DATA.write_text(text, encoding="utf-8")
        print(f"Wrote {DATA.relative_to(ROOT)} ({len(df)} rows).")
    print(f"DATA_THROUGH {through}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
