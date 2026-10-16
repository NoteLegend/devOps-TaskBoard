# User setup and authorization checkpoints

Destination: https://github.com/NoteLegend/devOps-TaskBoard (remote inspected; no initial push authorized yet).
Git author: Rushi Jadhav, rushisjadhav3333@gmail.com (existing local configuration).

1. Authenticate GitHub locally: `.tools/gh auth login --hostname github.com --git-protocol https --web`, then `.tools/gh auth setup-git`. Do not paste login codes/tokens into chat. Review prepared commits before authorizing the first push to the destination. The instructor repository is never a push target.
2. Supply the agreed AWS profile and 12-digit account ID. Authenticate locally using AWS CLI v2 SSO (`aws configure sso --profile capstone`, then `aws sso login --profile capstone`) or an existing approved profile. Do not share secret values. Use `aws sts get-caller-identity --profile capstone` to check identity. The project-local `.venv/bin/aws` is CLI v1 for inspection and does not support SSO login; use CLI v2 for SSO.
3. Set `AWS_PROFILE` explicitly. Copy `terraform/terraform.tfvars.example` to ignored `terraform/terraform.tfvars`. Set account and persistent operator IAM ARN (not an STS assumed-role session ARN). Check for an existing GitHub OIDC provider before selecting `create_github_oidc_provider`.
4. Prepare actual `terraform plan`, itemized current regional estimate, account/resource list, and agreed running/teardown schedule. Wait for spending approval before apply. No cloud spend is approved by the current task.
5. After authorized provisioning, operator bootstraps namespaces, RBAC, LBC, storage, Metrics Server, monitoring and runtime secret using `scripts/bootstrap-aws.sh`.

Repository **Actions variables**, not secrets:

| Variable | Value |
|---|---|
| `AWS_REGION` | `ap-south-1` |
| `EKS_CLUSTER_NAME` | actual Terraform cluster output |
| `AWS_ROLE_ARN` | Terraform `deployment_role_arn` output |
| `DEPLOY_ENABLED` | `true` only after approved EKS bootstrap and public image pulling verification |

No AWS static-key GitHub secrets are required. No `KUBE_CONFIG_DATA` is used. `GITHUB_TOKEN` is provided by Actions; build/publish job has `packages: write`. PRs run tests, builds and scans without login, publishing or AWS deployment credentials. Publish and deploy only run on main outside PR events. Workflow concurrency serializes same-branch runs.

Use public GHCR packages for this classroom deployment. After initial publication, make both package visibilities public in GitHub package settings, then verify **anonymous** pull of each full-SHA image (`env -u DOCKER_CONFIG docker --config /tmp/empty-docker-config pull ...`). Do not enable deployment until this succeeds. Publishing a package does not make it public automatically. Private packages require a separate permanent read-only `read:packages` credential in a Kubernetes imagePullSecret referenced by `imagePullSecrets`; the workflow GITHUB_TOKEN is temporary and cannot serve that role. Private package mode is not the selected setup.

Credential locations: GitHub CLI credential store or `~/.config/gh`, AWS `~/.aws`/SSO cache, local kubeconfig `~/.kube/config`, Kubernetes `taskboard/taskboard-runtime`, Terraform local state under ignored `terraform/`. Never commit, archive or screenshot their contents. Terraform state remains local/private for this single-operator classroom project; no remote state service is provisioned.

GitHub repository visibility/instructor access and AWS demo lifetime must be agreed with the user. Submission requires real Actions/package/EKS evidence, observed HPA scaling, monitoring, and authorized teardown evidence.
