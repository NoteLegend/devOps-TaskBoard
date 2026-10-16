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

## Actual AWS exercises (2026-10-16 UTC)

Both ran on `arn:aws:eks:ap-south-1:835582727900:cluster/taskboard-eks`, only in namespace `taskboard-troubleshooting`. The original local transcripts remain separate.

The nonexistent `nginxinc/nginx-unprivileged:this-tag-does-not-exist` image produced ErrImagePull/ImagePullBackOff with a registry NotFound error. `kubectl describe pods -n taskboard-troubleshooting` and namespace events identified the missing tag. `kubectl set image deployment/diagnostic-web web=nginxinc/nginx-unprivileged:stable-alpine -n taskboard-troubleshooting` restored a Ready Pod. [Actual symptom/diagnosis](../images/aws-broken-image-diagnosis.png), [events](../evidence/logs/aws-troubleshooting/broken-image-events.txt).

The Service selector `app: incorrect-label` did not match the Pod's `app: diagnostic-web`; EndpointSlices had no endpoints and the isolated curl Pod failed to connect. `kubectl patch service diagnostic-web -n taskboard-troubleshooting --type=merge -p '{"spec":{"selector":{"app":"diagnostic-web"}}}'` restored endpoints. The subsequent curl Pod succeeded and returned the real Nginx page. [Actual failure](../images/aws-broken-service-diagnosis.png), [recovery](../images/aws-troubleshooting-recovered.png), [HTTP output](../evidence/logs/aws-troubleshooting/broken-service-http-recovery.txt). The expected failed curl probe was removed after saving evidence.

The first real CI deployment also exposed GitHub's immutable OIDC subject format, introduced for new repositories in 2026. AWS correctly rejected the legacy names-only subject. The fix uses the exact API `sub_claim_prefix`, including owner/repository IDs, and an exact main-branch suffix. No trust wildcard or static AWS key was added. [Initial failure](../evidence/logs/aws-ci-initial-oidc-failure.txt), [one-policy fix plan](../evidence/logs/aws-oidc-fix-plan.json), [successful run](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/38948125152).
