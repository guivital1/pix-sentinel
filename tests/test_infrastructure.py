from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_infrastructure_is_disabled_by_default() -> None:
    template = (ROOT / "template.yaml").read_text(encoding="utf-8")
    assert 'Default: "false"' in template
    assert "StartingPosition: LATEST" in template
    assert "RetentionPeriodHours: 24" in template


def test_data_has_expiration_policy_and_encryption() -> None:
    template = (ROOT / "template.yaml").read_text(encoding="utf-8")
    assert "ExpirationInDays: 30" in template
    assert "BucketEncryption:" in template
    assert "PublicAccessBlockConfiguration:" in template

