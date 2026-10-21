#!/usr/bin/env bash
# The same source/dependency/secret gates run locally and in GitHub Actions.
set -euo pipefail
cd "$(dirname "$0")/.."
stage=${1:-all}
report_dir=${SECURITY_REPORT_DIR:-evidence/logs/security-final}
mkdir -p "$report_dir"
run_sast() {
  bandit -r application/backend/app application/backend/alembic -f json -o "$report_dir/bandit.json"
  semgrep scan --config security/semgrep.yml --metrics=off --disable-version-check \
    --error --json --output "$report_dir/semgrep.json" application/frontend/src
}
run_sca() {
  # The complete pinned dependency set is audited, including build/test packages.
  pip-audit -r application/backend/requirements.txt --no-deps --disable-pip \
    --format json --output "$report_dir/pip-audit.json"
  (cd application/frontend && npm audit --audit-level=low --json) > "$report_dir/npm-audit.json"
}
run_secrets() {
  # CI checks out full history. Scan tracked working files as well, without
  # touching ignored .env files, local tooling, caches or private exports.
  gitleaks git --config security/gitleaks.toml --redact --no-banner --report-format json \
    --report-path "$report_dir/gitleaks-history.json" --log-opts='--all' .
  python3 scripts/scan-tracked-secrets.py "$report_dir/gitleaks-working-tree.json"
}
case "$stage" in
  sast) run_sast ;;
  sca) run_sca ;;
  secrets) run_secrets ;;
  all) run_sast; run_sca; run_secrets ;;
  *) echo 'Usage: scripts/security-scan.sh [all|sast|sca|secrets]' >&2; exit 2 ;;
esac
echo "PASS: $stage gates; reports in $report_dir"
