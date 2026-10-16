# Remaining work against the original capstone

Updated 2026-10-16. The original AWS/EKS requirements remain in scope. This is not a local-only substitution. The credit-only plan was approved and Terraform apply began at 2026-10-16T18:16Z. Screenshots and GitHub push must precede teardown.

## Completed

Application, API, PostgreSQL migrations/integration tests, Docker/Compose, browser verification, real CI/GHCR publication/scans, Terraform validation/actual plan, Helm and local Kubernetes verification. Local Ingress, PVC persistence, monitoring, CPU HPA 2 → 4 → 2 and both isolated failure exercises have genuine evidence in [VERIFICATION.md](VERIFICATION.md).

AWS account 835582727900 is authenticated. The Free Tier API reports FREE/ACTIVE and $117.20 credits. Revised worker type and EKS AMI are FreeTierEligible; both selected AZs offer that type. [Eligibility evidence](../evidence/logs/aws-free-tier-eligibility.json). A revised actual plan creates 66 Terraform objects; ALB and database disk follow through Kubernetes. No Paid-plan upgrade or cash spending is authorized.

## Not completed

| Requirement | Current result | What is needed |
|---|---|---|
| Actual AWS infrastructure | IN PROGRESS | Approved apply running; verify VPC, EKS, workers, IAM/add-ons and networking |
| Actual EKS bootstrap | NOT RUN | Verify nodes, EBS CSI, gp3 StorageClass, Metrics Server, ALB controller, monitoring CRDs and runtime configuration |
| CI deployment to AWS | NOT RUN; disabled | Configure the actual OIDC role output, enable deployment only after prerequisites, run Actions and verify the deployed immutable SHA |
| AWS application and storage | NOT RUN | Verify migration Job, Ready Pods, bound EBS PVC, service endpoints, ALB routing, browser/API CRUD/statistics, database persistence/readiness and Swagger |
| AWS metrics/HPA/exercises | NOT RUN | Verify actual application scrapes/dashboard queries, bounded CPU load and replica increase/recovery; repeat isolated failures and fixes on the agreed EKS cluster |
| AWS demo and submission evidence | NOT RUN | Rehearse the full instructor sequence against AWS, capture genuine sanitized evidence and refresh the archive/status |
| AWS teardown and residual resources | NOT RUN | After evidence/export and authorized project-data deletion, remove ALB/PVC/EBS and Terraform stack; record residual-cost checks |

The original assignment is **not yet fully submission-ready**. Existing local evidence proves local behavior only. See [the concrete Free Tier checkpoint](COST_CHECKPOINT.md) for the pending approval: eligible services funded only by credits, no Paid upgrade, up to three hours including cleanup. Stop if AWS demands a plan upgrade or eligibility/credit checks fail.
