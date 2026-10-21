# Third-party notices

The platform retains upstream license and policy provenance alongside its own implementation.

| Material | Source | License |
|---|---|---|
| AWS Load Balancer Controller IAM policy | [Official v3.6.0 policy](https://github.com/kubernetes-sigs/aws-load-balancer-controller/blob/v3.6.0/docs/install/iam_policy.json), copied into `terraform/lbc-iam-policy.json`. | [Apache-2.0](AWS_LOAD_BALANCER_CONTROLLER_LICENSE) |
| Application starter | MIT-licensed TaskBoard source, adapted into Release Helpdesk. | [Retained project license](../LICENSE) |

Policy actions and conditions were reviewed before use. Flux is installed from its versioned upstream distribution rather than vendored here; scanner versions and rules are in [security](../security/README.md). [Full application attribution](../docs/ATTRIBUTION.md).
