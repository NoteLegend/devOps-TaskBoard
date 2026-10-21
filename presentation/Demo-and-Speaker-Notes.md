# Release Helpdesk — recording and presenter guide

Suggested length: **12–15 minutes**, including short screen demonstrations. The deck has 16 presentation slides. PowerPoint contains the same speaker notes.

**Verified scope:** current source/security delivery and local Flux promotion/drift correction complement the preserved AWS lifecycle. Cloud screens are historical, and the cloud endpoint is offline. The only remaining delivery actions are your narrated recording and instructor submission.

## Recording setup

- Open `Release-Helpdesk-Presentation.pptx` in PowerPoint or LibreOffice Impress. It can also be imported into Google Slides with **File → Import slides → Upload**. A matching PDF is included for a consistent viewing copy.
- Record your voice and screen at 1080p. Keep the slide or evidence window readable; pause briefly when switching windows.
- Clearly say that the AWS deployment evidence was captured on **16 October 2026**, then the environment was removed after verification. Show the preserved AWS evidence and demonstrate the application locally. The old AWS URL is offline.
- For a local app demo, run `docker compose up --build -d --wait` from the repository root. Open `http://localhost:3000` and `http://localhost:8000/docs`. Use synthetic tickets. Stop with `docker compose down` to retain the volume.
- Open the public repository, successful AWS Actions run, GHCR package pages, and the `images/` folder before recording. Do not rerun Terraform, AWS load tests, or cloud troubleshooting for this presentation.
- Hide credentials and unrelated private windows. The existing `images/aws-browser-walkthrough.webm` is a real browser recording, but it does not include your narration or cover the full capstone.

## Suggested timing and screen changes

| Segment | Slides | Time | Show during the recording |
|---|---|---|---|
| Introduction and product | 1–2 | 1:30 | Create/edit/filter/delete a local ticket; briefly show mobile evidence. |
| Architecture, API and data | 3–4 | 1:45 | Swagger CRUD, statistics route and saved PostgreSQL table/persistence screenshot. |
| Containers and CI/CD | 5–6 | 1:45 | Compose images/users, Git history, Actions jobs and both GHCR SHA tags. |
| Security and infrastructure | 7–8 | 1:30 | Trivy reports, Terraform source/plan and saved AWS EKS/VPC screens. |
| Kubernetes, GitOps and rollout | 9–11 | 2:00 | Helm resources, actual Flux promotion/drift correction, registry identity and historical AWS update. |
| Scaling and monitoring | 12–13 | 1:45 | HPA before/scaled/recovered evidence, metrics, Prometheus UP and Grafana. |
| Troubleshooting and cleanup | 14–15 | 1:30 | Both failure symptoms and recovery, then completed destroy. |
| Outcomes | 16 | 0:30 | Summarize results, engineering lessons and the production roadmap. |

The timings are flexible, not an assignment-imposed limit. Keep screen demonstrations short and explain what the evidence proves. The instructor decides whether preserved cloud evidence satisfies a live-demo request; this guide follows the assignment’s recorded-walkthrough option and the documented approved AWS shutdown.

## Evidence to open at readable size

### Slide 01 — Release Helpdesk

This project is Release Helpdesk, a service desk for deployment incidents, access requests and release follow-ups. I will show how a change moves from Git through tested and scanned container images into a monitored AWS EKS deployment. The AWS screenshots and measurements were captured on 16 October 2026. The cloud environment was then deliberately torn down after its evidence was preserved; the local stack remains reproducible.

Evidence:

- [images/aws-application-desktop.png](../images/aws-application-desktop.png)
- [README.md](../README.md)
- [docs/VERIFICATION.md](../docs/VERIFICATION.md)

### Slide 02 — A focused desk for release operations.

The original application domain is a release helpdesk. Tickets represent deployment incidents and operational requests. In the demo I create a ticket called Release rollback approval, assign Demo Student, select HIGH priority, and move it from TODO to IN_PROGRESS. I then filter the queue, show updated counts, edit and delete the ticket. The frontend has mobile, loading, empty and error states. Its activity feed is explicitly limited to the current browser session. The original TaskBoard API and field names are retained for compatibility. This is a classroom application using synthetic data, without end-user authentication. Show the supplied browser walkthrough or demonstrate the same flow locally.

Evidence:

- [images/README.md](../images/README.md)
- [images/aws-application-desktop.png](../images/aws-application-desktop.png)
- [images/aws-application-mobile.png](../images/aws-application-mobile.png)
- [images/aws-browser-walkthrough.webm](../images/aws-browser-walkthrough.webm)
- [application/frontend/src/main.jsx](../application/frontend/src/main.jsx)
- [docs/ATTRIBUTION.md](../docs/ATTRIBUTION.md)

### Slide 03 — One system. Three connected paths.

Read the architecture as three paths. For requests, the AWS Load Balancer Controller implements the ALB Ingress: slash goes to React served by Nginx, and slash api goes to the FastAPI ClusterIP Service. Nginx also proxies API documentation to the backend. The API stores tickets in PostgreSQL on a persistent EBS volume. For delivery, GitHub Actions tests and scans source/dependencies/secrets, then builds and scans both images before publishing their full-SHA tags. Current GitOps promotion pins that verified SHA in Git and Flux reconciles the Helm release locally. The earlier cloud delivery used a short-lived AWS OIDC role and Helm. Terraform creates the VPC, EKS and IAM infrastructure before this application delivery flow. For observability, Prometheus scrapes the FastAPI metrics endpoint through a ServiceMonitor and Grafana visualizes those measurements. Arrows indicate logical flows; Terraform bootstrap and Alembic migration are explained on later slides.

Evidence:

- [README.md](../README.md)
- [helm/taskboard/templates/ingress.yaml](../helm/taskboard/templates/ingress.yaml)
- [application/frontend/nginx.conf](../application/frontend/nginx.conf)
- [.github/workflows/ci-cd.yml](../.github/workflows/ci-cd.yml)
- [monitoring/prometheus-values.yaml](../monitoring/prometheus-values.yaml)

### Slide 04 — Correctness starts before deployment.

The backend implements six business REST operations, including list, detail, statistics and full create, update, delete behavior. Nineteen parametrized API cases cover CRUD, statistics, validation, missing records, documentation, metrics and database failure recovery. Unit tests default to isolated in-memory SQLite. CI and the integration runner use a separate PostgreSQL database that is migrated before tests run. The test suite does not silently create a PostgreSQL schema. Alembic is the deployment schema authority. Readiness checks the database and tasks table, while liveness checks the process. In an isolated real outage, ready changed from 200 to 503 and back to 200 while health stayed 200. Separately, the AWS PostgreSQL Pod restart changed the Pod UID while all four synthetic records remained on its PVC. Show Swagger CRUD and the saved PostgreSQL table screenshot while explaining this slide.

Evidence:

- [docs/VERIFICATION.md](../docs/VERIFICATION.md)
- [application/backend/tests/test_api.py](../application/backend/tests/test_api.py)
- [application/backend/tests/conftest.py](../application/backend/tests/conftest.py)
- [images/aws-postgresql-pytest-passed.png](../images/aws-postgresql-pytest-passed.png)
- [images/aws-postgresql-table-and-persistence.png](../images/aws-postgresql-table-and-persistence.png)
- [evidence/logs/readiness-outage.txt](../evidence/logs/readiness-outage.txt)
- [evidence/logs/aws-database-persistence.json](../evidence/logs/aws-database-persistence.json)

### Slide 05 — The complete stack starts with one command.

The full local stack runs using docker compose up with build and wait. Dependencies are explicit: PostgreSQL must be healthy, the migration must complete, the API must be ready, and then the frontend starts. The backend runs as UID 10001. The frontend uses a Node build stage and copies only static output into unprivileged Nginx running as UID 101 on port 8080. Local host ports are loopback-bound: the UI is on localhost 3000 and the API documentation is on localhost 8000 slash docs. PostgreSQL is not published to a host port. A named database volume keeps data across normal restarts. Show the saved real Compose image and user screenshot, then open the local application if demonstrating live.

Evidence:

- [images/local-compose-images-and-users.png](../images/local-compose-images-and-users.png)
- [docker-compose.yml](../docker-compose.yml)
- [docker/backend.Dockerfile](../docker/backend.Dockerfile)
- [docker/frontend.Dockerfile](../docker/frontend.Dockerfile)
- [evidence/logs/compose-persistence.txt](../evidence/logs/compose-persistence.txt)

### Slide 06 — A guarded path from commit to cluster.

The current GitHub Actions workflow validates tests and security independently, then requires both jobs before building and publishing images. The security job runs Bandit, Semgrep, pip-audit, npm audit and Gitleaks over full history plus working text. It writes fresh report artifacts for that execution. Tests use a clean migrated PostgreSQL service and also check the frontend, Compose, Helm, GitOps manifests, Terraform and the account guard. Both final images pass the Trivy HIGH/CRITICAL gate before the exact scanned images are pushed with the full source SHA. Pull requests cannot log in to the registry, publish or obtain AWS deployment credentials. The historical OIDC cloud release was verified separately. Current promotion changes the Git-owned HelmRelease to a tested image SHA, and Flux performs the rollout. The screenshot is run 39583131700 for image-source commit 1178b68; later evidence/documentation commits do not change the deployed image source.

Evidence:

- [https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/39583131700](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/39583131700)
- [images/final/ci-security-release.png](../images/final/ci-security-release.png)
- [.github/workflows/ci-cd.yml](../.github/workflows/ci-cd.yml)
- [evidence/logs/ci-security-release.json](../evidence/logs/ci-security-release.json)
- [evidence/logs/ci-final-source](../evidence/logs/ci-final-source)
- [evidence/logs/ci-final-images](../evidence/logs/ci-final-images)
- [gitops/releases/release.yaml](../gitops/releases/release.yaml)

### Slide 07 — Security findings lead to repairs, then a release.

The refreshed scans cover four layers. Bandit checks Python source and migrations; checked-in Semgrep rules check selected dangerous frontend patterns. pip-audit checks the complete pinned Python dependency set, while npm audit includes the frontend build/development graph. Gitleaks scans full reachable Git history and working text with redacted reports. Trivy checks OS and language packages in both final images and fails all HIGH/CRITICAL findings, including unfixed findings. The new dependency audit found the certifi trust-store advisory published after the earlier cloud run. The dependency was upgraded to 2026.10.19 and the images rebuilt. Both new images reported zero HIGH/CRITICAL findings at the recorded scan. Exact public CPython signing fingerprints in archived Trivy metadata have a narrow path/value exception; application secrets are not excluded. Synthetic unsafe Python, unsafe JavaScript and a fake secret each triggered a failed gate. These are dated results and do not claim immunity to future advisories or all application weaknesses.

Evidence:

- [https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/39583131700](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/39583131700)
- [security/README.md](../security/README.md)
- [security/gitleaks.toml](../security/gitleaks.toml)
- [evidence/logs/security-final/summary.json](../evidence/logs/security-final/summary.json)
- [evidence/logs/security-final/negative-controls.json](../evidence/logs/security-final/negative-controls.json)
- [evidence/logs/security-initial/pip-audit.json](../evidence/logs/security-initial/pip-audit.json)
- [evidence/logs/ci-final-images](../evidence/logs/ci-final-images)

### Slide 08 — AWS infrastructure is declared in Terraform.

Terraform provisioned the real AWS environment in ap-south-1. The network spans two availability zones with two public and two private subnets. The ALB uses the public subnets; managed workers use the private subnets. A single NAT gateway supports private egress as a classroom cost tradeoff, rather than claiming full zonal resilience. The EKS cluster used Kubernetes 1.35 and two eligible m7i-flex.large AL2023 workers. Terraform also configures IAM roles, OIDC, EBS CSI and cluster add-ons. The recorded apply created sixty-six Terraform resources. Versions and provider locks are retained. The approved run used account credits under the active Free plan; it did not upgrade the account. Show the saved actual Terraform plan and AWS VPC/EKS Console screenshots. Infrastructure is now removed, and recreation needs a newly approved plan and budget.

Evidence:

- [docs/VERIFICATION.md](../docs/VERIFICATION.md)
- [terraform/main.tf](../terraform/main.tf)
- [terraform/variables.tf](../terraform/variables.tf)
- [terraform/.terraform.lock.hcl](../terraform/.terraform.lock.hcl)
- [terraform/terraform.tfvars.example](../terraform/terraform.tfvars.example)
- [images/aws-terraform-plan.png](../images/aws-terraform-plan.png)
- [images/aws-vpc-console.png](../images/aws-vpc-console.png)
- [images/aws-eks-active-console.png](../images/aws-eks-active-console.png)
- [images/aws-terraform-apply-and-ready-nodes.png](../images/aws-terraform-apply-and-ready-nodes.png)

### Slide 09 — Helm turns the stack into a repeatable release.

The Helm chart deploys into the taskboard namespace. The frontend has two replicas, and the backend HPA maintains at least two replicas. Both Services use ClusterIP networking. The Ingress routes slash to frontend port 8080 and slash api to backend port 8000 through the actual ALB controller. PostgreSQL runs as a StatefulSet with a bound five-GiB encrypted gp3 volume provisioned through EBS CSI. A single migration hook Job runs the Alembic upgrade under a PostgreSQL advisory lock; it is not run concurrently in every API replica. On first install the hook runs after the database resources exist, and on upgrades it runs before the update. The deployment script explicitly checks StatefulSet and Deployment rollouts, then performs external readiness and CRUD checks. Explain Helm values, release history and rollback, noting that destructive database changes would require a compatible migration strategy.

Evidence:

- [images/aws-kubernetes-helm-ingress.png](../images/aws-kubernetes-helm-ingress.png)
- [helm/taskboard/Chart.yaml](../helm/taskboard/Chart.yaml)
- [helm/taskboard/values.yaml](../helm/taskboard/values.yaml)
- [helm/taskboard/values-prod.yaml](../helm/taskboard/values-prod.yaml)
- [helm/taskboard/templates/migrate.yaml](../helm/taskboard/templates/migrate.yaml)
- [application/backend/app/migrate.py](../application/backend/app/migrate.py)
- [scripts/deploy.sh](../scripts/deploy.sh)
- [evidence/logs/aws-persistent-storage.json](../evidence/logs/aws-persistent-storage.json)

### Slide 10 — Committed intent keeps the running service honest.

Flux source-controller fetches this public repository. A Kustomization applies the Git-owned HelmRelease, and helm-controller installs or upgrades the same application chart. The baseline served gitops-v1. Commit 871c284 pinned both newly scanned 1178b68 image tags and changed the release marker to gitops-v2. The Nginx configuration checksum triggered a real frontend rollout, and HTTP exposed the new header. The verification then changed frontend replicas from two to one and observed Flux restore two in 34 seconds, without a forced reconcile, manual Helm upgrade or apply as the repair. The baseline exercise had independently recovered in 37 seconds. Backend replicas remain HPA-owned. The running image IDs were checked against public GHCR manifest digests and matched for both components. This GitOps verification is local kind; the earlier AWS environment remains deliberately removed.

Evidence:

- [evidence/logs/gitops-final/summary.json](../evidence/logs/gitops-final/summary.json)
- [images/final/gitops-verification.png](../images/final/gitops-verification.png)
- [gitops/README.md](../gitops/README.md)
- [gitops/releases/release.yaml](../gitops/releases/release.yaml)
- [evidence/logs/gitops-baseline/summary.json](../evidence/logs/gitops-baseline/summary.json)
- [evidence/logs/gitops-final/image-identity.json](../evidence/logs/gitops-final/image-identity.json)

### Slide 11 — One small change proves the delivery chain.

This is the end-to-end release proof required by the presentation rubric. The before screenshot comes from the previous deployed application commit 3ffe809. Commit 179ad20 clarified the visible help text to: Assign an owner, set a priority, and move release tickets through resolution. The linked real GitHub Actions run passed all three jobs and deployed that full SHA. Registry and Kubernetes inspection verified the deployed tags and digests. The after screenshot shows the new text through the AWS ALB. During the recording, open the commit, the successful run and these two original images at readable zoom. These are preserved screens from the actual release; the AWS endpoint has since been torn down. A current push still runs CI, but deployment is intentionally disabled after cleanup.

Evidence:

- [https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/38955563228](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/38955563228)
- [images/aws-live-update-before.png](../images/aws-live-update-before.png)
- [images/aws-live-update-after.png](../images/aws-live-update-after.png)
- [evidence/logs/aws-registry-image-verification.json](../evidence/logs/aws-registry-image-verification.json)
- [https://github.com/NoteLegend/devOps-TaskBoard/commit/179ad20c5e4995bf458a33531905d6f0e694b580](https://github.com/NoteLegend/devOps-TaskBoard/commit/179ad20c5e4995bf458a33531905d6f0e694b580)

### Slide 12 — CPU demand produced real scaling and recovery.

This chart is derived from the actual saved AWS HPA observations. It plots ready backend replicas rather than merely desired replicas, so it proves usable capacity increased. A bounded in-cluster load ran twenty-four workers for 180.1 seconds, completing 68,466 requests with zero load-client failures. Ready replicas moved from two to four and later recovered automatically to two. The HPA target stayed at sixty percent of the existing 100-millicore CPU request, and observed CPU peaked at 442 percent of that request. That percentage is relative to the resource request, not percent of an entire worker node. An earlier external load completed without errors but did not generate enough backend CPU to scale; that honest non-scaling result is retained. The follow-up client ran in an isolated namespace, and its CPU was excluded from the backend HPA. These are observations of this specific test, not a general throughput or production-capacity guarantee.

Evidence:

- [evidence/logs/aws-hpa-internal/frames.json](../evidence/logs/aws-hpa-internal/frames.json)
- [evidence/logs/aws-hpa-internal/summary.json](../evidence/logs/aws-hpa-internal/summary.json)
- [evidence/logs/aws-hpa/summary.json](../evidence/logs/aws-hpa/summary.json)
- [images/aws-hpa-before-load.png](../images/aws-hpa-before-load.png)
- [images/aws-hpa-scaled-under-load.png](../images/aws-hpa-scaled-under-load.png)
- [images/aws-hpa-recovered.png](../images/aws-hpa-recovered.png)
- [helm/taskboard/templates/hpa.yaml](../helm/taskboard/templates/hpa.yaml)

### Slide 13 — See traffic, latency and errors in one place.

The API exposes an actual HTTP request counter and a response-latency histogram at slash metrics. Handler labels use route templates, which avoids unbounded labels for every ticket ID. A ServiceMonitor selects the backend Service and named HTTP port, and Prometheus was verified scraping the application targets as UP. The screenshot is the real authenticated Grafana dashboard from the AWS run, with populated request rate, error rate, p95 latency and ready replica panels. Grafana stays a private ClusterIP Service and is accessed by authenticated port-forward. The small real error-rate sample includes the controlled PostgreSQL readiness interruption. Show the original metrics endpoint screenshot and Prometheus targets before opening this dashboard at full size.

Evidence:

- [images/aws-grafana-live-dashboard.png](../images/aws-grafana-live-dashboard.png)
- [application/backend/app/main.py](../application/backend/app/main.py)
- [helm/taskboard/templates/servicemonitor.yaml](../helm/taskboard/templates/servicemonitor.yaml)
- [monitoring/dashboard.json](../monitoring/dashboard.json)
- [images/aws-metrics-endpoint.png](../images/aws-metrics-endpoint.png)
- [images/aws-prometheus-targets-up.png](../images/aws-prometheus-targets-up.png)
- [evidence/logs/aws-prometheus-queries.json](../evidence/logs/aws-prometheus-queries.json)

### Slide 14 — Two failures. Two traceable recoveries.

In the first isolated exercise, the Pod was not Ready because its image tag did not exist. Pod description and events exposed the registry pull failure. After correcting the tag, the rollout reached Ready. In the second, the Service selector did not match the Pod labels, so EndpointSlices contained no usable endpoints. Comparing the selector against labels identified the cause. Correcting the selector restored endpoints and a successful HTTP response. Both exercises ran in taskboard-troubleshooting and the recorded recovery is saved. In the video, open the original image and Service diagnosis screenshots and the final recovery screenshot, or show the saved terminal logs. Keep the explanation in the order symptom, evidence, cause, correction, verification.

Evidence:

- [evidence/logs/aws-troubleshooting](../evidence/logs/aws-troubleshooting)
- [troubleshooting/broken-image.yaml](../troubleshooting/broken-image.yaml)
- [troubleshooting/broken-service.yaml](../troubleshooting/broken-service.yaml)
- [scripts/troubleshooting.sh](../scripts/troubleshooting.sh)
- [images/aws-broken-image-diagnosis.png](../images/aws-broken-image-diagnosis.png)
- [images/aws-broken-service-diagnosis.png](../images/aws-broken-service-diagnosis.png)
- [images/aws-troubleshooting-recovered.png](../images/aws-troubleshooting-recovered.png)

### Slide 15 — The deployment was verified, then removed.

The lifecycle ends with cleanup. All deployment screenshots and the walkthrough were pushed and verified remotely before deletion. The application and ALB were removed while the controller was still available; retained project storage was handled deliberately. Terraform then reported sixty-six resources destroyed. Read-only residual checks recorded the project EKS cluster, VPC, workers, ALB, target groups, NAT, EIP, network interfaces, retained disks and related roles as absent. The project KMS key is disabled and PendingDeletion for the required AWS waiting period, rather than already physically erased. Billing and credit reporting can lag, so the presentation does not claim zero usage or a settled cost total. DEPLOY_ENABLED is false and the old ALB URL is offline. The local stack remains available for review. No cloud resources need to be recreated to explain the preserved deployment evidence.

Evidence:

- [evidence/logs/aws-cleanup-verification.json](../evidence/logs/aws-cleanup-verification.json)
- [images/aws-terraform-destroy-complete.png](../images/aws-terraform-destroy-complete.png)
- [images/aws-cleanup-residual-checks.png](../images/aws-cleanup-residual-checks.png)
- [evidence/logs/aws-terraform-destroy.txt](../evidence/logs/aws-terraform-destroy.txt)
- [evidence/logs/aws-evidence-before-teardown.json](../evidence/logs/aws-evidence-before-teardown.json)
- [docs/CLEANUP.md](../docs/CLEANUP.md)

### Slide 16 — Tested. Reconciled. Observable.

The system connects product behavior to engineering evidence. The application is reproducible, data survives normal restarts, source and image gates stop unsafe changes, image SHAs connect source to registry artifacts, and Flux continuously reconciles the chosen release. The AWS lifecycle demonstrated real provisioning, ingress, persistent storage, monitoring, scaling and teardown. The later local GitOps verification adds real promotion and drift correction for the same application. Lessons are to verify application behavior after rollout, separate process liveness from database readiness, measure ready replicas for scaling, and tie every result to its revision and environment. Production improvements would add end-user authentication, HTTPS and DNS, managed database backups and service-level alerting. The repository includes original evidence, instructions and attribution; the recorded narration explains those results.

Evidence:

- [docs/VERIFICATION.md](../docs/VERIFICATION.md)
- [README.md](../README.md)
- [docs/ATTRIBUTION.md](../docs/ATTRIBUTION.md)

## Final submission

Submit your narrated recording, the PPTX (and PDF if accepted), and https://github.com/NoteLegend/devOps-TaskBoard. Include the source archive only if requested. The deck supplements actual project evidence; it does not replace the narration or instructor submission.

## Attribution

Release Helpdesk adapts Nensi Ravaliya’s MIT-licensed TaskBoard starter at commit `a4e39b6b3a54dab1efd386c75ab86bf1d8a23454`. See [project attribution](../docs/ATTRIBUTION.md) and [LICENSE](../LICENSE). All application, AWS, CI, monitoring and terminal screenshots embedded here are genuine repository evidence. The architecture diagrams and HPA chart are presentation graphics; the HPA chart is generated directly from the saved observations.
