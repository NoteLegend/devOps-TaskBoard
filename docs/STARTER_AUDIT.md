# Starter audit and repairs

Upstream commit and attribution: [ATTRIBUTION.md](ATTRIBUTION.md). Full README and GRADING.md inspected. The rubric requires an original domain, so the user selected DevOps Release Helpdesk. Existing `tasks` API/table and all supported fields are retained.

| Area | Upstream issue | Implementation |
|---|---|---|
| Workflow placement | Nested teaching directory would not be discovered | Starter integrated at destination root; `.github/workflows/ci-cd.yml`, root-relative contexts/artifacts |
| Registry | `YOUR_ORG`, mixed-case owners, latest tags | Lowercase full repository prefix, separate application/backend/frontend packages, full SHA tags; anonymous pulls and AWS Pod digests actually verified |
| EKS auth | Saved kubeconfig without AWS credentials/access | GitHub branch-restricted OIDC IAM role, `eks:DescribeCluster`, EKS access entry, namespace RoleBinding; no saved kubeconfig secret |
| Terraform | Invalid one-line HCL, old providers/EKS | Formatted HCL, module pins/provider lockfile, EKS 1.35, selected account guard, regional AZ lookup |
| Network | No subnet discovery labels | Public/private ELB role tags; private managed workers, one NAT for classroom cost tradeoff |
| Ingress | No controller, nginx class, wrong backend name/8080 | AWS LBC with IRSA, `alb` class, actual backend port 8000; Traefik for local tests; no retired community ingress-nginx |
| Storage | PVC but no EKS storage driver/class | EBS CSI IRSA/add-on and encrypted gp3 WaitForFirstConsumer StorageClass; retained EBS volumes require deliberate cleanup |
| Metrics | HPA assumed metrics provider | EKS Metrics Server add-on; local chart uses insecure kubelet TLS only for kind |
| Monitoring | ServiceMonitor enabled without CRDs | Off by default; bootstrap Operator before enabling; release label `monitoring`, service label and named `http` port, `/metrics` scrape |
| Migrations | Every API replica migrated and startup called create_all | Explicit one-shot Compose migration; Helm Job with PostgreSQL advisory lock; no API schema creation. First install hook is post-install; do not use Helm `--wait` before this hook |
| Probes | DB failures returned 500 | Process-only health; DB/table-aware readiness returns sanitized 503; API is unready before migrations |
| Routing | Nginx `backend` did not match Helm service | Release-scoped Nginx ConfigMap points to actual backend service; same-origin `/api` and `/docs`; Vite proxy uses 8000 |
| Secrets | Plaintext Helm passwords | Pre-created runtime Secret; no password in chart/CI arguments; secret helper preserves existing values |
| Compose | No health ordering | DB health → migration completion → API readiness → frontend; private DB and loopback host bindings |
| UI | Create/status only, unchecked mutations, fabricated activity/CI status | Validated create/edit/delete; loading/error messages, filters/search, real browser-session activity, delivery diagram clearly not run status |
| Tests | Three weak tests and create_all coupling | CRUD/statistics/validation/404/DB failure recovery/metrics; integration runner applies real PostgreSQL migrations |
| Failure labs | Broke main namespace, mismatched target ports | Fixed isolated namespace, intentional bad tag/selector, diagnostics and recovery helper |

Current primary references (inspected 2026-10-16):

- https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html — 1.35 is standard support; recheck regional support before applying.
- https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html — CSI requires IAM permissions and driver.
- https://docs.aws.amazon.com/eks/latest/userguide/lbc-helm.html — install actual controller with service-account IAM.
- https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws — trust audience and repository/branch subject.
- https://github.com/terraform-aws-modules/terraform-aws-eks/blob/v21.26.0/variables.tf — v21 module input names and add-on/access configuration.
- https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack — Operator/ServiceMonitor prerequisites.
- https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/ — community ingress-nginx retirement; AWS LBC and Traefik selected instead.

Dependency versions are pinned in requirements, npm lockfile, Terraform lockfile and bootstrap chart versions. Container base tags receive security updates; record image IDs/digests during each verified build. A pinned tag alone is not an immutable base digest.

Additional verification findings: pin GitHub runners to Ubuntu 24.04 and update upload-artifact/login/Helm/kubectl/AWS credential actions to current Node 24 releases after the first real run reported deprecated runtimes. EKS worker root disks use explicit encrypted gp3 block-device mappings: the module’s custom launch template ignores node-group `disk_size`.

Archive verification caught the starter’s `terraform/.gitignore` excluding `.terraform.lock.hcl`. That exclusion was removed, the provider lockfile committed, and the ZIP helper now requires it alongside all handover documents.
