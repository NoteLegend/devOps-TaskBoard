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

# Rollouts alone do not prove external routing. Wait for the actual ALB hostname.
for attempt in $(seq 1 60); do
  HOST=$(kubectl get ingress taskboard -n taskboard -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
  [[ -n "$HOST" ]] && break
  sleep 3
done
[[ -n "$HOST" ]] || { echo 'Ingress hostname was not assigned'; exit 1; }
python3 scripts/wait-ready.py "http://$HOST" --seconds 180
python3 scripts/smoke.py "http://$HOST"
