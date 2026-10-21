# Visual evidence

Original screenshots and browser activity show the application and platform as they ran. The library separates recorded AWS captures from local reproduction.

[Watch the demo](https://drive.google.com/file/d/1ZSxd5RlMJAqJkvLA3E_098BrKF4OgJLT/view?usp=sharing) · [Read the presentation](../presentation/Release-Helpdesk-Presentation.pdf) · [Download the slides](../presentation/Release-Helpdesk-Presentation.pptx?raw=1)

![Release Helpdesk on the recorded AWS deployment](aws-application-desktop.png)

| Area | Open the original captures |
|---|---|
| Application | [Desktop](aws-application-desktop.png) · [mobile](aws-application-mobile.png) · [Swagger](aws-swagger-statistics-executed.png) · [browser recording](aws-browser-walkthrough.webm) |
| API and data | [PostgreSQL tests](aws-postgresql-pytest-passed.png) · [table and persistence](aws-postgresql-table-and-persistence.png) |
| Delivery | [AWS pipeline](aws-ci-successful-deployment.png) · [tests/scans](aws-tests-and-trivy-results.png) · [backend registry](aws-ghcr-backend.png) · [frontend registry](aws-ghcr-frontend.png) |
| Visible release | [Before](aws-live-update-before.png) · [after](aws-live-update-after.png) |
| Infrastructure | [Plan](aws-terraform-plan.png) · [VPC](aws-vpc-console.png) · [EKS](aws-eks-active-console.png) · [ready nodes](aws-terraform-apply-and-ready-nodes.png) |
| Kubernetes | [Pods, Services, PVC, Helm and Ingress](aws-kubernetes-helm-ingress.png) |
| Autoscaling | [Before](aws-hpa-before-load.png) · [under load](aws-hpa-scaled-under-load.png) · [recovered](aws-hpa-recovered.png) |
| Observability | [Metrics](aws-metrics-endpoint.png) · [targets UP](aws-prometheus-targets-up.png) · [Grafana](aws-grafana-live-dashboard.png) |
| Recovery | [Bad image](aws-broken-image-diagnosis.png) · [wrong selector](aws-broken-service-diagnosis.png) · [recovered](aws-troubleshooting-recovered.png) |
| Teardown | [Destroy completed](aws-terraform-destroy-complete.png) · [residual checks](aws-cleanup-residual-checks.png) · [EKS absent](aws-eks-console-after-cleanup.png) |
| Current delivery / GitOps | [Integrated security pipeline](final/ci-security-release.png) · [Flux promotion and drift correction](final/gitops-verification.png) · [fresh browser](final/application-desktop.png) · [current UI clip](final/browser-walkthrough.webm) |
| Local reproduction | [Compose images/users](local-compose-images-and-users.png) · [local screenshot library](local/) |

## Provenance

[manifest.json](manifest.json) records the source, capture timestamp and SHA-256 digest of each original image/video. The packaging helper verifies these hashes. AWS evidence was pushed and independently checked before teardown. The previous AWS URL no longer serves traffic.

The WEBM files preserve short, original UI sequences. The linked demo video provides the recorded walkthrough; the presentation explains the architecture and engineering approach.
