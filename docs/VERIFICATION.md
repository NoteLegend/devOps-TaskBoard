# Executed verification

Status: **NOT YET SUBMISSION-READY**. Local implementation is verified as listed below. AWS infrastructure, EKS live deployment, public registry pulls, real Actions runs and authorized teardown remain mandatory. No cloud resources were created; no cloud spending or initial Git push is approved yet.

Environment: this Linux machine, 2026-10-16; workspace `/home/rushixd/Wurk/Scaler/DevOps/Final-Project`. Upstream `a4e39b6b3a54dab1efd386c75ab86bf1d8a23454`. Local commits are recorded in [commit history](../evidence/logs/git-history.txt); image IDs are recorded separately. Local image tag `local` is not evidence of a published immutable SHA tag.

| Check | Result | Actual execution / evidence |
|---|---|---|
| Starter README, GRADING and source audit | PASSED | [Audit](STARTER_AUDIT.md), [attribution](ATTRIBUTION.md) |
| Isolated backend unit tests | PASSED | `cd backend && .venv/bin/pytest -v`: 19 passed; [log](../evidence/logs/backend-tests.txt) |
| Clean PostgreSQL migration and schema comparison | PASSED | `docker compose -f compose.test.yml up --abort-on-container-exit --exit-code-from tests`: Alembic upgrade/check, 19 passed; [log](../evidence/logs/postgres-integration.txt) |
| Frontend production build | PASSED | `npm ci`, `npm run build`; [log](../evidence/logs/frontend-build.txt) |
| Compose syntax, images, startup | PASSED | `docker compose config --quiet`, build, `up -d --wait`; [status](../evidence/logs/compose-status.txt), [images](../evidence/logs/docker-images.txt) |
| Same-origin Compose CRUD/statistics | PASSED | `python3 scripts/smoke.py http://localhost:3000`; [log](../evidence/logs/compose-smoke.txt) |
| Browser create/edit/delete/filter/mobile/Swagger | PASSED | [Playwright log](../evidence/logs/browser-check.txt), [desktop](../evidence/application-desktop.png), [mobile](../evidence/application-mobile.png), [Swagger](../evidence/api-docs.png) |
| PostgreSQL normal restart persistence | PASSED | [Actual full-stack restart/table output](../evidence/logs/compose-persistence.txt) |
| Isolated real database outage/recovery | PASSED | [Log](../evidence/logs/readiness-outage.txt): initial 200, DB stopped → ready 503, health 200; DB restart → ready 200 |
| Both final image scans | PASSED for HIGH/CRITICAL gate | [Backend](../evidence/logs/trivy-backend.json), [frontend](../evidence/logs/trivy-frontend.json); zero findings at these severities, unfixed findings not ignored |
| Initial backend security scan | FAILED, remediated | [Original report](../evidence/logs/trivy-backend-initial.json). Debian OS findings, vulnerable constrained Starlette and pip-vendored dependencies; runtime changed to Alpine, compatible Starlette security floor, direct Prometheus middleware and removal of unnecessary runtime pip/ensurepip |
| Terraform initialization/format/validation | PASSED locally | Pinned modules/provider lockfile; [validation](../evidence/logs/terraform-validate.txt). No AWS plan/apply is implied |
| Helm lint/render/server admission | PASSED locally | [Lint](../evidence/logs/helm-lint.txt), [AWS rendering](../evidence/logs/helm-aws-render.yaml), [local API admission](../evidence/logs/helm-admission-local.txt) |
| Local kind Kubernetes / migration / PVC / rollouts | PASSED | [Cluster log](../evidence/logs/kind-create.txt), [resources](../evidence/logs/kubernetes-local.txt), [migration](../evidence/logs/migration-local.txt), [Helm](../evidence/logs/helm-local.txt) |
| Local Ingress CRUD/statistics | PASSED | http://localhost:8088; [smoke](../evidence/logs/ingress-smoke-local.txt) |
| Local Prometheus actual application scrape | PASSED | [Targets](../evidence/logs/prometheus-targets.json), [queries](../evidence/logs/prometheus-queries.json), [screenshot](../evidence/prometheus-targets-local.png) |
| Local authenticated Grafana populated panels | PASSED | [Check](../evidence/logs/monitoring-check-local.txt), [screenshot](../evidence/grafana-dashboard-local.png) |
| Local CPU HPA | RUNNING | Bounded 24-worker/180-second load; initial 2 replicas, observed CPU over target and desired 4. Final Ready count/recovery pending complete observation; [observations](../evidence/logs/hpa-observations.txt) |
| Local broken-image exercise | PASSED | [Symptom](../evidence/logs/broken-image-symptom.txt), [events](../evidence/logs/broken-image-events.txt), [diagnostics](../evidence/logs/broken-image-describe.txt), recovery log |
| Local broken-Service exercise | PASSED | [Empty endpoints](../evidence/logs/broken-service-empty.txt), [labels](../evidence/logs/broken-service-labels.txt), [recovered endpoints](../evidence/logs/broken-service-recovered.txt), [HTTP success](../evidence/logs/broken-service-http-recovery.txt) |
| GitHub identity/destination | PASSED | Authenticated local CLI as NoteLegend; origin https://github.com/NoteLegend/devOps-TaskBoard; initial push awaiting approval |
| Real CI/GHCR publish/anonymous pulling | BLOCKED | Initial push authorization; package visibility verification after publish |
| Actual AWS account/plan/current cost estimate | BLOCKED | Authenticated profile/account/operator ARN not supplied; no placeholder plan used |
| AWS Terraform apply/EKS/ALB/PVC/metrics/HPA | NOT RUN | Spending approval only after actual plan/cost/schedule; local kind is not AWS evidence |
| AWS teardown/residual costs | NOT RUN | No AWS creation; eventual teardown needs saved evidence and authorization |

Final scan scope: OS and language packages at HIGH/CRITICAL severity using Trivy 0.76.0 and its downloaded database on this date. Zero findings at these severities is not a claim that all severities or future vulnerabilities are absent. The original report includes, for example, a setuptools path traversal advisory; setuptools was reported from pip’s bundled SBOM, so unused packaging tools were removed from the runtime rather than suppressing the finding. No `.trivyignore` exceptions were added.

Observed/repaired local issues: Docker group refresh required; IPv6 localhost healthcheck corrected to IPv4; Traefik chart 42 uses `service.spec.type` rather than the previous values layout; disposable readiness DB needed persistent storage across stop/start rather than tmpfs; browser checks were scoped to their own synthetic ticket when demo data introduced multiple matching rows. Initial rollout metrics may be temporarily unknown until Metrics Server has a sample.

Verified local URLs: [Compose app](http://localhost:3000), [Swagger](http://localhost:8000/docs), [local Ingress](http://localhost:8088), [Prometheus private forward](http://localhost:9090/targets), [Grafana private forward](http://localhost:3001). Forward URLs work only while their local processes run. No AWS application, successful Actions run or registry package URL has yet been verified.
