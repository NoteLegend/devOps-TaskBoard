# Implementation decisions

The service uses one reusable Helm chart across local and AWS environments. Source and dependency analysis run before image publication; final images retain the existing Trivy gate. GHCR tags use full source SHAs, and promotion explicitly pins the tested artifact in Git.

Flux reconciles an isolated local Helm release from the public repository. It corrects frontend drift while leaving backend replica ownership to the HPA. Runtime Secrets are created separately. An Nginx config checksum turns release-marker changes into real frontend rollouts.

The repository uses the canonical application/container/Kubernetes/security/GitOps directory layout. Root Compose commands remain convenient, and the archive wraps the source in `final-devops-project/` without duplicated implementations or dependency/state directories.

See [verification](VERIFICATION.md) for actual outcomes, [traceability](REQUIREMENTS.md) for coverage, and [remaining handover](REMAINING.md) for student actions. Historical AWS evidence remains dated and separate from current local verification; no cloud recreation is needed for this work.
