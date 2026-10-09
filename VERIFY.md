# Verificación manual end-to-end

Checklist de pasos a ejecutar y observar (no supuestos) para validar el
laboratorio completo. Se completa a medida que se avanzan las fases.

- [x] FASE 2: clúster `kind-intent-lab` creado, contexto y server
      verificados (`https://127.0.0.1:<puerto>`).
- [x] FASE 2: Argo CD instalado en `argocd`, todos los pods `Ready`.
- [x] FASE 3: `schemas/intent.schema.json` rechaza intents fuera del
      vocabulario cerrado (ver `intents/examples/invalid/`).
- [x] FASE 3: render de `apps/intent-lab/overlays/dev` pasa
      `kubeconform -strict` y las políticas `conftest`.
- [x] `argocd/appproject.yaml` y `argocd/application.yaml` aplicados
      manualmente; Argo CD sincroniza `apps/intent-lab/overlays/dev` al
      namespace `intent-lab`.
- [ ] Pipeline de CI corre en un PR de prueba, sin secretos ni acceso a
      clúster, con permisos `contents: read`.
- [ ] Prueba 7 (`kubectl scale`, bajo autorización explícita) demuestra
      selfHeal de Argo CD.

Cada ítem se marca solo tras ejecución y verificación real, documentada
en `docs/EVIDENCIA.md`.
