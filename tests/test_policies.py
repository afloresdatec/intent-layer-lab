import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"

conftest_available = shutil.which("conftest") is not None
kustomize_available = shutil.which("kustomize") is not None

pytestmark = pytest.mark.skipif(
    not conftest_available, reason="conftest no está instalado en este entorno"
)


def run_conftest(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["conftest", "test", str(path), "-p", str(REPO_ROOT / "policies"), "-o", "json"],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    "fixture",
    ["bad_latest_tag.yaml", "bad_missing_limits.yaml", "bad_disallowed_kind.yaml"],
)
def test_bad_fixtures_are_denied(fixture):
    result = run_conftest(FIXTURES / fixture)
    assert result.returncode != 0, f"{fixture} debería violar alguna política"


@pytest.mark.skipif(
    not kustomize_available, reason="kustomize no está instalado en este entorno"
)
def test_current_overlay_passes_policies():
    rendered = subprocess.run(
        ["kustomize", "build", str(REPO_ROOT / "apps" / "intent-lab" / "overlays" / "dev")],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    result = subprocess.run(
        ["conftest", "test", "-", "-p", str(REPO_ROOT / "policies")],
        input=rendered,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
