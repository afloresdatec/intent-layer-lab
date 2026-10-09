#!/usr/bin/env python3
"""Valida un archivo de intent contra schemas/intent.schema.json.

Uso: validate_intent.py <intent.json>
Sale con código 0 si es válido, 1 si no lo es (imprime los errores).
"""
import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "intent.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def validate_intent(intent: dict, schema: dict | None = None) -> list[str]:
    schema = schema or load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(intent), key=str)]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"uso: {argv[0]} <intent.json>", file=sys.stderr)
        return 2

    intent_path = Path(argv[1])
    intent = json.loads(intent_path.read_text())
    errors = validate_intent(intent)

    if errors:
        print(f"INVÁLIDO: {intent_path}")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"VÁLIDO: {intent_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
