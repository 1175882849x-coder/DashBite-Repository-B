"""Render both inherited views with fixed data, without live pipeline writers."""
from pathlib import Path
import shutil

import pytest
from streamlit.testing.v1 import AppTest

from pipeline.paths import ensure_data_dirs
from tests.conftest import FIXTURES


@pytest.mark.integration
@pytest.mark.parametrize("populated", [True, False])
@pytest.mark.parametrize("page", ["Model Pulse", "Ops Control"])
def test_dashboard_views_render_populated_metrics(tmp_path, page, populated):
    dirs = ensure_data_dirs(tmp_path)
    if populated:
        shutil.copy(FIXTURES / "features_biz.csv", dirs["features"] / "features_fixed.csv")
        shutil.copy(FIXTURES / "predictions_sample.csv", dirs["predictions"] / "predictions_fixed.csv")
    # Disable the timed rerun only in this harness; retain the real app and widgets.
    script = f"""
from pathlib import Path
from unittest.mock import patch
import streamlit as st
from pipeline.dashboard import app
original_checkbox = st.sidebar.checkbox

def checkbox_without_auto_refresh(label, value=False, **kwargs):
    return original_checkbox(label, value=False, **kwargs)

with patch.object(app, 'PROJECT_ROOT', Path({str(tmp_path)!r})), patch.object(st.sidebar, 'checkbox', checkbox_without_auto_refresh):
    app.main()
"""
    app = AppTest.from_string(script).run(timeout=15)
    app.sidebar.radio[0].set_value(page).run(timeout=15)
    assert not app.exception, [error.message for error in app.exception]
    assert app.header[0].value == page
    metrics = {metric.label: metric.value for metric in app.metric}
    if not populated:
        assert any("No predictions yet" in info.value for info in app.info)
        if page == "Model Pulse":
            assert metrics["Sample volume"] == "0"
        else:
            assert metrics["Orders at risk (value)"] == "$0.00"
        return
    if page == "Model Pulse":
        assert int(metrics["Sample volume"]) > 0
        assert 0 <= float(metrics["Mean late probability"]) <= 1
    else:
        assert 0 <= float(metrics["Late rate"].rstrip("%")) <= 100
        assert float(metrics["Orders at risk (value)"].replace("$", "").replace(",", "")) > 0
        assert len(app.dataframe) > 0
