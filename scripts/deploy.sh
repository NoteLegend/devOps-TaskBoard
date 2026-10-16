#!/usr/bin/env bash
set -euo pipefail
TAG=${1:?Usage: deploy.sh COMMIT_SHA}
[[ "$TAG" =~ ^[0-9a-f]{40}$ ]] || { echo 'Expected a full immutable Git SHA'; exit 2; }
: "${IMAGE_BASE:=ghcr.io/notelegend/devops-taskboard}"
kubectl get secret taskboard-runtime -n taskboard >/dev/null
# No --wait: on first install it would wait for API readiness before the post-install migration hook.
helm upgrade --install taskboard helm/taskboard -n taskboard -f helm/taskboard/values-prod.yaml \
  --set-string backend.image="$IMAGE_BASE-backend" --set-string frontend.image="$IMAGE_BASE-frontend" \
  --set-string backend.tag="$TAG" --set-string frontend.tag="$TAG" --timeout 6m --history-max 5
kubectl rollout status statefulset/taskboard-postgres -n taskboard --timeout=180s
kubectl rollout status deployment/taskboard-backend -n taskboard --timeout=180s
kubectl rollout status deployment/taskboard-frontend -n taskboard --timeout=180s
kubectl get pods,svc,ingress,hpa,pvc -n taskboard
