# Executed verification

## Current delivery and GitOps verification — 21 October 2026

The same Release Helpdesk application now includes integrated source security, dependency auditing, full-history/working-tree secret gates and a continuously reconciled Flux Helm release. Source directories follow the canonical delivery layout; no separate application has been substituted for missing evidence.

| Check | Actual result | Evidence |
|---|---|---|
| Python source analysis | Bandit: zero findings, no skipped tests / nosec exemptions. | [Bandit](../evidence/logs/security-final/bandit.json) |
| Frontend source analysis | Semgrep: four checked-in rule groups, zero findings; source parsed. | [Semgrep](../evidence/logs/security-final/semgrep.json) |
| Dependency analysis | pip-audit and npm audit: zero known findings after the certifi fix. | [Python](../evidence/logs/security-final/pip-audit.json), [JavaScript](../evidence/logs/security-final/npm-audit.json), [initial advisory](../evidence/logs/security-initial/pip-audit.json) |
| Secret analysis | Gitleaks: no unexcepted findings in full reachable Git history or working text. Exact public CPython signing fingerprint excepted only in explicit archived image-report paths. | [History](../evidence/logs/security-final/gitleaks-history.json), [working tree](../evidence/logs/security-final/gitleaks-working-tree.json), [config](../security/gitleaks.toml) |
| Gate rejection controls | Unsafe Python, unsafe JavaScript and a synthetic fake secret each produced scanner exit code 1. The original vulnerable dependency scan also failed before repair. | [Controls](../evidence/logs/security-final/negative-controls.json), [initial SCA](../evidence/logs/security-initial/) |
| Application regression | 19 unit tests; 19 migrated PostgreSQL integration cases; no migration drift; real browser create/edit/filter/delete/mobile/Swagger. | [Unit](../evidence/logs/final-backend-unit.txt), [PostgreSQL](../evidence/logs/final-postgres-integration.txt), [browser](../evidence/logs/final-browser.txt) |
| Configuration | Docker/Compose builds and smoke, Helm lint/render, GitOps Kustomize, Terraform fmt/validate, actionlint and six account-guard tests passed. | [Config](../evidence/logs/final-configuration.txt), [guard](../evidence/logs/final-deployment-guard.txt), [smoke](../evidence/logs/final-compose-smoke.txt) |
| Hosted source/image delivery | Main commit `1178b684e26c00d06d05b66653d54dd5cebd191b`: tests and integrated security succeeded; both images scanned with zero HIGH/CRITICAL findings and published. AWS deploy skipped because infrastructure remains removed. | [Real run 39583131700](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/39583131700), [run record](../evidence/logs/ci-security-release.json), [source reports](../evidence/logs/ci-final-source/), [image reports](../evidence/logs/ci-final-images/) |
| Flux baseline | The controller fetched public main, installed the actual chart, passed HTTP CRUD and automatically corrected frontend replicas 2 → 1 → 2 in 37.0 seconds without forced reconciliation. | [Baseline summary](../evidence/logs/gitops-baseline/summary.json), source/Helm/event records in that directory. |
| Git-owned release promotion | Commit `871c2848d3dc6cb4076de33f6e7bb82ec23cdd0c` pins the newly scanned `1178b68…` images and changes `gitops-v1` → `gitops-v2`; Flux upgrades the release. Final verification records observed revision, HTTP marker, image identity and repeated automatic drift recovery. | [Final GitOps summary and records](../evidence/logs/gitops-final/), [current Prometheus targets/counters](../evidence/logs/gitops-final/monitoring.json) |
| Deliverable structure | Root directories match application/, docker/, kubernetes/, helm/, terraform/, .github/workflows/, security/, monitoring/ and gitops/. ZIP wraps the tracked source under final-devops-project/ and checks media hashes/exclusions. | [Packager](../scripts/package-submission.py), [traceability](REQUIREMENTS.md) |

The final report-isolation and archived-metadata configuration also passed in [run 39584671289](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/39584671289), with [fresh hosted source reports](../evidence/logs/ci-submission-source/) and [the run record](../evidence/logs/ci-submission-validation.json). The earlier promotion run was correctly blocked by the public signing fingerprint in its newly archived report path; the exception was extended only to that exact path/value, and full history/working-tree scans then passed.

The Starlette/httpx test-client deprecation warning is informational; both test suites passed. Semgrep's checked-in rules cover selected frontend risks; no source scanner proves absence of every vulnerability. All security results are dated observations. Hosted scan reports are separately retained from local reports, and CI writes fresh artifacts into an empty scan-results directory.

GitOps is verified on **local kind**, with runtime credentials generated outside Git, and only frontend replica drift under Git ownership. The HPA owns backend replicas. The recorded AWS/EKS lifecycle below occurred on 16 October; its endpoint remains offline, and this follow-up created no AWS resources. Submitting the verified repository is the remaining student handover action.

## Historical AWS lifecycle — 16 October 2026

The approved AWS run provisioned, served, monitored and removed the real cloud environment. Its original screenshots, failures and successful recovery are retained below. Newer source-security and local GitOps results do not claim a second cloud deployment.

## Identity, source and deployed version

- Repository: https://github.com/NoteLegend/devOps-TaskBoard ; upstream inspected: `a4e39b6b3a54dab1efd386c75ab86bf1d8a23454` (MIT attribution retained).
- Account `835582727900`, operator IAM user `shrival`, profile `Raghavendra Linga`, region `ap-south-1`; Free Tier API reports FREE/ACTIVE with $117.20 credits at initial verification. The local Terraform adapter calls the CLI process credential provider; credential values are never archived.
- Live application commit: **179ad20c5e4995bf458a33531905d6f0e694b580**. [Successful push/test/build/scan/publish/deploy](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/38955563228).
- Live ALB during the demo: http://k8s-taskboar-taskboar-cabb6ffcf1-243133037.ap-south-1.elb.amazonaws.com ; `/docs`, `/api/tasks/stats` and `/metrics` verified through the same origin. This historical endpoint was removed during the authorized cleanup.
- [Actual anonymous GHCR digests and matching Ready Pod image IDs](../evidence/logs/aws-registry-image-verification.json). Both application images use this full SHA, are public, and Pods have no imagePullSecrets.
- [Screenshot/video index](../images/README.md), [capture sources/timestamps/hashes](../images/manifest.json), [requirements](REQUIREMENTS.md).

## Local and CI checks

| Check | Result | Commands / genuine evidence |
|---|---|---|
| Backend unit tests | PASSED: 19 | `cd backend && .venv/bin/pytest -v`; [log](../evidence/logs/backend-tests.txt) |
| Clean PostgreSQL migrations/integration | PASSED: 19 | `docker compose -f compose.test.yml up --abort-on-container-exit --exit-code-from tests`; Alembic upgrade/check; [log](../evidence/logs/postgres-integration.txt) |
| Free Tier guard unit cases | PASSED: 6 | `python3 -m unittest discover -s scripts -p 'test_*.py' -v`; [log](../evidence/logs/free-tier-guard-tests.txt) |
| Frontend production build | PASSED locally and CI | `npm ci && npm run build`; [local](../evidence/logs/frontend-build.txt), [actual CI tests/build extract](../evidence/logs/aws-ci-test-extract.txt) |
| Docker builds / Compose config/startup | PASSED | [Images](../evidence/logs/docker-images.txt), [build](../evidence/logs/compose-build.txt), [status](../evidence/logs/compose-status.txt) |
| Compose browser/API CRUD and persistence | PASSED | [Smoke](../evidence/logs/compose-smoke.txt), [browser](../evidence/logs/browser-check.txt), [restart/table](../evidence/logs/compose-persistence.txt) |
| Isolated database readiness failure/recovery | PASSED | [Real outage](../evidence/logs/readiness-outage.txt): ready 200 → DB stopped/ready 503 while health stays 200 → DB restarted/ready 200 |
| Real main CI gates and OIDC deployment | PASSED | [Run record](../evidence/logs/aws-ci-live-update.json), [pipeline screenshot](../images/aws-ci-successful-deployment.png) |
| PR event without publishing/deploying | PASSED | [Real PR run](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/38956791668), [actual skip states](../evidence/logs/ci-pr-safety.json) |
| App image Trivy HIGH/CRITICAL gate | PASSED: zero at these severities | [Actual CI reports](../evidence/logs/aws-ci-scans/), [summary](../evidence/logs/aws-ci-scan-summary.json), [tests/scans screenshot](../images/aws-tests-and-trivy-results.png) |

The scans cover OS and language packages at HIGH/CRITICAL using Trivy 0.76.0 on the recorded date. Lower severities and future database updates are not claimed clean. The [original failed scan](../evidence/logs/trivy-backend-initial.json) is retained: runtime OS, Starlette constraints and unnecessary pip/ensurepip were repaired without ignore exceptions.

## Actual AWS checks

| Requirement | Result | Commands / genuine evidence |
|---|---|---|
| Explicit account / Free plan / eligible workers and AMI | PASSED | `python3 scripts/check-free-tier.py --account 835582727900`; [eligibility](../evidence/logs/aws-free-tier-eligibility.json), [latest pre-cleanup account guard](../evidence/logs/aws-free-tier-before-cleanup.json) |
| Terraform actual plan/apply | PASSED: 66 added | [Sanitized plan](../evidence/logs/terraform-free-tier-plan-summary.txt), [apply](../evidence/logs/aws-terraform-apply.txt), [Console VPC](../images/aws-vpc-console.png), [Console EKS](../images/aws-eks-active-console.png) |
| EKS managed workers / system add-ons | PASSED | EKS 1.35, two Ready m7i-flex.large AL2023 workers, no node-group health issues; [worker metadata](../evidence/logs/aws-nodegroup.json), [nodes](../evidence/logs/aws-nodes.txt), [apply/Ready screenshot](../images/aws-terraform-apply-and-ready-nodes.png) |
| Controller / gp3 / Metrics Server / monitoring bootstrap | PASSED | `scripts/bootstrap-aws.sh`; [actual transcript](../evidence/logs/aws-bootstrap.txt) |
| Helm migration, replicas, Services and Ingress | PASSED | `kubectl get pods,svc,pvc,ingress,hpa -n taskboard`, `helm list -n taskboard`; [resources](../evidence/logs/aws-kubernetes-resources.txt), [endpoints](../evidence/logs/aws-service-endpoints.txt), [migration](../evidence/logs/aws-migration.txt), [screenshot](../images/aws-kubernetes-helm-ingress.png) |
| Persistent PostgreSQL and schema authority | PASSED | Bound 5-GiB gp3 EBS CSI volume; actual Pod restart changed UID and preserved all four synthetic records; [storage](../evidence/logs/aws-persistent-storage.json), [persistence](../evidence/logs/aws-database-persistence.json), [table/revision screenshot](../images/aws-postgresql-table-and-persistence.png) |
| Browser/API through real ALB | PASSED | [Final browser log](../evidence/logs/aws-browser-final.txt): create/update/filter/delete, mobile, Swagger execution and metrics; [desktop](../images/aws-application-desktop.png), [mobile](../images/aws-application-mobile.png), [Swagger 200](../images/aws-swagger-statistics-executed.png), [actual walkthrough video](../images/aws-browser-walkthrough.webm) |
| Commit → CI → visible deployment update | PASSED | 3ffe809 → 179ad20 application images; [before](../images/aws-live-update-before.png), [after](../images/aws-live-update-after.png), real main-branch run above |
| Actual Prometheus scrape/query and private Grafana | PASSED | [Application targets UP](../evidence/logs/aws-prometheus-targets.json), [query responses](../evidence/logs/aws-prometheus-queries.json), [target screenshot](../images/aws-prometheus-targets-up.png), [authenticated populated dashboard](../images/aws-grafana-live-dashboard.png) |
| CPU HPA increase and recovery | PASSED: Ready replicas 2 → 4 → 2; peak 442% of 100m CPU request; 68,466 successful requests, 0 failures in 180.1 seconds | [Internal bounded test](../evidence/logs/aws-hpa-internal/), [before](../images/aws-hpa-before-load.png), [scaled](../images/aws-hpa-scaled-under-load.png); [automatic recovery](../images/aws-hpa-recovered.png) |
| Isolated image and Service failures/fixes | PASSED | Only namespace taskboard-troubleshooting; [actual logs](../evidence/logs/aws-troubleshooting/), [image failure](../images/aws-broken-image-diagnosis.png), [selector failure](../images/aws-broken-service-diagnosis.png), [HTTP recovery](../images/aws-troubleshooting-recovered.png) |
| Deployment evidence pushed before teardown | PASSED before any deletion | Commit 8439aa3; all 48 images/ files matched the remote GitHub tree; [proof](../evidence/logs/aws-evidence-before-teardown.json) |
| Authorized teardown and residual-cost checks | PASSED: 66 destroyed, project resources absent | [Destroy log](../evidence/logs/aws-terraform-destroy.txt), [actual residual checks](../evidence/logs/aws-cleanup-verification.json), [genuine destroy screenshot](../images/aws-terraform-destroy-complete.png); disabled KMS key pending AWS deletion window |

## Honest failures and limits

- First AWS deploy was rejected by IAM because this new GitHub repository uses immutable OIDC subject IDs. An exact subject/main trust correction changed one IAM policy, then the failed job passed. [Original failure](../evidence/logs/aws-ci-initial-oidc-failure.txt), [fix plan](../evidence/logs/aws-oidc-fix-plan.json). No trust wildcard or static key was introduced.
- Initial ALB hostname propagation briefly failed local DNS lookup; public DNS resolved automatically, and real CI/external smoke passed. An early screenshot harness used the wrong local AWS CLI/Playwright browser revision and an overly strict filter locator; these tool issues were corrected. [Preserved locator failure](../evidence/logs/aws-browser-initial-filter-locator-failure.txt). Application CRUD then passed in a real browser.
- The external 24-worker load completed 3,602 requests with zero failures in 181.2 seconds, but CPU peaked at 38% against a 60% target and stayed at two replicas. [Actual non-scaling result](../evidence/logs/aws-hpa/summary.json). The subsequent isolated in-cluster client removes the external round trip; its CPU is excluded from backend HPA measurements. Production CPU requests/target were not lowered to manufacture scaling.
- The controlled PostgreSQL restart briefly interrupted readiness, which appears as a small real error-rate sample in Grafana. It preserved data and completed before the autoscaling load.
- Local kind evidence remains separately labelled: [local HPA 2 → 4 → 2](../evidence/logs/hpa-summary-local.json), [registry deployment](../evidence/logs/registry-deployment-local.txt), [local monitoring](../evidence/logs/monitoring-check-local.txt). It is not substituted for AWS evidence.
- The browser recording is genuine historical UI evidence. The implementation gaps are closed by the later source-security/GitOps work above; instructor repository submission remains a student action.

## Completed AWS cleanup

**PASSED at 2026-10-16T20:12:57.381709+00:00.** All deployment screenshots/video were pushed and independently checked at commit `8439aa3f1a4d797e48f0d2e279b44f97bf9c7e0c` before deletion ([remote blob-hash proof](../evidence/logs/aws-evidence-before-teardown.json)). The final evidence push also [passed CI with deployment skipped](../evidence/logs/ci-evidence-push-safe.json).

The application/ALB and its target groups were removed while the controller was active. A private synthetic-data export was saved outside git/archive before deleting the 5-GiB retained database disk. The app, monitoring and controller releases were uninstalled, then the reviewed destroy plan completed: **66 Terraform resources destroyed** ([actual transcript](../evidence/logs/aws-terraform-destroy.txt)).

[Actual residual checks](../evidence/logs/aws-cleanup-verification.json) confirm no project EKS cluster, VPC, active workers, Auto Scaling group, ALB/target groups, network interfaces, retained project disks/snapshots, allocated EIP, active NAT, IAM roles/OIDC providers or CloudWatch log group. Terraform state has no remaining resources and `DEPLOY_ENABLED=false`. The historical ALB application URL is shut down. Local Compose/kind data and unrelated EC2 `i-05e7775e28a9a1a1c` remain untouched.

AWS requires a waiting period for KMS deletion. The project key is **disabled / PendingDeletion**, scheduled for **2026-11-16T01:42:25.050000+05:30**. AWS [does not charge for customer-managed keys scheduled for deletion](https://aws.amazon.com/kms/pricing/); see the [mandatory waiting-period documentation](https://docs.aws.amazon.com/kms/latest/cryptographic-details/key-deletion.html). The key is not claimed already physically erased.

The account remains **FREE / ACTIVE**. Credit/billing reports can lag; the final settled debit is not yet known, and the reported balance is not proof of zero usage. No Paid-plan upgrade occurred. Existing unrelated account activity is excluded from this project's cleanup. Review the Billing Console after reports settle without provisioning anything.

Read-only repeat verification (requires authenticated CLI; creates nothing):

```bash
export PATH="$PWD/.tools:$PATH"
export AWS_PROFILE='Raghavendra Linga'
python3 scripts/verify-aws-cleanup.py --account 835582727900
```

Real cleanup screenshots: [destroy completion](../images/aws-terraform-destroy-complete.png), [residual checks](../images/aws-cleanup-residual-checks.png). Future infrastructure recreation requires fresh plan/credit-use/lifetime approval.

Known-pattern Git history secret scan: [PASSED, zero findings across 319 unique text blobs](../evidence/logs/git-history-secret-scan.json). Binary screenshots/video were visually reviewed separately; no detector proves absence of every possible secret.
