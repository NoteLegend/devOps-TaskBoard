# Deployment

## Local Compose

```bash
docker compose up --build -d --wait
python3 scripts/smoke.py http://localhost:3000
docker compose -f compose.test.yml up --abort-on-container-exit --exit-code-from tests
```

Test Compose uses a separate project and tmpfs database; no application DB is truncated. Normal Compose restart preserves the named application volume.

## Infrastructure checkpoint

```bash
export PATH="$PWD/.tools:$PWD/.venv/bin:$PATH"
export AWS_PROFILE=YOUR_AGREED_PROFILE
aws sts get-caller-identity
aws eks describe-cluster-versions --region ap-south-1
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit the ignored tfvars with the agreed account/operator ARN.
terraform -chdir=terraform init
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
terraform -chdir=terraform plan -out=approved.tfplan
terraform -chdir=terraform show -no-color approved.tfplan
```

A real plan needs authenticated AWS and chosen identity. **Do not apply without user approval of that actual plan, current costs and schedule.** Review VPC/two public and two private subnets, routes/IGW, one NAT/EIP, EKS control plane, two t3.medium workers and root disks, logs/KMS/IAM, EBS CSI/metrics add-ons. Helm later adds a billable ALB and PostgreSQL gp3 disk. Include ALB LCUs, public IPv4, NAT processing, EBS and data transfer in the estimate. See [cost checkpoint](COST_CHECKPOINT.md).

After approval only:

```bash
terraform -chdir=terraform apply approved.tfplan
export AWS_ACCOUNT_ID=YOUR_APPROVED_ACCOUNT
scripts/bootstrap-aws.sh
```

Bootstrap explicitly checks account identity, creates deployment namespace RBAC, waits for EBS/Metrics Server, installs pinned AWS Load Balancer Controller with IRSA, creates gp3, installs monitoring/CRDs, and creates the runtime secret without printing values. The operator needs provisioning privileges; routine CI has only DescribeCluster plus namespace Kubernetes permissions. No cluster-admin CI role.

Verify regional EKS add-on versions selected in the actual plan with `aws eks describe-addon-versions` for 1.35; Terraform resolves compatible builds through AWS and the approved saved plan fixes the selected values. Record them in evidence. Restrict API endpoint CIDRs if using runners with fixed egress; the default allows GitHub-hosted runner IPs but still requires authentication/RBAC.

## Deploy immutable images

First publish scans-passing SHA images, set both GHCR packages public and prove anonymous pulls. Configure Actions variables from [setup](USER_SETUP.md), then enable deploy. Local equivalent:

```bash
scripts/deploy.sh "$(git rev-parse HEAD)"
kubectl get pods,svc,pvc,ingress,hpa -n taskboard
kubectl get endpointslices -n taskboard
kubectl get jobs -n taskboard
kubectl logs -n taskboard job/taskboard-migrate-RELEASE_REVISION
```

Migration hook is post-install/pre-upgrade with bounded retries and PostgreSQL advisory locking. First install creates PostgreSQL before migrations. **Do not add Helm `--wait` or `--atomic` to this chart’s first-install command**: API readiness depends on the post-install migration hook. The deploy helper waits for each rollout after hook completion. Migrations must stay backward compatible while old replicas run on upgrades. Helm rollback does not revert schema; never automatically downgrade a live database.

ALB Ingress has an empty host rule, so its generated AWS hostname works without purchasing a domain. Get it with:

```bash
kubectl get ingress taskboard -n taskboard -o jsonpath='{.status.loadBalancer.ingress[0].hostname}{"\n"}'
python3 scripts/smoke.py http://ACTUAL_ALB_HOSTNAME
```

`/api` routes directly to backend:8000; `/` routes to frontend:8080. Nginx proxies `/docs` and `/openapi.json` to the backend. PostgreSQL remains ClusterIP only. This HTTP classroom demo is not for sensitive data. An authenticated production service would add HTTPS and user authorization.

## Monitoring and scaling

```bash
kubectl get servicemonitor -n taskboard
kubectl top pods -n taskboard
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
# In a second terminal:
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80
```

Prometheus/Grafana remain private ClusterIP. Retrieve the generated Grafana admin password locally from its Kubernetes Secret without recording it; use the authenticated UI at http://localhost:3001. Dashboard config is `monitoring/dashboard.json`. Check Prometheus `/targets` and query `up{namespace="taskboard"}` and `sum(rate(http_requests_total{namespace="taskboard"}[2m]))`. Metrics Server CPU data is separate from Prometheus application metrics.

Before load, verify requests, current CPU and free node capacity. `URL=http://ACTUAL_HOST/api/tasks scripts/hpa-evidence.sh` caps load at 24 workers/180 seconds and HPA at four replicas. Record initial/increased/recovered replicas and CPU; investigate metrics, requests, pending Pods and workload cost if scaling does not occur. Request counts alone do not demonstrate scaling.

## Rollback

```bash
helm history taskboard -n taskboard
helm rollback taskboard PREVIOUS_REVISION -n taskboard --wait --timeout 5m
kubectl rollout status deployment/taskboard-backend -n taskboard --timeout=180s
python3 scripts/smoke.py http://ACTUAL_HOST
```

Rollback uses already-applied backward-compatible schema; restore a DB backup separately if a schema change was destructive. Do not delete PVCs to fix an image/Service problem.

## Local Kubernetes (separate evidence)

```bash
export PATH="$PWD/.tools:$PATH"
kind create cluster --config k8s/kind.yaml --image kindest/node:v1.35.0 --wait 180s
scripts/bootstrap-local.sh
python3 scripts/smoke.py http://localhost:8088
scripts/troubleshooting.sh
```

Local Traefik NodePort reaches kind’s loopback mapping. Only local Metrics Server bypasses self-signed kubelet certificate validation. Local storage uses kind’s default StorageClass; AWS uses EBS gp3. Local checks do not satisfy AWS infrastructure/deployment acceptance criteria.
