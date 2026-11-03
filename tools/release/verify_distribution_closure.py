"""Install selected release wheels with registry dependencies before upload."""

from __future__ import annotations

import argparse
import email
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


def verify(directory: Path) -> None:
    wheels = sorted(directory.resolve().glob("*.whl"))
    if not wheels:
        raise ValueError("No release wheels found")
    modules = []
    for wheel in wheels:
        with zipfile.ZipFile(wheel) as archive:
            metadata = email.message_from_bytes(archive.read(next(
                name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
            )))
        modules.append(metadata["Name"].replace("-", "_"))
    smoke = (
        "import importlib,json; "
        f"modules={modules!r}; "
        "[importlib.import_module(name) for name in modules]; "
        "print(json.dumps({'imported':modules}))"
    )
    if "tigrbl" in modules:
        smoke += (
            "; from tigrbl import provideTableHandler, create_table_record, "
            "database_from_context, payload_from_context, deriveTableSpec, makeOp"
            "; from tigrbl_concrete._concrete._engine_session import EngineSession"
            "; from tigrbl_base._base import EngineSessionBase"
            "; assert issubclass(EngineSession, EngineSessionBase)"
        )
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required")
    env = dict(os.environ)
    for key in list(env):
        if key.startswith(("UV_INDEX", "UV_EXTRA_INDEX", "UV_DEFAULT_INDEX", "UV_FIND_LINKS", "PIP_INDEX", "PIP_EXTRA_INDEX")) or key in {"PYTHONPATH", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"}:
            env.pop(key, None)
    command = [uv, "--no-config", "run", "--no-project", "--isolated", "--python", sys.executable,
               "--default-index", "https://pypi.org/simple"]
    for wheel in wheels:
        command.extend(["--with", str(wheel)])
    command.extend(["python", "-I", "-c", smoke])
    with tempfile.TemporaryDirectory(prefix="tigrbl-release-closure-") as isolated:
        subprocess.run(command, cwd=isolated, env=env, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    verify(args.directory)


if __name__ == "__main__":
    main()
