#!/usr/bin/env bash
set -euo pipefail
: "${URL:?Set your project URL including /api/tasks}"
mkdir -p evidence/logs
kubectl top nodes
kubectl top pods -n taskboard
kubectl get deployment taskboard-backend -n taskboard -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}{"\n"}'
kubectl get hpa taskboard-backend -n taskboard
python3 scripts/load-test.py "$URL" --seconds 180 --workers 24 > evidence/logs/hpa-load.txt &
LOAD_PID=$!
trap 'kill "$LOAD_PID" 2>/dev/null || true' EXIT
# Collect 3 minutes under load and 3 minutes of recovery; max replicas is four.
for attempt in $(seq 1 36); do
  date -u +%FT%TZ
  kubectl get hpa taskboard-backend -n taskboard
  kubectl top pods -n taskboard --containers
  kubectl get deployment taskboard-backend -n taskboard
  sleep 10
done | tee evidence/logs/hpa-observations.txt
wait "$LOAD_PID"
kubectl describe hpa taskboard-backend -n taskboard > evidence/logs/hpa-describe.txt
