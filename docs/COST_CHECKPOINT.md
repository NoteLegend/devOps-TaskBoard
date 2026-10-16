# Cloud spending checkpoint — AWAITING USER APPROVAL

Prepared from an actual authenticated Terraform plan on 2026-10-16T17:44:58.275764+00:00. **No apply or billable resource creation has occurred.**

- Agreed account: **835582727900**; IAM operator: `arn:aws:iam::835582727900:user/shrival`.
- Source login profile: **Raghavendra Linga**; Terraform uses the local `taskboard-terraform` process-credential adapter for this same identity.
- Region: **ap-south-1 (Mumbai)**; cluster: **taskboard-eks**, EKS **1.35** (verified in regional standard support).
- Actual result: **66 add, 0 change, 0 destroy**. No existing project VPC, EKS cluster or GitHub OIDC provider found.
- One unrelated t4g.small instance exists and remains untouched. Standard On-Demand quota is 8 vCPUs; existing usage is 2, proposed workers use 4 more.
- Private binary plan: `terraform/approved.tfplan`. Do not commit/archive it or Terraform state.
- Plan SHA-256: `76285e71a9bf2075f41db0723d709eefd47f7b13f8ae3fe1610e1dce7dc1a46e`. Re-plan and obtain fresh approval if proposed billable resources materially change.

[Sanitized actual plan](../evidence/logs/terraform-plan-summary.txt) · [all 66 resources and versions](../evidence/logs/terraform-resource-inventory.json) · [current AWS Price List rates/model](../evidence/logs/aws-pricing-estimate.json)

## Resources covered by this proposed approval

| Group | Concrete resources |
|---|---|
| Network | New 10.20.0.0/16 VPC; public 10.20.101.0/24 and 10.20.102.0/24, private 10.20.1.0/24 and 10.20.2.0/24 in ap-south-1a/b; routes, IGW, discovery tags; one NAT gateway/EIP; security groups/rules and new-VPC default network resources |
| Kubernetes | One standard-support EKS 1.35 control plane; one managed node group with exactly two t3.medium On-Demand AL2023 workers; two encrypted 20-GiB gp3 root disks; worker release pinned to 1.35.8-20261012 |
| Add-ons | Compatible builds pinned from DescribeAddonVersions: vpc-cni v1.22.4-eksbuild.3; kube-proxy v1.35.3-eksbuild.52; CoreDNS v1.13.2-eksbuild.51; EBS CSI v1.67.0-eksbuild.1; Metrics Server v0.9.0-eksbuild.13 |
| Identity and logs | Five IAM roles, policy attachments, EKS/operator access entries; GitHub and cluster OIDC providers; one customer-managed KMS key/alias; EKS API/audit/authenticator log group with seven-day retention |
| Bootstrap after Terraform | AWS Load Balancer Controller and **one internet-facing ALB**, target groups/security rules and minimum two ALB public IPv4 addresses; **one encrypted 5-GiB gp3 PostgreSQL PVC/EBS volume**; Prometheus/Grafana inside the existing workers, private access only |

The ALB and database EBS volume are created by Kubernetes controllers after Terraform and are **additional to the 66 Terraform objects**. Worker EC2 instances/root disks are children of the node-group/launch-template resources. No RDS, paid domain, extra worker autoscaler or paid external API is included.

## Current cost estimate (USD, excluding tax/credits)

Rates were retrieved directly through AWS Price List GetProducts (pricing endpoint us-east-1, products filtered to Mumbai). Effective dates and SKUs are retained in the rate/model JSON. No free-tier or promotional credits are assumed.

| Component | Quantity and rate | Estimated USD/hour |
|---|---|---:|
| EKS control plane | 1 × $0.10/hour | 0.1000 |
| EC2 workers | 2 × $0.0448/hour | 0.0896 |
| NAT gateway | 1 × $0.056/hour | 0.0560 |
| ALB | 1 × $0.0239/hour | 0.0239 |
| ALB capacity assumption | Average 1 LCU × $0.008/hour | 0.0080 |
| Public IPv4 | 3 minimum × $0.005/hour (NAT + two ALB addresses) | 0.0150 |
| gp3 storage | 45 GiB × $0.0912/GiB-month, prorated /730h | 0.0056 |
| KMS key | 1 × $1/month, prorated /730h | 0.0014 |
| **Baseline total** | Before usage-based additions | **0.2995** |

Proposed lifetime: **up to three hours**, including provisioning, verification/demo, evidence capture and teardown. Modeled three-hour baseline is **$0.90**. With 5 GB NAT processing ($0.28), 0.25 GB log ingestion ($0.1675), 10,000 symmetric KMS calls ($0.03), and $0.10 cross-AZ/transfer allowance, the model is **about $1.48**. Proposed working budget is **$3 excluding applicable tax** to allow headroom.

This is an estimate, **not a billing cap**. Extra traffic/logs, ALB addresses/LCUs, EC2 surplus CPU credits, retained disks/snapshots or delayed teardown add charges. At this baseline alone, 24 hours is about $7.19 and 730 hours about $218.63, before usage/tax. This is not free-tier infrastructure.

Primary pricing references: https://aws.amazon.com/eks/pricing/ , https://aws.amazon.com/ec2/pricing/on-demand/ , https://aws.amazon.com/vpc/pricing/ , https://aws.amazon.com/elasticloadbalancing/pricing/ , https://aws.amazon.com/ebs/pricing/ , https://aws.amazon.com/kms/pricing/ . The JSON contains exact region-specific queried rates, not generic regional examples.

To reproduce a component query, use the explicit source profile, e.g.:

```bash
.tools/aws pricing get-products --service-code AmazonEC2 --region us-east-1 \
  --profile 'Raghavendra Linga' \
  --filters Type=TERM_MATCH,Field=regionCode,Value=ap-south-1 \
            Type=TERM_MATCH,Field=instanceType,Value=t3.medium \
            Type=TERM_MATCH,Field=operatingSystem,Value=Linux \
            Type=TERM_MATCH,Field=tenancy,Value=Shared \
            Type=TERM_MATCH,Field=preInstalledSw,Value=NA \
            Type=TERM_MATCH,Field=capacitystatus,Value=Used
```

## Teardown included in the proposal, only if approved

Save sanitized evidence and synthetic database export first. Remove the app Ingress while LBC is running and wait for ALB/target groups to disappear. Uninstall the app/monitoring; remove **only this project's** PostgreSQL PVC/PV/EBS volume after data-deletion authorization. Remove the controller, review a destroy plan and destroy this Terraform stack. Check NAT gateways, EIPs, load balancers, EC2 workers, retained EBS, logs and KMS pending-deletion state. The unrelated EC2 instance is excluded. See [ordered cleanup](CLEANUP.md).

Approval is requested for creation, the stated demo lifetime/budget, and teardown of this new project's synthetic data **after evidence is saved**. If the user needs a later presentation, agree a different retention deadline/cost before apply. **Current state: NOT APPROVED.**
