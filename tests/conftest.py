"""Fixture bersama: satu pipeline penuh di direktori sementara (session scope)."""
from pathlib import Path

import pytest

from _util import run_script


@pytest.fixture(scope="session")
def workspace(tmp_path_factory) -> Path:
    ws = tmp_path_factory.mktemp("qris")
    (ws / "data" / "bronze").mkdir(parents=True)
    (ws / "reports").mkdir()
    for script in ["gen_qris.py", "clean_silver.py", "build_gold.py", "forecast.py", "model.py"]:
        run_script(script, ws)
    return ws


@pytest.fixture(scope="session")
def retrain_workspace(workspace: Path) -> Path:
    run_script("run_retrain.py", workspace)
    return workspace
