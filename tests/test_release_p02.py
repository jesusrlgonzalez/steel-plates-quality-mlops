"""The release ZIP carries the P02 evidence complete, intact and reproducible (Owner order A5, A5-D12)."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
P02 = "reports/pilots/P02"
REQUIRED = (
    [f"docs/pilots/P02/{f}" for f in ("README.md", "00_ficha_ejecutiva.md", "01_caso_empresarial.md",
                                      "02_datos_y_escenarios.md", "03_resultados.md", "04_dictamen.md")]
    + [f"{P02}/{f}" for f in ("manifest.json", "raw_export_history.csv", "decisions.csv", "results.json",
                              "sensitivity.csv", "seguimiento_revision.csv", "evidence.json")]
    + ["src/quality_ml/pilot_p02.py", "src/quality_ml/review_policy.py", "examples/review_triage/inspeccion_placas.csv",
       "tests/test_pilot_p02.py", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "LICENSE"]
)
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    if shutil.which("git") is None or not (ROOT / ".git").exists():
        pytest.skip("needs a git checkout")
    out = tmp_path_factory.mktemp("bundle") / "p02.zip"
    subprocess.run(["bash", "deploy/build_release_bundle.sh", "HEAD", str(out), "deploy/release-assets-p02.txt"],
                   cwd=ROOT, check=True)
    return zipfile.ZipFile(out)


def test_bundle_contains_every_required_p02_element(bundle):
    missing = sorted(set(REQUIRED) - set(bundle.namelist()))
    assert not missing, missing


def test_bundle_hashes_match_the_recorded_evidence(bundle):
    ev = json.loads(bundle.read(f"{P02}/evidence.json"))
    for name, h in ev["salidas"].items():
        assert sha(bundle.read(f"{P02}/{name}")) == h, name
    for path, h in ev["codigo_y_fuente"].items():
        assert sha(bundle.read(path)) == h, path
    assert all(ev["criterios"].values())


def test_bundle_alone_regenerates_identical_p02_outputs(bundle, tmp_path):
    bundle.extractall(tmp_path)
    ev = json.loads((tmp_path / P02 / "evidence.json").read_text(encoding="utf-8"))
    for name in ev["salidas"]:
        (tmp_path / P02 / name).unlink()
    env = {**os.environ, "PYTHONPATH": str(tmp_path / "src")}
    subprocess.run([sys.executable, "-B", "-m", "quality_ml.pilot_p02"], cwd=tmp_path, env=env, check=True,
                   stdout=subprocess.DEVNULL)
    for name, h in ev["salidas"].items():
        assert sha((tmp_path / P02 / name).read_bytes()) == h, name
