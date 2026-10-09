.PHONY: help render validate-schema validate-policy validate-manifests test cluster-up cluster-down argocd-install

KUBECONFIG_PATH := $(HOME)/.kube/intent-lab.yaml
KIND_CONTEXT := kind-intent-lab
OVERLAY := apps/intent-lab/overlays/dev

help:
	@echo "Targets: render, validate-schema, validate-policy, validate-manifests, test, cluster-up, cluster-down, argocd-install"

render:
	kustomize build $(OVERLAY)

validate-manifests: render
	kustomize build $(OVERLAY) | kubeconform -strict -summary

validate-policy: render
	kustomize build $(OVERLAY) | conftest test - -p policies

test:
	.venv/bin/pytest -q

cluster-up:
	kind create cluster --name intent-lab --kubeconfig $(KUBECONFIG_PATH)

cluster-down:
	kind delete cluster --name intent-lab --kubeconfig $(KUBECONFIG_PATH)
