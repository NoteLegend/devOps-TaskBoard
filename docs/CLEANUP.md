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
