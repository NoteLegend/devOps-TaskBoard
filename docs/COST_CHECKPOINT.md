# Cloud spending checkpoint — BLOCKED, NOT APPROVED

No billable resources have been created. AWS profile/account, actual Terraform plan, current ap-south-1 prices and demo lifetime remain required before asking for spending approval.

Intended resource budget (verify actual plan): one EKS standard-support control plane; two t3.medium On-Demand workers (fixed two-node capacity); two 20-GiB root disks; one NAT gateway/EIP; public/private networking across two AZs; one ALB with public IPv4 and LCU usage; one 5-GiB encrypted gp3 PostgreSQL volume; logs/KMS; data transfer/NAT processing. Monitoring uses worker capacity with ephemeral Prometheus retention; no RDS is planned.

Required cost calculation: hourly EKS + 2×regional EC2 + NAT + ALB + public IPv4 + prorated EBS/KMS/logs; add measured/assumed NAT GB, ALB LCUs and egress. Multiply by agreed lifetime and show taxes/credits/exclusions. This is **not free-tier infrastructure**. Do not present an unauthenticated placeholder plan or stale generic dollar estimate as approval evidence.

Primary pricing sources to query at checkpoint: https://aws.amazon.com/eks/pricing/ , https://aws.amazon.com/ec2/pricing/on-demand/ , https://aws.amazon.com/vpc/pricing/ , https://aws.amazon.com/elasticloadbalancing/pricing/ , https://aws.amazon.com/ebs/pricing/ . Use AWS Price List API/Calculator for Mumbai instance/storage specifics.

Use [cleanup](CLEANUP.md) to remove Kubernetes-created ALB and authorized retained storage before Terraform destroy. Save evidence first. Agree exact running-until time with the user before leaving cloud infrastructure active.
