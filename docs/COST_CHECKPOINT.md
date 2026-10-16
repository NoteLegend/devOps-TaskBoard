# AWS Free Tier deployment checkpoint

**Original AWS/EKS requirements remain in scope. Approved apply began at 2026-10-16T18:16Z; creation is in progress.** The user requires no out-of-pocket spending and no replacement deployment stack. Do not upgrade this account to a Paid plan or activate paid-only services.

## Verified account and proposed resources

- Account **835582727900**, IAM operator `shrival`, source profile `Raghavendra Linga`, region **ap-south-1**.
- AWS Free Tier API reports **FREE / ACTIVE**, **$117.20 USD remaining credits**, expiration **2027-02-15T11:21:26Z**. [Actual guard result](../evidence/logs/aws-free-tier-guard.json).
- New authenticated plan: **66 add, 0 change, 0 destroy**, captured 2026-10-16T18:12:41.898274+00:00.
- Saved private plan: `terraform/free-tier.tfplan`; SHA-256 `46cabe4c47e711371099fcebde0353de3d634ed3199443f6636a8432743fefaf`. Never publish the binary or state. **The earlier `approved.tfplan` is superseded and must not be applied.**
- EKS **1.35** control plane; two **m7i-flex.large** AL2023 x86_64 managed workers (2 vCPU/8 GiB RAM each), two encrypted 20-GiB gp3 root disks.
- New VPC 10.20.0.0/16, two public and two private subnets in ap-south-1a/b, IGW/routes/security groups, one NAT gateway/EIP; EKS add-ons for networking, DNS, EBS CSI and Metrics Server.
- Five IAM roles, GitHub/cluster OIDC providers, operator/CI access entries, one KMS key and seven-day EKS logs. CI gets DescribeCluster and read-only Free Tier status; Kubernetes access stays namespace-scoped.
- Kubernetes bootstrap later creates **one internet-facing ALB** and **one encrypted 5-GiB PostgreSQL gp3 EBS volume**, additional to the 66 Terraform objects. Prometheus/Grafana run inside these workers and remain private/authenticated.
- An unrelated running EC2 instance is excluded and will remain untouched. No RDS, paid domain, paid API or additional worker autoscaler.

The original t3.medium plan was revised because t3.medium is not Free-plan eligible. AWS reports m7i-flex.large and the selected EKS AL2023 AMI eligible, with the worker type offered in both selected AZs: [actual eligibility checks](../evidence/logs/aws-free-tier-eligibility.json). This changes worker capacity only; the required application, Terraform, EKS, Helm, Ingress and monitoring stack stay the same.

[All 66 new resources](../evidence/logs/terraform-free-tier-resource-inventory.json) · [sanitized plan summary](../evidence/logs/terraform-free-tier-plan-summary.txt) · [current gross rates/model](../evidence/logs/aws-free-tier-pricing-estimate.json).

## Credits, gross prices and proposed lifetime

EKS itself is **not an always-free service**: its standard-support control plane costs $0.10/hour. The proposed deployment uses the verified Free account plan and promotional credits. AWS documents that the Free plan incurs no charges until upgraded and closes when its credits/time expire. Some services/features can be unavailable; stop if AWS requires an upgrade. Do not switch to Paid, join Organizations, activate advanced features or use Marketplace purchases to bypass a restriction.

| Component | Gross USD/hour before credits |
|---|---:|
| EKS control plane | 0.1000 |
| Two m7i-flex.large workers ($0.10075 each/hour) | 0.2015 |
| NAT gateway | 0.0560 |
| ALB plus assumed average one LCU/hour | 0.0319 |
| Three minimum public IPv4 addresses | 0.0150 |
| 45 GiB gp3 and one KMS key, prorated | 0.0070 |
| **Baseline** | **0.4114** |

Proposed lifetime: **up to three hours including creation, AWS verification/demo, evidence saving and teardown**. Model: **$1.81 in credits** including startup/usage assumptions; propose **up to $3 credit consumption** as the working allowance, **$0 cash spending authorized**. The $3 estimate is not a technical hard cap. Credit usage can be delayed; additional traffic/logs, ALB scaling, retained disks or delayed cleanup consume more credits. Existing unrelated account activity also uses credits.

Assumptions: 5 GB NAT processing, 0.25 GB log ingestion, 10,000 symmetric KMS calls, $0.10 transfer allowance, average one ALB LCU/hour, 730-hour proration for monthly storage/key rates. Baseline for 24 hours would be about $9.87 in credits, so leaving the cluster running indefinitely is excluded.

## Checks and cleanup

`scripts/check-free-tier.py --account 835582727900` is read-only. It refuses Paid/inactive/wrong accounts, balances under $20, and plans expiring within four hours. Run it immediately before apply, bootstrap and deployment. Bootstrap and the retained CI deployment job enforce it. [Six guard tests](../evidence/logs/free-tier-guard-tests.txt) passed, including rejected Paid, wrong-account, low-credit and expiring-plan cases. This check is not a spending limiter and never upgrades an account.

After evidence and a private synthetic DB export are saved, delete the app Ingress while its controller runs and verify ALB removal; uninstall the release/monitoring; remove only this new project's retained PostgreSQL PVC/PV/EBS volume with data-deletion authorization; remove LBC; review/destroy this Terraform stack; check for residual workers, EBS, NAT/EIP, ELB, logs and KMS state. Follow [CLEANUP.md](CLEANUP.md). Keep the repository, registry images, evidence and unrelated EC2 instance.

**Approved 2026-10-16T18:16Z:** the user approved this credit-funded plan and instructed deployment, screenshots saved under `images/`, and a GitHub push before teardown. Remove only project resources/synthetic data after evidence is saved and pushed. No cash spending or Paid-plan upgrade is approved. The proposed three-hour window starts at apply (18:16Z); target full teardown by 21:16Z.

Primary sources: [EKS prices](https://aws.amazon.com/eks/pricing/), [AWS account plans](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html), [Free Tier service support](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html), [EC2 eligible instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html), [Free Tier status API](https://docs.aws.amazon.com/cli/latest/reference/freetier/get-account-plan-state.html). Rates were queried directly from AWS Price List for Mumbai.
