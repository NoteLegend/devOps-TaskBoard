#!/usr/bin/env bash
set -euo pipefail
NS=taskboard-troubleshooting
mkdir -p evidence/logs
kubectl create namespace "$NS" --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n "$NS" -f troubleshooting/broken-image.yaml
# Wait only within this disposable diagnostic namespace.
for attempt in $(seq 1 24); do
  kubectl get pods -n "$NS" -o jsonpath='{.items[*].status.containerStatuses[*].state.waiting.reason}' | grep -Eq 'ErrImagePull|ImagePullBackOff' && break
  sleep 5
done
kubectl get pods -n "$NS" | tee evidence/logs/broken-image-symptom.txt
kubectl describe pods -n "$NS" > evidence/logs/broken-image-describe.txt
kubectl get events -n "$NS" --sort-by=.lastTimestamp > evidence/logs/broken-image-events.txt
kubectl set image deployment/diagnostic-web web=nginxinc/nginx-unprivileged:stable-alpine -n "$NS"
kubectl rollout status deployment/diagnostic-web -n "$NS" --timeout=180s
kubectl apply -n "$NS" -f troubleshooting/broken-service.yaml
kubectl get pods -n "$NS" --show-labels > evidence/logs/broken-service-labels.txt
kubectl get endpointslices -n "$NS" -l kubernetes.io/service-name=diagnostic-web -o yaml > evidence/logs/broken-service-empty.txt
kubectl patch service diagnostic-web -n "$NS" --type=merge -p '{"spec":{"selector":{"app":"diagnostic-web"}}}'
kubectl get endpointslices -n "$NS" -l kubernetes.io/service-name=diagnostic-web -o yaml > evidence/logs/broken-service-recovered.txt
kubectl run diagnostic-curl -n "$NS" --restart=Never --image=curlimages/curl:8.16.0 --command -- curl --fail --retry 10 --retry-delay 2 http://diagnostic-web:8080
kubectl wait -n "$NS" --for=jsonpath='{.status.phase}'=Succeeded pod/diagnostic-curl --timeout=90s
kubectl logs diagnostic-curl -n "$NS" > evidence/logs/broken-service-http-recovery.txt
# Restore the isolated exercises to working state. Namespace deletion is a separate cleanup step.
