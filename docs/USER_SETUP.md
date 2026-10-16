# User setup and authorization checkpoints

Destination: https://github.com/NoteLegend/devOps-TaskBoard (verified public repository; initial push and CI/GHCR fixes authorized and completed).
Git author: Rushi Jadhav, rushisjadhav3333@gmail.com (existing local configuration).

1. Authenticate GitHub locally: `.tools/gh auth login --hostname github.com --git-protocol https --web`, then `.tools/gh auth setup-git`. Do not paste login codes/tokens into chat. Initial push approval has been given; subsequent task fixes may be pushed to this same destination. The instructor repository is never a push target.
2. AWS login **verified**: account `835582727900`, IAM user `shrival`, region `ap-south-1`, source profile `Raghavendra Linga`. Renew locally if needed: `.tools/aws login --profile 'Raghavendra Linga' --region ap-south-1`. Never share credential values. See [first-login guide](AWS_FIRST_LOGIN.md).
3. The ignored Terraform variables and process-profile adapter are configured for this identity. No existing project cluster/VPC or GitHub OIDC provider was found. The operator's provisioning permissions and available worker quota were checked read-only.
4. The actual authenticated plan and regional estimate are prepared in [COST_CHECKPOINT.md](COST_CHECKPOINT.md). AWS reports an ACTIVE FREE plan and $117.20 credits. **Only credits may fund eligible services; no Paid upgrade or cash spending is authorized. Approval of the revised plan, credit use, lifetime and cleanup remains required before apply.**
5. After authorized provisioning, operator bootstraps namespaces, RBAC, LBC, storage, Metrics Server, monitoring and runtime secret using `scripts/bootstrap-aws.sh`.

Repository **Actions variables**, not secrets:

| Variable | Value |
|---|---|
| `AWS_REGION` | `ap-south-1` |
| `EKS_CLUSTER_NAME` | actual Terraform cluster output |
| `AWS_ROLE_ARN` | Terraform `deployment_role_arn` output |
| `DEPLOY_ENABLED` | `true` only after approved EKS bootstrap and public image pulling verification |

No AWS static-key GitHub secrets are required. No `KUBE_CONFIG_DATA` is used. `GITHUB_TOKEN` is provided by Actions; build/publish job has `packages: write`. PRs run tests, builds and scans without login, publishing or AWS deployment credentials. Publish and deploy only run on main outside PR events. Workflow concurrency serializes same-branch runs.

Use public GHCR packages for this classroom deployment. Both packages were verified anonymously pullable after publication. If a future package is private, make its visibility public in GitHub package settings, then verify **anonymous** pull of each full-SHA image (`env -u DOCKER_CONFIG docker --config /tmp/empty-docker-config pull ...`). Do not enable deployment until this succeeds. Publishing a package does not make it public automatically. Private packages require a separate permanent read-only `read:packages` credential in a Kubernetes imagePullSecret referenced by `imagePullSecrets`; the workflow GITHUB_TOKEN is temporary and cannot serve that role. Private package mode is not the selected setup.

Credential locations: GitHub CLI credential store or `~/.config/gh`, AWS `~/.aws`/SSO cache, local kubeconfig `~/.kube/config`, Kubernetes `taskboard/taskboard-runtime`, Terraform local state under ignored `terraform/`. Never commit, archive or screenshot their contents. Terraform state remains local/private for this single-operator classroom project; no remote state service is provisioned.

GitHub repository visibility/instructor access and AWS demo lifetime must be agreed with the user. Submission requires real Actions/package/EKS evidence, observed HPA scaling, monitoring, and authorized teardown evidence.

Authentication was verified as IAM user `shrival` in account `835582727900`; the user explicitly confirmed this new account. Source profile `Raghavendra Linga` uses the browser temporary session. The AWS config header is quoted because its name contains a space. Terraform's SDK uses local profile `taskboard-terraform`, whose `credential_process` runs the AWS CLI export directly into the SDK; no exported credential values are stored in the repository. For local Terraform commands use `export AWS_PROFILE=taskboard-terraform`; for CLI/bootstrap use `export AWS_PROFILE='Raghavendra Linga'`. Account-level provisioning permissions were checked read-only; routine CI remains the separate OIDC deployment role.

To recreate the SDK adapter on this machine (configuration contains a command, never credential values):

```bash
.tools/aws configure set credential_process "$PWD/.tools/aws configure export-credentials --profile \"Raghavendra Linga\" --format process" --profile taskboard-terraform
.tools/aws configure set region ap-south-1 --profile taskboard-terraform
AWS_PROFILE=taskboard-terraform .tools/aws sts get-caller-identity
```

If the project path contains spaces, quote the executable path inside `credential_process` too. The source browser profile must already be authenticated.

OIDC update: GitHub reports `use_immutable_subject=true` with `sub_claim_prefix=repo:NoteLegend@184594732/devOps-TaskBoard@1422224595`. Terraform requires `github_oidc_subject_prefix` and appends only `:ref:refs/heads/main`; do not substitute the legacy names-only subject or lowercase the OIDC repository name. Query with `.tools/gh api repos/NoteLegend/devOps-TaskBoard/actions/oidc/customization/sub --jq .sub_claim_prefix`. IDs in the subject bind trust to this repository. [GitHub reference](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims).
