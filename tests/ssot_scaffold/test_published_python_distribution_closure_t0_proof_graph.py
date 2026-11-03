from pathlib import Path

import yaml


def test_registry_upload_waits_for_built_wheel_dependency_verification():
    root = Path(__file__).resolve().parents[2]
    jobs = yaml.safe_load((root / ".github/workflows/publish.yml").read_text())["jobs"]
    assert "verify-python-distribution-closure" in jobs["publish-pypi"]["needs"]
    assert "build-python-packages" in jobs["verify-python-distribution-closure"]["needs"]
