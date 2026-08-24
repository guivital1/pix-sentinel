import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_assets_and_sample_data_exist() -> None:
    html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    script = (ROOT / "docs/dashboard.js").read_text(encoding="utf-8")
    data = json.loads((ROOT / "docs/data/dashboard.json").read_text(encoding="utf-8"))
    assert "PIX Sentinel" in html
    assert "data/dashboard.json" in script
    assert data["summary"]["transactions"] >= 100
