"""AppTest: drive every control and check nothing raises. Run: python -m pytest tests -q
AppTest never renders the page, so also look at the app in a browser after any visual change."""
import os
from pathlib import Path
from streamlit.testing.v1 import AppTest

os.environ["JIE_SAMPLE"] = "1"  # the real CSV is not in the repo during development
APP = str(Path(__file__).resolve().parents[1] / "app.py")


def _app():
    return AppTest.from_file(APP, default_timeout=240).run()


def test_loads():
    at = _app()
    assert not at.exception


def test_prefectures_and_weeks():
    at = _app()
    at.sidebar.selectbox(key="to_add").set_value("Hokkaido").run()
    at.sidebar.button(key="add_pref").click().run()
    assert not at.exception and "Hokkaido" in at.session_state["prefs"]
    sl = at.sidebar.select_slider
    sl[0].set_value(sl[0].options[10]).run()
    assert not at.exception
    at.sidebar.multiselect(key="prefs").set_value([]).run()
    assert not at.exception


def test_options_and_buttons():
    at = _app()
    at.sidebar.radio(key="layout").set_value("One panel per prefecture").run()
    assert not at.exception
    for t in at.sidebar.toggle:
        t.set_value(not t.value).run()
        assert not at.exception
    for key in ("pmap_area",):
        for opt in ["Kanto (Tokyo area)", "Kansai (Osaka area)", "Selected prefectures", "Kanto and Kansai"]:
            at.radio(key=key).set_value(opt).run()
            assert not at.exception
    at.radio(key="jmap_scale_True").set_value("Continuous").run()
    at.slider(key="ears_thr").set_value(2.0).run()
    assert not at.exception
    for b in at.button:
        if b.key and b.key.startswith("btn_"):
            b.click().run()
            assert not at.exception


def test_real_data_or_stop(monkeypatch):
    """With data/idwr_weekly.csv the app shows real data; without it, it stops."""
    monkeypatch.delenv("JIE_SAMPLE")
    at = AppTest.from_file(APP, default_timeout=180).run()
    assert not at.exception
    real = (Path(APP).parent / "data" / "idwr_weekly.csv").exists()
    if real:
        assert len(at.tabs) == 8
        assert not any("SAMPLE" in t.value for t in at.title)
    else:
        assert any("not loaded yet" in e.value for e in at.error)
        assert len(at.tabs) == 0


def test_other_diseases():
    """Every disease loads; non-influenza diseases hide the 1.0-based measures and the IDWR level shading."""
    def disease_box(at):
        return next(b for b in at.sidebar.selectbox if b.label == "Disease")

    at = _app()
    for dis in list(disease_box(at).options):
        disease_box(at).set_value(dis).run()
        assert not at.exception, dis
    disease_box(at).set_value("RSV infection").run()
    assert not at.exception
    assert at.radio(key="jmap_scale_False").options == ["Continuous"]
    at.slider(key="ears_thr").set_value(2.0).run()
    assert not at.exception
    disease_box(at).set_value("Influenza").run()
    assert not at.exception
