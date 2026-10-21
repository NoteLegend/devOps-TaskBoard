# Local verification walkthrough

Use these optional commands to inspect the implemented system and its recorded evidence. The submission requirements are mapped in [REQUIREMENTS.md](REQUIREMENTS.md).

## Prepare

```bash
export PATH="$PWD/.tools:$PATH"
docker compose up --build -d --wait
python3 scripts/smoke.py http://localhost:3000
# Optional Flux-managed view; keep this terminal open.
kubectl --context kind-taskboard-local port-forward -n release-helpdesk-gitops svc/release-helpdesk-frontend 8099:8080
```

Open localhost:3000 (Compose) or localhost:8099 (GitOps), the successful Actions run, both GHCR package pages and the original `images/` files. The old AWS application URL is offline after the recorded teardown. Do not rerun cloud provisioning or cloud load tests for this verification.

## Show the system

| Segment | Demonstration |
|---|---|
| Product | Create a synthetic release ticket, assign priority/owner, edit its status, filter/search and delete it. Show responsive UI evidence. |
| API / database | Use `/docs` for CRUD/statistics. Show the recorded PostgreSQL table, Alembic revision and restart-persistence proof. |
| Containers | Explain Node → Nginx multi-stage build, both non-root users and database → migration → API readiness. |
| CI / security | Open real Actions jobs and report artifacts. Explain Bandit, Semgrep, pip-audit, npm audit, Gitleaks and both Trivy gates. Show the certifi finding and the repaired version. |
| Artifact identity | Show full SHA tags in GHCR and the same SHA pinned in GitOps desired state. |
| Terraform / Kubernetes | Show infrastructure code and original plan/VPC/EKS screens; explain chart values, Services, ConfigMap, runtime Secret, PVC, probes and Ingress. |
| GitOps | Show Flux source revision/Ready status, the committed release marker/image promotion, and the before/drift/recovered records. The controller—not a manual apply—restored frontend replicas. |
| Scaling / monitoring | Show HPA 2 → 4 → 2, actual CPU/load measurements, `/metrics`, Prometheus UP and populated Grafana. |
| Troubleshooting | Explain invalid image and mismatched selector: symptom, resource/log evidence, cause, correction and successful response. |
| Lifecycle | Show preserved evidence, actual destroy completion and residual-resource checks. |

## Optional live drift exercise

```bash
python3 scripts/verify-gitops.py --expect-marker gitops-v2 --output .tools/demo-gitops-check
flux get all -A
```

This deliberately changes frontend replicas in the isolated local GitOps namespace and waits for Flux to restore them without a forced reconcile. It also verifies HTTP CRUD and the release marker. The saved result retains the observed controller revision and recovery timing.

## Finish

Explain lessons learned: verify behavior after rollout, separate readiness from liveness, measure ready replicas for autoscaling, tie reports to revisions and let GitOps correct drift. Submit the repository and checked source/evidence requested by the course PDF. `docker compose down` stops the local application while retaining its database volume.
