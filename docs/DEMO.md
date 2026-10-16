# Session 21 demonstration sequence

Follow the instructor’s complete sequence; use real screens/results only. Confirm current blockers in [verification](VERIFICATION.md). Real CI/GHCR and AWS deployment checks are verified in images/. The approved credit-funded run was shut down after all deployment screenshots/evidence were pushed; cleanup passed. Recreating infrastructure requires a new plan/credit-use/lifetime approval.

1. **Application:** open Release Helpdesk at the actual Ingress URL (local alternative http://localhost:3000 is labelled local). Open a synthetic ticket “Release rollback approval”, set priority HIGH and assignee Demo Student. Filter by status/priority, edit to IN_PROGRESS, demonstrate responsive layout and dashboard counts.
2. **API:** open `/docs`; POST, GET, PUT and DELETE `/api/tasks`. GET `/api/tasks/stats` must return statistics, not ID validation error. `python3 scripts/smoke.py http://ACTUAL_HOST` is repeatable evidence.
3. **Database:** `docker compose exec -T postgres psql -U taskboard -d taskboard -c 'SELECT id,title,status,priority,assignee FROM tasks;'` or `kubectl exec -n taskboard taskboard-postgres-0 -- psql -U taskboard -d taskboard -c 'TABLE tasks;'`. Show Alembic revision and persistent data after a normal restart.
4. **Git:** make a small visible help-text change, run its relevant checks, `git add frontend/src/main.jsx && git commit -m "Clarify release ticket triage guidance"`. Do not manufacture ten empty commits; the grading rubric requests at least ten meaningful commits.
5. **CI:** after initial push approval, `git push origin main`; open the actual Actions run and explain test/build → image build/scan → publish → deploy gates. A local test log is not an Actions run.
6. **Docker:** `docker images taskboard-backend` and `docker images taskboard-frontend`; show non-root runtime and multi-stage frontend.
7. **Security:** show both Trivy artifact results. Explain scanning OS/Python/JS packages, severity gating and remaining findings honestly. No ignored unfixed vulnerabilities by default.
8. **Registry:** open actual GHCR package pages and show full commit SHA tags. Verify anonymous pull and deployed images match the same commit.
9. **Terraform:** show network/EKS/IAM/storage files and actual approved plan, region/account, running infrastructure and costs. State the teardown deadline.
10. **Kubernetes:** `kubectl get pods,svc,pvc -n taskboard`; show Ready replicas, bound PostgreSQL PVC and endpoints.
11. **Helm:** `helm list -n taskboard`, `helm history taskboard -n taskboard`; show successful migration Job and explain rollback/schema compatibility.
12. **Ingress:** open application and `/docs` through the actual ALB hostname; show `kubectl get ingress -n taskboard` and matching controller/class.
13. **Autoscaling:** for the measured AWS workload use `python3 scripts/load-in-cluster.py --context arn:aws:eks:ap-south-1:835582727900:cluster/taskboard-eks --seconds 180 --workers 24`, with HPA/Ready replica/CPU observation in a second terminal (see DEPLOYMENT.md). The external alternative follows: `kubectl top pods -n taskboard`; run `URL=http://ACTUAL_HOST/api/tasks scripts/hpa-evidence.sh`. Show actual CPU, before/after replicas and recovery. If not observed, report NOT PASSED and diagnose; do not claim request volume proves scaling.
14. **Monitoring:** use private port-forwards in [deployment](DEPLOYMENT.md). Show Prometheus target UP, increasing request counters and populated Grafana dashboard. Keep credentials off screen.
15. **Failure simulation:** `scripts/troubleshooting.sh`; show isolated `taskboard-troubleshooting` namespace, ImagePullBackOff diagnosis/recovery and mismatched Service selector → empty endpoints → corrected selector → HTTP success. Main deployment stays healthy.
16. **Teardown evidence:** save approved evidence and authorize data deletion, follow [cleanup](CLEANUP.md), record completed destroy and residual-resource checks. The rubric requires teardown evidence.

Capture real screenshots: application desktop/mobile, Swagger CRUD, table, pytest output, Compose stack/images, commit history, Actions gates, Trivy findings, GHCR SHA tags, Terraform plan and AWS VPC/EKS, Pods/Services/PVC/Helm/Ingress, HPA replica increase/recovery, Prometheus Targets and Grafana panels, both failure symptoms/fixes and destroy. Store sanitized screenshots/video under `images/` and command logs under `evidence/logs/` and link exact files in verification. Never capture secret manifests, AWS keys, login codes or Grafana passwords.

## Rehearsal after the approved AWS shutdown

Use the saved real AWS screens, successful pipeline and before/after rollout evidence for cloud stages. Do not rerun provisioning, cloud load or cloud troubleshooting without fresh approval. Reproduce application/API/database locally:

```bash
docker compose up --build -d --wait
python3 scripts/smoke.py http://localhost:3000
# Browser: http://localhost:3000 ; Swagger: http://localhost:8000/docs
docker compose exec -T postgres psql -U taskboard -d taskboard -c 'TABLE tasks;'
# Stop locally, retain database data:
docker compose down
```

[Completed AWS destroy](../images/aws-terraform-destroy-complete.png) and [residual checks](../evidence/logs/aws-cleanup-verification.json) fulfill the technical cleanup evidence. Student presentation/submission still needs to be delivered.
