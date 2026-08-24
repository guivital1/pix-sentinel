import json

from pix_sentinel.pipeline import run_local_pipeline


def test_local_pipeline_builds_dashboard_payload(tmp_path) -> None:
    output = tmp_path / "dashboard.json"
    payload = run_local_pipeline(200, 42, output)
    saved = json.loads(output.read_text(encoding="utf-8"))

    assert payload == saved
    assert payload["summary"]["transactions"] == 200
    assert sum(payload["risk_distribution"].values()) == 200
    assert payload["summary"]["alerts"] > 0
    assert len(payload["alerts"]) <= 12
