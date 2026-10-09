import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import apply_intent  # noqa: E402


def _isolate(tmp_path, monkeypatch):
    """Copia overlay/base reales a un tmp_path y redirige el módulo ahí,
    para no mutar el repo real al correr las pruebas."""
    overlay_src = REPO_ROOT / "apps" / "intent-lab" / "overlays" / "dev" / "kustomization.yaml"
    base_src = REPO_ROOT / "apps" / "intent-lab" / "base" / "deployment.yaml"

    overlay_dst = tmp_path / "kustomization.yaml"
    base_dst = tmp_path / "deployment.yaml"
    shutil.copy(overlay_src, overlay_dst)
    shutil.copy(base_src, base_dst)

    monkeypatch.setattr(apply_intent, "OVERLAY_KUSTOMIZATION", overlay_dst)
    monkeypatch.setattr(apply_intent, "BASE_DEPLOYMENT", base_dst)
    return overlay_dst


def test_scale_deployment_updates_replicas(tmp_path, monkeypatch):
    overlay_dst = _isolate(tmp_path, monkeypatch)
    intent = {
        "intent": "scale_deployment",
        "target": "intent-lab",
        "namespace": "intent-lab",
        "requested_by": "ai-assistant@example.invalid",
        "params": {"replicas": 5},
    }

    apply_intent.apply_intent(intent)

    result = yaml.safe_load(overlay_dst.read_text())
    entry = next(e for e in result["replicas"] if e["name"] == "intent-lab")
    assert entry["count"] == 5


def test_set_image_tag_updates_image(tmp_path, monkeypatch):
    overlay_dst = _isolate(tmp_path, monkeypatch)
    intent = {
        "intent": "set_image_tag",
        "target": "intent-lab",
        "namespace": "intent-lab",
        "requested_by": "ai-assistant@example.invalid",
        "params": {"image_tag": "1.27.4"},
    }

    apply_intent.apply_intent(intent)

    result = yaml.safe_load(overlay_dst.read_text())
    entry = next(e for e in result["images"] if e["name"] == "docker.io/library/nginx")
    assert entry["newTag"] == "1.27.4"


def test_invalid_intent_is_rejected(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    intent = {
        "intent": "delete_namespace",
        "target": "intent-lab",
        "namespace": "intent-lab",
        "requested_by": "ai-assistant@example.invalid",
        "params": {},
    }

    try:
        apply_intent.apply_intent(intent)
        assert False, "debería haber lanzado ValueError"
    except ValueError:
        pass
