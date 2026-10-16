# First AWS login for a new personal account

The selected account is `835582727900`, region `ap-south-1`, and requested profile name is `Raghavendra Linga`. Account ID and profile name are configuration, not authentication. No cloud spend is approved yet.

A new personal account usually has an email/password root login and no IAM Identity Center SSO portal. Use the project-local AWS CLI v2 (signature verified against AWS’s published signing key):

```bash
.tools/aws login --profile 'Raghavendra Linga' --region ap-south-1
.tools/aws sts get-caller-identity --profile 'Raghavendra Linga'
```

Complete login in your browser. Keep password, MFA/browser codes and cached credentials private. No access keys or SSO start URL are required for this login method. AWS documents it at https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html . Tokens are cached outside this repository in `~/.aws/login/cache`.

If identity is `arn:aws:iam::835582727900:root`, use it to verify account setup, then establish a dedicated operator identity before EKS provisioning. An EKS access entry needs an IAM user/role ARN; root is not the intended application operator.

For a small classroom account, the console path is IAM → Users → Create user → `capstone-operator`, enable console access and choose an IAM user if prompted. Grant the provisioning permissions needed for VPC/EKS/IAM (AdministratorAccess is broad and should be limited to the classroom operator), and `SignInLocalDevelopmentAccess` for browser CLI login. Set its password privately, sign in as that user, and run the same `aws login` command to select it. Protect the root account with MFA; use this operator for subsequent work. Routine CI uses the separate, narrowly scoped OIDC deployment role in Terraform, never this operator’s credentials.

New SDKs may support `login_session` directly. If Terraform does not, use a separate local process-credential profile that calls `aws configure export-credentials --profile 'Raghavendra Linga' --format process`. Its output must go directly to the SDK, never a chat, screenshot, committed file or evidence log.

After login, the agent can verify the account/permissions, select the persistent operator ARN, generate the real Terraform plan, obtain current Mumbai pricing and present the spending checkpoint. **Login is not approval to apply Terraform.**
