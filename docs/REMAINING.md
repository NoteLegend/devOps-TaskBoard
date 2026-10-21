# Final handover

Engineering work is implemented in this repository: source/dependency/secret gates, image scanning, canonical layout and Flux reconciliation are included alongside the original cloud lifecycle. [Executed verification](VERIFICATION.md) records the actual revisions and outcomes.

The remaining student actions are:

1. Record the narrated walkthrough using the updated [presentation and speaker guide](../presentation/README.md). Demonstrate the current local application/GitOps instance and clearly label the saved AWS screens as the earlier deployment, which was subsequently removed.
2. Submit the public repository URL, source archive, recording and presentation in the instructor's requested locations. `python3 scripts/package-submission.py` produces a checked ZIP with the complete `final-devops-project/` structure.
3. If necessary, inspect settled billing for the earlier approved cloud run. Reporting can lag; the KMS key deletion window and historical residual checks are documented in [cleanup](CLEANUP.md).

No AWS recreation is required to review or narrate the preserved evidence. Keep `DEPLOY_ENABLED=false` after teardown. The root/component READMEs describe the product; [requirement traceability](REQUIREMENTS.md) is kept separately for review. A final grade depends on evaluation and the delivered recording; passing checks is not a guaranteed score.
