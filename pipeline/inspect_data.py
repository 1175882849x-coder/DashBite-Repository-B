"""Print pipeline artifact inventory and dashboard helper values."""
import argparse
import hashlib
import json
import joblib
import numpy as np
from pipeline.dashboard.app import load_features, load_predictions, load_quality_log
from pipeline.dashboard.ml_metrics import sample_volume, score_summary
from pipeline.dashboard.biz_metrics import late_rate, at_risk_order_value
from pipeline.dashboard.quality_metrics import throughput_summary
from pipeline.paths import data_root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true", help="Stable content hashes; stop writers first")
    parser.add_argument("--validate", action="store_true", help="Assert pipeline artifact contracts")
    args = parser.parse_args()
    if args.snapshot:
        print(json.dumps({str(p.relative_to(data_root())): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(data_root().rglob("*")) if p.is_file()}, sort_keys=True, indent=2))
        return
    for path in sorted(data_root().rglob("*")):
        if path.is_file():
            print(f"{path.relative_to(data_root())}: {path.stat().st_size} bytes")
    features, predictions = load_features(), load_predictions()
    if args.validate:
        quality = load_quality_log()
        assert not features.empty and not predictions.empty and not quality.empty
        assert features.notna().all().all()
        assert {"hour", "is_peak"}.issubset(features.columns)
        assert (quality.rows_in == quality.rows_out + quality.rows_dropped).all()
        assert set(predictions.order_id).issubset(set(features.order_id))
        assert not predictions.order_id.duplicated().any()
        assert np.isfinite(predictions.late_probability).all()
        assert predictions.late_probability.between(0, 1).all()
        assert predictions.predicted_late.isin([0, 1]).all()
        checkpoints = {joblib.load(p)["checkpoint_id"] for p in (data_root() / "models").glob("checkpoint_*.joblib")}
        assert set(predictions.checkpoint_id).issubset(checkpoints)
        metrics = [json.loads(p.read_text()) for p in (data_root() / "models").glob("metrics_*.json")]
        assert metrics and all(0 <= m["accuracy"] <= 1 and m["n_train"] > 0 for m in metrics)
        state = json.loads((data_root() / "models/train_state.json").read_text())
        assert (data_root() / "models" / state["last_checkpoint"]).is_file()
        print("PASS: pipeline artifact contracts (snapshot may contain pending unscored features)")
    print(json.dumps({"samples": sample_volume(features),
                      "scores": score_summary(predictions),
                      "late_rate": late_rate(features),
                      "at_risk_value": at_risk_order_value(features, predictions),
                      "throughput": throughput_summary(load_quality_log())}, indent=2))


if __name__ == "__main__":
    main()
