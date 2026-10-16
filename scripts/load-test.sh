#!/usr/bin/env bash
set -euo pipefail
exec python3 scripts/load-test.py "${URL:-http://localhost:3000/api/tasks}" --seconds "${SECONDS_LIMIT:-180}" --workers "${WORKERS:-12}"
