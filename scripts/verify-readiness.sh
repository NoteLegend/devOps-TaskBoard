#!/usr/bin/env bash
set -euo pipefail
C=(docker compose -f compose.readiness.yml)
"${C[@]}" up -d --wait
"${C[@]}" exec -T backend python -c "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:8000/ready').status==200; print('Initial ready: 200')"
"${C[@]}" stop postgres
"${C[@]}" exec -T backend python - <<'PY'
import urllib.request, urllib.error
try:
    urllib.request.urlopen('http://127.0.0.1:8000/ready',timeout=10)
except urllib.error.HTTPError as e:
    assert e.code==503
    assert b'Database temporarily unavailable' in e.read()
    print('Database stopped: readiness 503, sanitized error')
else:
    raise AssertionError('Readiness succeeded without database')
assert urllib.request.urlopen('http://127.0.0.1:8000/health').status==200
print('Liveness remains 200')
PY
"${C[@]}" start postgres
"${C[@]}" exec -T backend python - <<'PY'
import time,urllib.request
for _ in range(30):
    try:
        assert urllib.request.urlopen('http://127.0.0.1:8000/ready',timeout=5).status==200
        print('PASSED: database recovered; readiness 200')
        break
    except Exception:time.sleep(1)
else:raise AssertionError('Readiness did not recover')
PY
"${C[@]}" down
