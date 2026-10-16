# Cleanup and retained data

For the current demo, the user explicitly authorized deleting only this project’s synthetic data/cloud resources **after all deployment screenshots are saved under images/ and pushed to GitHub**. This condition must be verified before deletion. Existing unrelated EC2/local work is excluded. Future runs need their own data-retention/teardown authorization.

## Local

```bash
# Stop application, retain tasks:
docker compose down
# Stop disposable test containers (test DB is tmpfs):
docker compose -f compose.test.yml down
# After local evidence is saved and cluster deletion is authorized:
kind delete cluster --name taskboard-local
```

Do not run `docker compose down -v` unless deletion of the named application data volume is approved. The local kind cluster contains its own PostgreSQL data; deleting it destroys that data. Project tools/dependencies are ignored; keep them for reproducibility or remove only the project-owned directories after review.

## AWS (after approved evidence backup and teardown)

1. Confirm AWS account/profile/region and kube context. Back up PostgreSQL locally using `kubectl exec -n taskboard taskboard-postgres-0 -- pg_dump -U taskboard -d taskboard > PRIVATE_BACKUP_PATH` (keep backups out of git/archive).
2. Delete Ingress **while LBC is still running**: `kubectl delete ingress taskboard -n taskboard`. Wait until its AWS ALB, target groups and managed security groups are gone; do not remove finalizers to hide failed cleanup.
3. `helm uninstall taskboard -n taskboard`; hook Jobs and StatefulSet PVCs can remain, so inspect `kubectl get jobs,pvc -n taskboard`.
4. After explicit data-deletion approval, delete the release PVC(s). The gp3 StorageClass uses **Retain**, so inspect Released PV volume handles and delete only those identified project EBS volumes via AWS after backup. Never delete unrelated volumes.
5. `helm uninstall monitoring -n monitoring`; inspect leftover CRDs, Jobs and dashboard config (CRDs are cluster-scoped and not auto-removed). `helm uninstall aws-load-balancer-controller -n kube-system` only after all project load balancers are deleted.
6. Prepare/review destroy: `terraform -chdir=terraform plan -destroy -out=destroy.tfplan`. After authorization, `terraform -chdir=terraform apply destroy.tfplan`. Record successful completion.
7. Check AWS EKS clusters, project-tagged EC2 workers, ASGs, EBS volumes/snapshots, ELBv2, NAT gateways, EIPs, network interfaces, KMS pending deletion and CloudWatch log groups. Verify project resources are gone or deliberately retained with known ongoing cost. Check Cost Explorer after billing updates. IAM/OIDC sharing must be handled carefully if other projects use the provider.

Do not destroy VPC/EKS before Kubernetes-created ALBs are removed; controller-managed network interfaces can block Terraform deletion. Local Terraform state is private and needed for teardown: preserve it until destroy is verified, then archive it securely outside the submission. Registry images and GitHub repository remain for grading unless separately requested.

The isolated readiness test also retains its own local volume, `taskboard-readiness_readiness-data`, after its containers are removed. It contains only generated test data. After saving the readiness evidence and authorizing its deletion, remove that exact volume with `docker volume rm taskboard-readiness_readiness-data`. The Compose integration test database uses tmpfs and has no retained volume. Never use a global Docker prune to clean this project.

## Current execution gate

Deployment image SHA is recorded separately from the evidence commit. Disable repository `DEPLOY_ENABLED` before the final evidence push and wait for any application deployment run to finish; subsequent documentation/evidence pushes must not race teardown. Verify remote main matches the evidence commit and every images/ file is tracked/pushed. Save the private synthetic DB export outside git. After that gate, remove Ingress/ALB first, detach/delete only the recorded retained database volume, uninstall controllers and apply the reviewed Terraform destroy plan. Post-cleanup screenshots/logs are pushed in a second evidence commit.

## Completed AWS cleanup

**PASSED at 2026-10-16T20:12:57.381709+00:00.** All deployment screenshots/video were pushed and independently checked at commit `8439aa3f1a4d797e48f0d2e279b44f97bf9c7e0c` before deletion ([remote blob-hash proof](../evidence/logs/aws-evidence-before-teardown.json)). The final evidence push also [passed CI with deployment skipped](../evidence/logs/ci-evidence-push-safe.json).

The application/ALB and its target groups were removed while the controller was active. A private synthetic-data export was saved outside git/archive before deleting the 5-GiB retained database disk. The app, monitoring and controller releases were uninstalled, then the reviewed destroy plan completed: **66 Terraform resources destroyed** ([actual transcript](../evidence/logs/aws-terraform-destroy.txt)).

[Actual residual checks](../evidence/logs/aws-cleanup-verification.json) confirm no project EKS cluster, VPC, active workers, Auto Scaling group, ALB/target groups, network interfaces, retained project disks/snapshots, allocated EIP, active NAT, IAM roles/OIDC providers or CloudWatch log group. Terraform state has no remaining resources and `DEPLOY_ENABLED=false`. The historical ALB application URL is shut down. Local Compose/kind data and unrelated EC2 `i-05e7775e28a9a1a1c` remain untouched.

AWS requires a waiting period for KMS deletion. The project key is **disabled / PendingDeletion**, scheduled for **2026-11-16T01:42:25.050000+05:30**. AWS [does not charge for customer-managed keys scheduled for deletion](https://aws.amazon.com/kms/pricing/); see the [mandatory waiting-period documentation](https://docs.aws.amazon.com/kms/latest/cryptographic-details/key-deletion.html). The key is not claimed already physically erased.

The account remains **FREE / ACTIVE**. Credit/billing reports can lag; the final settled debit is not yet known, and the reported balance is not proof of zero usage. No Paid-plan upgrade occurred. Existing unrelated account activity is excluded from this project's cleanup. Review the Billing Console after reports settle without provisioning anything.

Read-only repeat verification (requires authenticated CLI; creates nothing):

```bash
export PATH="$PWD/.tools:$PATH"
export AWS_PROFILE='Raghavendra Linga'
python3 scripts/verify-aws-cleanup.py --account 835582727900
```

Real cleanup screenshots: [destroy completion](../images/aws-terraform-destroy-complete.png), [residual checks](../images/aws-cleanup-residual-checks.png). Future infrastructure recreation requires fresh plan/credit-use/lifetime approval.
