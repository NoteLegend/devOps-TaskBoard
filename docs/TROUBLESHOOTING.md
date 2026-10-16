# Troubleshooting exercises

Run `scripts/troubleshooting.sh` against the intended context. Every mutation uses `-n taskboard-troubleshooting`; main Release Helpdesk is untouched. Actual results are tracked in [verification](VERIFICATION.md) and `evidence/logs/broken-*`. Until those exist, the following describes the procedure, not a completed exercise.

## Wrong image tag

Apply `troubleshooting/broken-image.yaml` in the isolated namespace. Inspect `kubectl get pods -n taskboard-troubleshooting`, `kubectl describe pods -n taskboard-troubleshooting`, and `kubectl get events -n taskboard-troubleshooting --sort-by=.lastTimestamp`. Expected symptom: ErrImagePull/ImagePullBackOff; root cause: intentionally nonexistent Nginx image tag. Fix with `kubectl set image deployment/diagnostic-web web=nginxinc/nginx-unprivileged:stable-alpine -n taskboard-troubleshooting`, then wait for rollout. A missing registry credential can cause the same symptom; events distinguish denied access from missing tags.

## Incorrect Service selector

With diagnostic-web Ready, apply `troubleshooting/broken-service.yaml` in that same namespace. Compare `kubectl get pods -n taskboard-troubleshooting --show-labels` with the Service selector. Inspect EndpointSlices using `kubectl get endpointslices -n taskboard-troubleshooting -l kubernetes.io/service-name=diagnostic-web -o yaml`. Root cause: selector `app: incorrect-label` matches no Pods. Patch it to `app: diagnostic-web`, check populated Ready addresses and port 8080, then run the bounded diagnostic curl Pod and record HTTP recovery.

Leave the isolated resources in recovered state for review; delete only that namespace during authorized local cleanup. On AWS, verify no diagnostic LoadBalancer/PVC was created (the lab uses neither).

## Other observed or likely failures

- Docker socket denied: local user was absent from docker group. User added membership; existing agent shell needed a fresh group (`newgrp docker`). Membership grants administrator-equivalent Docker access.
- Migration hook hangs on first install with `--wait`: API readiness needs the post-install hook. Use the deployment helper’s explicit post-hook rollout checks.
- PVC Pending on AWS: check EBS CSI controller/IRSA, gp3 provisioner, WaitForFirstConsumer and schedulable same-AZ nodes.
- HPA unknown: check Metrics Server/APIService and CPU requests; Prometheus does not supply the HPA CPU resource API.
- Prometheus empty: check Operator CRD, ServiceMonitor label `release: monitoring`, service app label, named `http` port, and `/metrics`.
- Frontend 502: check backend Service endpoints and readiness, then Nginx’s release-specific upstream. Browser calls must stay same-origin.
- GHCR pull denied: verify package visibility or permanent read-only imagePullSecret. GitHub workflow tokens expire.
