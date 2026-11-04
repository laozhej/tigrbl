import importlib.util
from pathlib import Path
import subprocess
import zipfile

import pytest


@pytest.mark.parametrize("has_module", [True, False])
def test_wheel_install_must_supply_its_importable_package(tmp_path, has_module):
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("closure", root / "tools/release/verify_distribution_closure.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    wheel = tmp_path / "closure_probe-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        prefix = "closure_probe-0.1.0.dist-info/"
        archive.writestr(prefix + "METADATA", "Metadata-Version: 2.1\nName: closure-probe\nVersion: 0.1.0\n")
        archive.writestr(prefix + "WHEEL", "Wheel-Version: 1.0\nGenerator: closure-test\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
        archive.writestr(prefix + "RECORD", "")
        if has_module:
            archive.writestr("closure_probe/__init__.py", "")
    if has_module:
        module.verify(tmp_path)
    else:
        with pytest.raises(subprocess.CalledProcessError):
            module.verify(tmp_path)
