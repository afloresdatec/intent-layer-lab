# Políticas sobre los manifiestos RENDERIZADOS (salida de `kustomize build`),
# no sobre los intents. Sintaxis OPA 1.0 (if/contains nativos).
package main

disallowed_kinds := {"Secret", "Role", "RoleBinding", "ServiceAccount", "NetworkPolicy"}

allowed_namespace := "intent-lab"

deny contains msg if {
	disallowed_kinds[input.kind]
	msg := sprintf("resource kind %q is not allowed in this application", [input.kind])
}

deny contains msg if {
	input.kind in {"Deployment", "Service"}
	input.metadata.namespace != allowed_namespace
	msg := sprintf("namespace %q is not allowed; only %q is permitted", [input.metadata.namespace, allowed_namespace])
}

deny contains msg if {
	some c in input.spec.template.spec.containers
	endswith(c.image, ":latest")
	msg := sprintf("container %q uses the mutable tag 'latest' (image=%q)", [c.name, c.image])
}

deny contains msg if {
	some c in input.spec.template.spec.containers
	not contains(c.image, ":")
	msg := sprintf("container %q has no explicit image tag (image=%q)", [c.name, c.image])
}

deny contains msg if {
	some c in input.spec.template.spec.containers
	not c.resources.requests
	msg := sprintf("container %q must define resources.requests", [c.name])
}

deny contains msg if {
	some c in input.spec.template.spec.containers
	not c.resources.limits
	msg := sprintf("container %q must define resources.limits", [c.name])
}

deny contains msg if {
	input.kind == "Deployment"
	input.spec.replicas > 10
	msg := sprintf("replicas (%d) exceed the allowed maximum of 10", [input.spec.replicas])
}
