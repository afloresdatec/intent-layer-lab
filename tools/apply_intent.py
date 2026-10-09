#!/usr/bin/env python3
"""Traduce un intent VALIDADO a un cambio determinista sobre el overlay
apps/intent-lab/overlays/dev/kustomization.yaml.

No aplica nada al clúster ni hace commit: solo escribe el archivo local.
El cambio resultante se revisa y aprueba como cualquier otro, vía PR.

Uso: apply_intent.py <intent.json>
"""
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_intent import validate_intent  # noqa: E402

OVERLAY_KUSTOMIZATION = REPO_ROOT / "apps" / "intent-lab" / "overlays" / "dev" / "kustomization.yaml"
BASE_DEPLOYMENT = REPO_ROOT / "apps" / "intent-lab" / "base" / "deployment.yaml"


def base_image_repo() -> str:
    deployment = yaml.safe_load(BASE_DEPLOYMENT.read_text())
    image = deployment["spec"]["template"]["spec"]["containers"][0]["image"]
    repo, _, _tag = image.rpartition(":")
    return repo


def apply_intent(intent: dict) -> str:
    """Muta kustomization.yaml in-place. Devuelve una descripción del cambio."""
    errors = validate_intent(intent)
    if errors:
        raise ValueError(f"intent inválido: {errors}")

    kustomization = yaml.safe_load(OVERLAY_KUSTOMIZATION.read_text())
    target = intent["target"]

    if intent["intent"] == "scale_deployment":
        replicas = intent["params"]["replicas"]
        entries = kustomization.setdefault("replicas", [])
        entry = next((e for e in entries if e["name"] == target), None)
        if entry is None:
            entry = {"name": target, "count": replicas}
            entries.append(entry)
        else:
            entry["count"] = replicas
        change = f"replicas[{target}] -> {replicas}"

    elif intent["intent"] == "set_image_tag":
        image_tag = intent["params"]["image_tag"]
        repo = base_image_repo()
        entries = kustomization.setdefault("images", [])
        entry = next((e for e in entries if e["name"] == repo), None)
        if entry is None:
            entry = {"name": repo, "newTag": image_tag}
            entries.append(entry)
        else:
            entry["newTag"] = image_tag
        change = f"images[{repo}].newTag -> {image_tag}"

    else:
        raise ValueError(f"intent desconocido: {intent['intent']}")

    OVERLAY_KUSTOMIZATION.write_text(
        yaml.safe_dump(kustomization, sort_keys=False, default_flow_style=False)
    )
    return change


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"uso: {argv[0]} <intent.json>", file=sys.stderr)
        return 2

    intent = json.loads(Path(argv[1]).read_text())
    try:
        change = apply_intent(intent)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Aplicado localmente a {OVERLAY_KUSTOMIZATION.relative_to(REPO_ROOT)}: {change}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
