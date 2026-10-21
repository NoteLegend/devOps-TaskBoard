#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
context=${1:-kind-taskboard-local}
[[ "$context" == kind-* ]] || { echo 'This bootstrap is for a local kind cluster.' >&2; exit 2; }
[[ "$(kubectl config current-context)" == "$context" ]] || { echo "Select $context explicitly first." >&2; exit 2; }
flux check --pre
flux install --version=v2.9.6 --components=source-controller,kustomize-controller,helm-controller
kubectl apply -f gitops/releases/namespace.yaml
if ! kubectl get secret taskboard-runtime -n release-helpdesk-gitops >/dev/null 2>&1; then
  python3 scripts/create-runtime-secret.py --namespace release-helpdesk-gitops --release release-helpdesk
fi
kubectl apply -f gitops/clusters/local/source.yaml
kubectl wait gitrepository/release-helpdesk -n flux-system --for=condition=Ready --timeout=180s
kubectl wait helmrelease/release-helpdesk -n release-helpdesk-gitops --for=condition=Ready --timeout=420s
kubectl rollout status deployment/release-helpdesk-backend -n release-helpdesk-gitops --timeout=180s
kubectl rollout status deployment/release-helpdesk-frontend -n release-helpdesk-gitops --timeout=180s
flux get all -A
