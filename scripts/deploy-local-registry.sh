#!/usr/bin/env bash
set -euo pipefail
TAG=${1:?Usage: deploy-local-registry.sh COMMIT_SHA}
[[ "$TAG" =~ ^[0-9a-f]{40}$ ]] || { echo 'Expected a full Git SHA'; exit 2; }
[[ "$(kubectl config current-context)" == kind-taskboard-local ]] || { echo 'Select kind-taskboard-local first'; exit 2; }
BASE=${IMAGE_BASE:-ghcr.io/notelegend/devops-taskboard}
kubectl get secret taskboard-runtime -n taskboard >/dev/null
helm upgrade --install taskboard helm/taskboard -n taskboard -f helm/taskboard/values-dev.yaml \
  --set ingress.host='' --set monitoring.serviceMonitor.enabled=true --set imagePullPolicy=Always \
  --set-string backend.image="$BASE-backend" --set-string frontend.image="$BASE-frontend" \
  --set-string backend.tag="$TAG" --set-string frontend.tag="$TAG" --timeout 6m
kubectl rollout status deployment/taskboard-backend -n taskboard --timeout=180s
kubectl rollout status deployment/taskboard-frontend -n taskboard --timeout=180s
python3 scripts/wait-ready.py http://127.0.0.1:8088
python3 scripts/smoke.py http://127.0.0.1:8088
kubectl get pods -n taskboard -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,IMAGE_ID:.status.containerStatuses[0].imageID
