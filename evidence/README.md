# Genuine evidence

The complete [screenshot/video index](../images/README.md) includes genuine AWS Console, terminal, application, CI/GHCR, monitoring, scaling, troubleshooting and cleanup captures. [Manifest](../images/manifest.json) records actual sources, timestamps and SHA-256 digests. Historical local captures are labelled separately and do not substitute for AWS.

- [Executed verification and limitations](../docs/VERIFICATION.md), [requirement mapping](../docs/REQUIREMENTS.md).
- [Deployment media remotely verified before any teardown](logs/aws-evidence-before-teardown.json).
- [Real successful AWS deployment](https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/38955563228).
- [Observed AWS HPA 2→4→2](logs/aws-hpa-internal/summary.json), [backend metrics and targets](logs/aws-prometheus-queries.json).
- [Actual destroy transcript](logs/aws-terraform-destroy.txt), [residual/account checks](logs/aws-cleanup-verification.json), [cleanup screenshots](../images/aws-terraform-destroy-complete.png).
- [Known-pattern Git history secret scan](logs/git-history-secret-scan.json).

Original failures are retained honestly: initial backend CVEs, initial OIDC trust mismatch and external load that did not cause scaling. Final app scans have zero HIGH/CRITICAL findings at the recorded date; future CVEs/lower severities are not claimed clean. AWS resources were removed after screenshots were pushed; the historical ALB URL no longer runs. The browser video is real UI activity, not a narrated student presentation.
