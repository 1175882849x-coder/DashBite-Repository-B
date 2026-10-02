import json
import joblib
import numpy as np
import pandas as pd
import pytest
from tests.conftest import FIXTURES
from pipeline.config import Config
from pipeline.paths import ensure_data_dirs
from pipeline.preprocess import process_new_raw_files
from pipeline.train import maybe_train, load_state
from pipeline.infer import run_once
from pipeline.dashboard.app import load_features, load_predictions, load_quality_log
from pipeline.dashboard.ml_metrics import sample_volume, score_summary
from pipeline.dashboard.biz_metrics import late_rate, at_risk_order_value
from pipeline.dashboard.quality_metrics import throughput_summary


@pytest.mark.integration
def test_raw_to_dashboard_and_no_duplicate_work(tmp_path):
    dirs = ensure_data_dirs(tmp_path)
    raw = pd.read_csv(FIXTURES / "raw_seed123.csv")
    assert set(raw.was_late) == {0, 1}
    bad = raw.iloc[[0]].copy()
    bad["order_id"] = "invalid-fixed-id"
    bad["distance_km"] = -1
    pd.concat([raw, bad]).to_csv(dirs["raw"] / "orders_fixed.csv", index=False)
    assert len(process_new_raw_files(tmp_path)) == 1
    features = load_features(tmp_path)
    assert len(features) == len(raw) > 0
    assert set(features.order_id) == set(raw.order_id)
    assert features.notna().all().all()
    assert (features.distance_km > 0).all()
    assert set(features.hour) == {12}
    assert set(features.is_peak) == {1}
    quality = load_quality_log(tmp_path)
    assert (quality.rows_in == quality.rows_out + quality.rows_dropped).all()
    assert quality.rows_dropped.sum() == 1
    cfg = Config(train_every_n_events=4, random_seed=42)
    checkpoint = maybe_train(cfg, tmp_path)
    bundle = joblib.load(checkpoint)
    metrics = json.loads(next(dirs["models"].glob("metrics_*.json")).read_text())
    assert 0 <= metrics["accuracy"] <= 1
    assert metrics["n_train"] + metrics["n_test"] == len(features)
    assert metrics["checkpoint_id"] == bundle["checkpoint_id"]
    assert load_state(tmp_path) == {"labeled_rows_at_last_train": len(features), "last_checkpoint": checkpoint.name}
    assert run_once(cfg, tmp_path) is not None
    predictions = load_predictions(tmp_path)
    assert set(predictions.order_id) == set(features.order_id)
    assert not predictions.order_id.duplicated().any()
    assert np.isfinite(predictions.late_probability).all()
    assert predictions.late_probability.between(0, 1).all()
    assert predictions.predicted_late.isin([0, 1]).all()
    assert set(predictions.checkpoint_id) == {bundle["checkpoint_id"]}
    assert sample_volume(features) == len(raw)
    summary = score_summary(predictions)
    assert summary["count"] == len(raw)
    assert summary["mean_probability"] == pytest.approx(predictions.late_probability.mean())
    assert late_rate(features) == pytest.approx(raw.was_late.mean())
    expected_risk = features.set_index("order_id").loc[predictions.loc[predictions.predicted_late == 1, "order_id"], "order_value"].sum()
    assert at_risk_order_value(features, predictions) == pytest.approx(expected_risk)
    assert throughput_summary(quality)["rows_out"] == len(raw)
    before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert process_new_raw_files(tmp_path) == []
    assert run_once(cfg, tmp_path) is None
    assert maybe_train(cfg, tmp_path) is None
    assert before == {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
