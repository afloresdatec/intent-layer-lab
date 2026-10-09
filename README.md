# intent-layer-lab

Laboratorio local y desechable que prueba de punta a punta el patrón
**intent-layer + GitOps** con Argo CD: un asistente de IA propone cambios
mediante un "intent" estructurado y **nunca** tiene permisos de escritura
sobre el clúster. La IA decide **qué**; un ejecutor determinista (CI +
políticas + aprobación humana + Argo CD) decide **si** y **cómo**.

## Idea general

1. Un intent estructurado (JSON validado contra `schemas/intent.schema.json`)
   describe un cambio deseado, limitado a un vocabulario cerrado
   (`scale_deployment`, `set_image_tag`).
2. El intent se traduce de forma determinista a un cambio sobre
   `apps/intent-lab/overlays/dev` (no hay generación libre de YAML).
3. Un Pull Request expone ese cambio. El CI valida el intent contra el
   schema, renderiza los manifiestos con `kustomize`, y los valida con
   `kubeconform` (esquema) y `conftest`/OPA (políticas). El CI no tiene
   credenciales de clúster.
4. Un humano revisa y aprueba/mergea el PR.
5. Argo CD, ya apuntando a este repositorio, sincroniza el estado deseado
   al clúster. Argo CD es el único componente con permisos de escritura
   sobre el clúster, y solo sobre el namespace `intent-lab`.

## Componentes

- `apps/intent-lab/`: manifiestos base + overlay `dev` (Kustomize).
- `argocd/`: `AppProject` y `Application` de Argo CD (se aplican
  manualmente; no desde el CI ni desde una IA).
- `schemas/`: contrato JSON Schema de los intents.
- `intents/`: ejemplos de intents válidos/inválidos y los propuestos.
- `policies/`: políticas Rego (OPA/conftest) sobre los manifiestos renderizados.
- `tools/`: utilidades para validar/traducir intents.
- `tests/`: pruebas automatizadas (pytest).

## Clúster y versiones fijadas

Clúster Kubernetes local desechable (`kind`), con kubeconfig dedicado en
`~/.kube/intent-lab.yaml` y contexto `kind-intent-lab` (nunca el kubeconfig
por defecto).

| Componente   | Versión  |
|--------------|----------|
| kind         | v0.33.0  |
| kustomize    | v5.8.3   |
| conftest/OPA | v0.71.1 (OPA 1.21.1, sintaxis OPA 1.0) |
| kubeconform  | v0.8.0   |
| Argo CD      | v3.5.4   |

Argo CD se instala desde el manifiesto oficial de esa versión exacta
(nunca `stable`), aplicado con `kubectl apply --server-side` en el
namespace `argocd`.

## Cómo correrlo

Ver `Makefile` para los targets de render/validación/pruebas, y
`VERIFY.md` para los pasos de verificación manual end-to-end.

## Fuera de alcance / garantías de seguridad

- Ningún componente de IA tiene credenciales de clúster ni de Git con
  permiso de merge/push a `main`.
- El workflow de CI no usa secretos, no accede a ningún clúster, corre con
  permisos mínimos (`contents: read`) y se dispara solo con `pull_request`.
- El `AppProject` de Argo CD restringe destino (un solo namespace),
  recursos de clúster (únicamente `Namespace`, imprescindible para que
  Argo CD pueda crear el namespace `intent-lab` vía `CreateNamespace=true`)
  y tipos de recursos namespaced sensibles
  (`Secret`, `Role`, `RoleBinding`, `ServiceAccount`, `NetworkPolicy`).
