#!/usr/bin/env python3
"""Compare the running GitOps Pod image IDs with public GHCR manifests."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import urllib.parse
import urllib.request

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--context', default='kind-taskboard-local')
p.add_argument('--output', default='evidence/logs/gitops-final/image-identity.json')
args = p.parse_args()
results = []
for component in ['backend', 'frontend']:
    pods = json.loads(subprocess.check_output([
        'kubectl', '--context', args.context, 'get', 'pods', '-n', 'release-helpdesk-gitops',
        '-l', 'app=release-helpdesk-'+component, '-o', 'json'], text=True))['items']
    assert pods, component + ' has no Pods'
    image = pods[0]['spec']['containers'][0]['image']
    assert image.startswith('ghcr.io/notelegend/devops-taskboard-'), image
    repository, tag = image.removeprefix('ghcr.io/').rsplit(':', 1)
    assert len(tag) == 40 and all(c in '0123456789abcdef' for c in tag)
    query = urllib.parse.urlencode({'service': 'ghcr.io', 'scope': f'repository:{repository}:pull'})
    with urllib.request.urlopen('https://ghcr.io/token?'+query, timeout=20) as r:
        token = json.load(r)['token']
    headers = {'Authorization': 'Bearer '+token,
               'Accept': ', '.join(['application/vnd.oci.image.index.v1+json',
                                    'application/vnd.oci.image.manifest.v1+json',
                                    'application/vnd.docker.distribution.manifest.list.v2+json',
                                    'application/vnd.docker.distribution.manifest.v2+json'])}
    with urllib.request.urlopen(urllib.request.Request(f'https://ghcr.io/v2/{repository}/manifests/{tag}', headers=headers), timeout=20) as r:
        digest = r.headers['Docker-Content-Digest']
        manifest = json.load(r)
    if 'manifests' in manifest:
        digest = next(m['digest'] for m in manifest['manifests']
                      if m.get('platform', {}).get('os') == 'linux' and m.get('platform', {}).get('architecture') == 'amd64')
    ids = [p['status']['containerStatuses'][0]['imageID'] for p in pods]
    assert all(v.endswith(digest) for v in ids), (component, digest, ids)
    results.append({'component': component, 'image': image, 'registry_digest': digest,
                    'pod_image_ids': ids, 'result': 'MATCH'})
summary = {'result': 'PASSED', 'captured_at_utc': datetime.now(timezone.utc).isoformat(),
           'context': args.context, 'images': results}
Path(args.output).write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
