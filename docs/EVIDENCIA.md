# Evidencia

Registro de lo **observado** (ejecutado y verificado) durante las pruebas
de este laboratorio, distinto de lo meramente supuesto o planeado. Cada
entrada indica fecha, comando ejecutado y resultado real.

## FASE 0 — Preflight

- Fecha: 2026-10-09
- Directorio de trabajo vacío y sin repo git previo: confirmado.
- Versiones de herramientas instaladas y verificadas con `--version`:
  kind v0.33.0, kustomize v5.8.3, conftest 0.71.1 (OPA 1.21.1),
  kubeconform v0.8.0, docker 29.0.0 (daemon activo), kubectl v1.37.0
  (client), git 2.34.1, python3 3.10.12, pytest 8.4.1 (en venv local).
- No existía clúster kind `intent-lab` ni kubeconfig
  `~/.kube/intent-lab.yaml` previos: confirmado (`kind get clusters` →
  "No kind clusters found").

## FASE 2 — Clúster y Argo CD

- Fecha: 2026-10-09
- `kind create cluster --name intent-lab --kubeconfig ~/.kube/intent-lab.yaml`:
  clúster creado correctamente.
- Contexto verificado: `kind-intent-lab`. Servidor verificado:
  `https://127.0.0.1:38785` (local, puerto efímero de kind).
- Argo CD `v3.5.4` instalado con
  `kubectl apply --server-side -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.5.4/manifests/install.yaml`
  en el namespace `argocd`.
- Los 7 pods de `argocd` llegaron a `1/1 Running`:
  argocd-application-controller-0, argocd-applicationset-controller,
  argocd-dex-server, argocd-notifications-controller, argocd-redis,
  argocd-repo-server, argocd-server.
- No se leyeron ni imprimieron secretos (ni `argocd-initial-admin-secret`).

## FASE 3 — Contrato, render y políticas

- Fecha: 2026-10-09
- `schemas/intent.schema.json`: vocabulario cerrado a `scale_deployment` y
  `set_image_tag`. 10 pruebas pytest (`tests/test_schema.py`,
  `tests/test_apply_intent.py`) pasan: `10 passed`.
- 2 ejemplos válidos (`intents/examples/valid/`) validan OK con
  `tools/validate_intent.py`; 7 ejemplos inválidos
  (`intents/examples/invalid/`) son rechazados correctamente (vocabulario
  cerrado, namespace fijo, tag `latest` prohibido, límites de réplicas,
  propiedades adicionales, params incorrectos para el intent).
- `kustomize build apps/intent-lab/overlays/dev | kubeconform -strict -summary`:
  `Valid: 2, Invalid: 0, Errors: 0`.
- `kustomize build apps/intent-lab/overlays/dev | conftest test - -p policies`:
  `14 tests, 14 passed, 0 failures`.
- Fixtures deliberadamente inválidas (`tests/fixtures/bad_*.yaml`) son
  rechazadas por las políticas Rego, cada una por el motivo correcto:
  tag `latest`, `resources.limits` ausente, y `kind: Secret` no permitido.
- `tools/apply_intent.py` probado con pytest (sobre copias temporales,
  sin mutar el repo real): traduce intents válidos a cambios deterministas
  de `replicas`/`images.newTag` en el overlay, y rechaza intents inválidos
  sin escribir nada.
- `make validate-manifests`, `make validate-policy` y `make test`:
  ejecutados y verificados, todos en verde.

## Aplicación manual de AppProject/Application

- Fecha: 2026-10-09
- `kubectl apply -f argocd/appproject.yaml` y
  `kubectl apply -f argocd/application.yaml`: ambos recursos creados en
  el namespace `argocd` (`appproject.argoproj.io/intent-lab`,
  `application.argoproj.io/intent-lab`).
- Estado observado: `SYNC STATUS: Unknown`, `HEALTH STATUS: Healthy`,
  con condición `ComparisonError`: *"failed to list refs: authentication
  required: Repository not found"*. Esperado: el repo remoto
  `afloresdatec/intent-layer-lab` todavía no existe en GitHub (no se ha
  hecho push). Pendiente de FASE siguiente, bajo autorización explícita.
