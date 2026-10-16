# Genuine evidence

All screenshots are browser captures of this running application/monitoring stack. `*-local` and kind logs refer to a local Kubernetes cluster and do not establish AWS deployment.

- [Application desktop](application-desktop.png), [mobile](application-mobile.png), [Swagger](api-docs.png)
- [Prometheus target](prometheus-targets-local.png), [authenticated Grafana dashboard](grafana-dashboard-local.png)
- [Executed status and linked logs](../docs/VERIFICATION.md)
- [Full requirement mapping](../docs/REQUIREMENTS.md)

`logs/trivy-backend-initial.json` records a failed scan, not the final outcome. Final reports are `trivy-backend.json` and `trivy-frontend.json`. HPA logs must be read for actual replica counts and recovery, not just successful HTTP requests.

Verified external evidence: [successful CI](ci-first-run.png), [backend package](ghcr-backend.png), [frontend package](ghcr-frontend.png), [Git history](git-history.png), and `logs/ghcr-anonymous-pull.txt`.

Pending AWS evidence: actual approved AWS Terraform plan and VPC/EKS, live AWS Pods/Ingress/HPA/metrics, and authorized destroy/residual-cost verification. Terminal screenshot requirements not directly captured can be satisfied by opening the corresponding command output in a terminal and capturing it; use the exact demo commands in `docs/DEMO.md`. No fake terminal/AWS/CI screenshots are included.
