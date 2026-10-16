# Genuine capstone screenshots and walkthrough

Actual AWS account **835582727900**, region **ap-south-1**. Captures are genuine AWS Console/terminal/browser output; no screenshots are mocked. `manifest.json` records their sources, timestamps or preserved file modification times, and SHA-256 digests. Historical local captures are grouped under `local/`.

Application image SHA: `179ad20c5e4995bf458a33531905d6f0e694b580`. The walkthrough is an actual browser recording of create/edit/filter/delete, mobile, Swagger execution and metrics through the ALB; it is not a narrated student presentation. AWS resources are removed after deployment evidence is pushed, so these captures remain available after the live URL is shut down.

## Start here

| Requirement | Genuine capture |
|---|---|
| Application through AWS Ingress | [Desktop](aws-application-desktop.png), [mobile](aws-application-mobile.png), [actual browser walkthrough](aws-browser-walkthrough.webm) |
| Browser CRUD / API statistics | [Create](aws-ticket-created.png), [saved/filter state](aws-ticket-updated-filtered.png), [Swagger executed 200](aws-swagger-statistics-executed.png) |
| Tests / security | [PostgreSQL/Alembic/pytest](aws-postgresql-pytest-passed.png), [actual CI scan results](aws-tests-and-trivy-results.png) |
| CI/CD / registry / Git | [Successful AWS deployment pipeline](aws-ci-successful-deployment.png), [PR gates skip publishing/deploy](pr-validation-no-deployment.png), [GHCR backend](aws-ghcr-backend.png), [frontend](aws-ghcr-frontend.png), [meaningful commits](git-meaningful-history.png) |
| Visible commit → CI → AWS update | [Before](aws-live-update-before.png), [after](aws-live-update-after.png), [successful pipeline](aws-ci-successful-deployment.png) |
| Terraform / AWS infrastructure | [Actual plan](aws-terraform-plan.png), [apply and Ready nodes](aws-terraform-apply-and-ready-nodes.png), [VPC Console](aws-vpc-console.png), [healthy EKS Console](aws-eks-active-console.png) |
| Kubernetes / Helm / storage | [Pods, Services, PVC, Helm and ALB](aws-kubernetes-helm-ingress.png), [database table/revision/persistence](aws-postgresql-table-and-persistence.png) |
| CPU-based HPA | [Before](aws-hpa-before-load.png), [four Ready under load](aws-hpa-scaled-under-load.png), [automatic recovery](aws-hpa-recovered.png) |
| Real monitoring | [Backend metrics](aws-metrics-endpoint.png), [Prometheus targets UP](aws-prometheus-targets-up.png), [authenticated Grafana panels](aws-grafana-live-dashboard.png) |
| Isolated failures / fixes | [Bad image diagnosis](aws-broken-image-diagnosis.png), [wrong Service selector](aws-broken-service-diagnosis.png), [HTTP recovery](aws-troubleshooting-recovered.png) |
| Authorized cleanup after evidence push | [66 destroyed](aws-terraform-destroy-complete.png), [26 residual checks](aws-cleanup-residual-checks.png), [empty EKS Console](aws-eks-console-after-cleanup.png) |
| Local Docker | [Actual Compose images, health and runtime users](local-compose-images-and-users.png) |

## Complete capture list

- [aws-application-desktop.png](aws-application-desktop.png)
- [aws-application-mobile.png](aws-application-mobile.png)
- [aws-broken-image-diagnosis.png](aws-broken-image-diagnosis.png)
- [aws-broken-service-diagnosis.png](aws-broken-service-diagnosis.png)
- [aws-browser-walkthrough.webm](aws-browser-walkthrough.webm)
- [aws-ci-successful-deployment.png](aws-ci-successful-deployment.png)
- [aws-eks-active-console.png](aws-eks-active-console.png)
- [aws-eks-provisioning-console.png](aws-eks-provisioning-console.png)
- [aws-ghcr-backend.png](aws-ghcr-backend.png)
- [aws-ghcr-frontend.png](aws-ghcr-frontend.png)
- [aws-grafana-live-dashboard.png](aws-grafana-live-dashboard.png)
- [aws-hpa-before-load.png](aws-hpa-before-load.png)
- [aws-hpa-recovered.png](aws-hpa-recovered.png)
- [aws-hpa-scaled-under-load.png](aws-hpa-scaled-under-load.png)
- [aws-kubernetes-helm-ingress.png](aws-kubernetes-helm-ingress.png)
- [aws-live-update-after.png](aws-live-update-after.png)
- [aws-live-update-before.png](aws-live-update-before.png)
- [aws-metrics-endpoint.png](aws-metrics-endpoint.png)
- [aws-postgresql-pytest-passed.png](aws-postgresql-pytest-passed.png)
- [aws-postgresql-table-and-persistence.png](aws-postgresql-table-and-persistence.png)
- [aws-prometheus-targets-up.png](aws-prometheus-targets-up.png)
- [aws-swagger-statistics-executed.png](aws-swagger-statistics-executed.png)
- [aws-swagger.png](aws-swagger.png)
- [aws-terraform-apply-and-ready-nodes.png](aws-terraform-apply-and-ready-nodes.png)
- [aws-terraform-plan.png](aws-terraform-plan.png)
- [aws-tests-and-trivy-results.png](aws-tests-and-trivy-results.png)
- [aws-ticket-create-form.png](aws-ticket-create-form.png)
- [aws-ticket-created.png](aws-ticket-created.png)
- [aws-ticket-updated-filtered.png](aws-ticket-updated-filtered.png)
- [aws-troubleshooting-recovered.png](aws-troubleshooting-recovered.png)
- [aws-vpc-console.png](aws-vpc-console.png)
- [git-meaningful-history.png](git-meaningful-history.png)
- [local/api-docs-ingress-local.png](local/api-docs-ingress-local.png)
- [local/api-docs.png](local/api-docs.png)
- [local/application-desktop-ingress-local.png](local/application-desktop-ingress-local.png)
- [local/application-desktop.png](local/application-desktop.png)
- [local/application-mobile-ingress-local.png](local/application-mobile-ingress-local.png)
- [local/application-mobile.png](local/application-mobile.png)
- [local/ci-first-run.png](local/ci-first-run.png)
- [local/ghcr-backend.png](local/ghcr-backend.png)
- [local/ghcr-frontend.png](local/ghcr-frontend.png)
- [local/git-history.png](local/git-history.png)
- [local/grafana-dashboard-local.png](local/grafana-dashboard-local.png)
- [local/prometheus-targets-local.png](local/prometheus-targets-local.png)
- [local-compose-images-and-users.png](local-compose-images-and-users.png)
- [pr-validation-no-deployment.png](pr-validation-no-deployment.png)

- [aws-terraform-destroy-complete.png](aws-terraform-destroy-complete.png)
- [aws-cleanup-residual-checks.png](aws-cleanup-residual-checks.png)
- [aws-eks-console-after-cleanup.png](aws-eks-console-after-cleanup.png)

Cleanup completed after the remotely verified deployment media push at commit `8439aa3`. [Gate proof](../evidence/logs/aws-evidence-before-teardown.json), [actual destroy](../evidence/logs/aws-terraform-destroy.txt), [26 residual checks](../evidence/logs/aws-cleanup-verification.json). The extra cleanup captures were taken after shutdown and pushed separately. The historical AWS endpoint is intentionally removed.
