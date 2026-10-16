#!/usr/bin/env bash
set -euo pipefail
kubectl config use-context kind-taskboard-local
kind load docker-image taskboard-backend:local taskboard-frontend:local --name taskboard-local
kubectl apply -f k8s/namespace.yaml
helm repo add traefik https://traefik.github.io/charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
helm upgrade --install traefik traefik/traefik --version 42.0.0 -n ingress-system --create-namespace \
  --set service.spec.type=NodePort --set ports.web.nodePort=30080 --wait --timeout 5m
helm upgrade --install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system \
  --set 'args[0]=--kubelet-insecure-tls' --wait --timeout 5m
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 92.9.0 \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml --wait --timeout 10m
kubectl wait --for=condition=Established crd/servicemonitors.monitoring.coreos.com --timeout=120s
kubectl create configmap taskboard-dashboard -n monitoring --from-file=taskboard.json=monitoring/dashboard.json --dry-run=client -o yaml | kubectl apply -f -
kubectl label configmap taskboard-dashboard -n monitoring grafana_dashboard=1 --overwrite
python3 scripts/create-runtime-secret.py
helm upgrade --install taskboard helm/taskboard -n taskboard -f helm/taskboard/values-dev.yaml \
  --set ingress.host='' --set monitoring.serviceMonitor.enabled=true --timeout 6m
kubectl rollout status deployment/taskboard-backend -n taskboard --timeout=180s
kubectl rollout status deployment/taskboard-frontend -n taskboard --timeout=180s
kubectl get pods,svc,ingress,hpa,pvc -n taskboard
