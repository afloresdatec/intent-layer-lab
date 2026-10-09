import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from validate_intent import load_schema, validate_intent  # noqa: E402

VALID_DIR = REPO_ROOT / "intents" / "examples" / "valid"
INVALID_DIR = REPO_ROOT / "intents" / "examples" / "invalid"


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_valid_examples_pass():
    schema = load_schema()
    examples = sorted(VALID_DIR.glob("*.json"))
    assert examples, "no hay ejemplos válidos"
    for path in examples:
        errors = validate_intent(_load(path), schema)
        assert errors == [], f"{path.name} debería ser válido, errores: {errors}"


def test_invalid_examples_fail():
    schema = load_schema()
    examples = sorted(INVALID_DIR.glob("*.json"))
    assert examples, "no hay ejemplos inválidos"
    for path in examples:
        errors = validate_intent(_load(path), schema)
        assert errors != [], f"{path.name} debería ser inválido"


def test_schema_vocabulary_is_closed():
    schema = load_schema()
    assert schema["properties"]["intent"]["enum"] == [
        "scale_deployment",
        "set_image_tag",
    ]
