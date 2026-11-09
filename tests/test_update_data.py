# Maintained by SpatialHealthInformatics
"""Tests for tools/update_idwr_data.py using a small synthetic yearly file (no network).
Run: python -m pytest tests/test_update_data.py -q"""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import update_idwr_data as u  # noqa: E402

YEAR, WEEK = 2026, 3


def make_file(week=WEEK, header_week=None, edit=None):
    pref = pd.read_csv(ROOT / "data" / "prefecture_names.csv")["prefecture_ja"].tolist()
    L = ["報告数・定点当り報告数", f"{YEAR}年{header_week or week}週(1月1日～1月4日),{YEAR}年1月7日作成"]
    for jp in u.DISEASES:
        L.append(jp + "," * (3 + 2 * week))
        L.append("," + "総数,総数," + ",".join(f"{w:02d}週,{w:02d}週" for w in range(1, week + 1)))
        L.append("," + "報告,定当," + ",".join("報告,定当" for _ in range(week)))
        for name in ["総数"] + pref:
            cells = [name, "10", "1.0"]
            for w in range(1, week + 1):
                cells += ["5", f"{w}.5"]
            L.append(",".join(cells))
    text = "\n".join(L)
    if edit:
        text = text.replace(*edit, 1)
    return text.encode("cp932")


def test_parse_shape_and_values():
    df = u.parse(make_file(), YEAR, WEEK)
    assert len(df) == 19 * 47 * WEEK
    assert list(df.columns) == u.COLUMNS
    assert df["disease"].iloc[0] == "Influenza" and df["pref_code"].max() == 47
    assert df[df.week == 2]["per_sentinel"].eq(2.5).all()
    assert df[df.week == 1]["week_start"].iloc[0] == "2025-12-29"


@pytest.mark.parametrize("kwargs", [
    {"header_week": 2},
    {"edit": ("北海道,10,1.0,5,1.5", "北海道,10,1.0,5,abc")},
    {"edit": ("北海道,10,1.0,5,1.5", "北海道,10,1.0,5,-3")},
    {"edit": ("北海道", "北海島")},
    {"edit": ("ヘルパンギーナ", "ヘルパ")},
])
def test_bad_files_are_rejected(kwargs):
    with pytest.raises(u.CheckFailed):
        u.parse(make_file(**kwargs), YEAR, WEEK)


def test_not_shift_jis():
    with pytest.raises(u.CheckFailed):
        u.parse("日本".encode("utf-16"), YEAR, WEEK)


def test_combine_keeps_other_years_and_refuses_older(tmp_path, monkeypatch):
    new = u.parse(make_file(), YEAR, WEEK)
    old25 = new.assign(year=2025, week_start="2025-01-06")
    f = tmp_path / "idwr_weekly.csv"
    old25.to_csv(f, index=False)
    monkeypatch.setattr(u, "DATA", f)
    out = u.combine(new, YEAR)
    assert set(out["year"]) == {2025, 2026} and len(out) == 2 * len(new)
    out.to_csv(f, index=False)
    with pytest.raises(u.CheckFailed):
        u.combine(u.parse(make_file(week=2), YEAR, 2), YEAR)
