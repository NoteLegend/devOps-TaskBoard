#!/usr/bin/env python3
"""Verify Flux convergence and automatic drift correction on the local application."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
import urllib.request

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--context', default='kind-taskboard-local')
p.add_argument('--expect-marker', default='gitops-v1')
p.add_argument('--port', type=int, default=8099)
p.add_argument('--output', default='evidence/logs/gitops-final')
args = p.parse_args()
if not args.context.startswith('kind-'):
    p.error('Only a local kind context is supported for this controlled drift exercise.')
out = Path(args.output)
out.mkdir(parents=True, exist_ok=True)
k = ['kubectl', '--context', args.context]
ns = 'release-helpdesk-gitops'

def run(*parts):
    return subprocess.check_output(k + list(parts), text=True)

def obj(*parts):
    return json.loads(run(*parts, '-o', 'json'))

def wait_for(check, label, seconds=240):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = check()
        if result:
            return result
        time.sleep(3)
    raise RuntimeError('Timed out waiting for ' + label)

before = obj('get', 'deployment', 'release-helpdesk-frontend', '-n', ns)
assert before['spec']['replicas'] == 2, 'Expected Git-owned frontend replica count of two'
hr = obj('get', 'helmrelease', 'release-helpdesk', '-n', ns)
assert any(c['type'] == 'Ready' and c['status'] == 'True' for c in hr['status']['conditions'])
(out/'frontend-before.json').write_text(json.dumps(before, indent=2)+'\n')
started = time.monotonic()
run('scale', 'deployment/release-helpdesk-frontend', '-n', ns, '--replicas=1')
drift = obj('get', 'deployment', 'release-helpdesk-frontend', '-n', ns)
assert drift['spec']['replicas'] == 1, 'The controlled manual drift was not observed'
(out/'frontend-drift.json').write_text(json.dumps(drift, indent=2)+'\n')

def recovered():
    deployment = obj('get', 'deployment', 'release-helpdesk-frontend', '-n', ns)
    return deployment if deployment['spec']['replicas'] == 2 and deployment.get('status', {}).get('availableReplicas', 0) == 2 else None

# No flux reconcile, Helm upgrade or kubectl apply here: the controller must act.
after = wait_for(recovered, 'automatic replica drift correction')
elapsed = round(time.monotonic()-started, 1)
(out/'frontend-recovered.json').write_text(json.dumps(after, indent=2)+'\n')
source = obj('get', 'gitrepository', 'release-helpdesk', '-n', 'flux-system')
ks = obj('get', 'kustomization', 'release-helpdesk', '-n', 'flux-system')
hr = obj('get', 'helmrelease', 'release-helpdesk', '-n', ns)
for name, value in [('source', source), ('kustomization', ks), ('helmrelease', hr)]:
    (out/f'{name}.json').write_text(json.dumps(value, indent=2)+'\n')
(out/'events.txt').write_text(run('get', 'events', '-n', ns, '--sort-by=.lastTimestamp'))
(out/'resources.txt').write_text(run('get', 'pods,svc,cm,pvc,hpa', '-n', ns))
with (out/'port-forward.log').open('w') as log:
    process = subprocess.Popen(k + ['port-forward', '-n', ns, 'svc/release-helpdesk-frontend', f'{args.port}:8080'], stdout=log, stderr=log)
    try:
        url = f'http://127.0.0.1:{args.port}'
        def ready():
            try:
                with urllib.request.urlopen(url+'/ready', timeout=4) as response:
                    return response.status == 200
            except (OSError, ValueError):
                return False
        wait_for(ready, 'same-origin API readiness', 60)
        with urllib.request.urlopen(url, timeout=5) as response:
            marker = response.headers.get('X-Release-Version')
            assert marker == args.expect_marker, (marker, args.expect_marker)
        subprocess.run(['python3', 'scripts/smoke.py', url], check=True, stdout=(out/'http-smoke.txt').open('w'))
    finally:
        process.terminate()
        process.wait(timeout=10)
summary = {
    'result': 'PASSED', 'captured_at_utc': datetime.now(timezone.utc).isoformat(),
    'context': args.context, 'application': 'Release Helpdesk', 'namespace': ns,
    'source_revision': source['status']['artifact']['revision'],
    'kustomization_revision': ks['status']['lastAppliedRevision'],
    'helm_ready': True, 'manual_frontend_replicas': [2, 1],
    'automatically_recovered_replicas': 2, 'drift_recovery_seconds': elapsed,
    'forced_reconcile': False, 'http_marker': marker, 'same_origin_crud': 'PASSED',
    'hpa_replica_ownership': 'backend replicas excluded; frontend replicas owned by Git',
}
(out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
