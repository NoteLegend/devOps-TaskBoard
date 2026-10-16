#!/usr/bin/env bash
set -euo pipefail
: "${AWS_PROFILE:?Select the agreed authenticated AWS profile}"
: "${AWS_ACCOUNT_ID:?Set the agreed account ID}"
ACTUAL=$(aws sts get-caller-identity --query Account --output text)
[[ "$ACTUAL" == "$AWS_ACCOUNT_ID" ]] || { echo 'Wrong AWS account'; exit 1; }
REGION=$(terraform -chdir=terraform output -raw aws_region)
CLUSTER=$(terraform -chdir=terraform output -raw cluster_name)
VPC=$(terraform -chdir=terraform output -raw vpc_id)
ROLE=$(terraform -chdir=terraform output -raw alb_role_arn)
aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER"
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployer-rbac.yaml
kubectl rollout status deployment/ebs-csi-controller -n kube-system --timeout=180s
kubectl rollout status deployment/metrics-server -n kube-system --timeout=180s
kubectl apply -f k8s/gp3.yaml
helm repo add eks https://aws.github.io/eks-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller --version 3.6.0 -n kube-system \
  --set clusterName="$CLUSTER" --set region="$REGION" --set vpcId="$VPC" \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set-string serviceAccount.annotations.'eks\.amazonaws\.com/role-arn'="$ROLE" --wait --timeout 5m
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 92.9.0 \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml --wait --timeout 10m
kubectl wait --for=condition=Established crd/servicemonitors.monitoring.coreos.com --timeout=120s
kubectl create configmap taskboard-dashboard -n monitoring --from-file=taskboard.json=monitoring/dashboard.json --dry-run=client -o yaml | kubectl apply -f -
kubectl label configmap taskboard-dashboard -n monitoring grafana_dashboard=1 --overwrite
python3 scripts/create-runtime-secret.py
kubectl top nodes
