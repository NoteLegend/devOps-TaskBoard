#!/usr/bin/env python3
"""Archive tracked files only, with an explicit credential/build exclusion check."""
import argparse,hashlib,json,subprocess,zipfile,pathlib
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',default='release-helpdesk-submission.zip')
args=parser.parse_args()
files=subprocess.check_output(['git','ls-files','-z']).decode().split('\0')
required={'README.md','docs/REQUIREMENTS.md','docs/USER_SETUP.md','docs/DEPLOYMENT.md','docs/DEMO.md','docs/TROUBLESHOOTING.md','docs/CLEANUP.md','docs/VERIFICATION.md','terraform/.terraform.lock.hcl',
          'application/backend/app/main.py','application/frontend/src/main.jsx',
          'docker/backend.Dockerfile','docker/frontend.Dockerfile','kubernetes/namespace.yaml',
          'security/semgrep.yml','security/gitleaks.toml','gitops/releases/release.yaml',
          '.github/workflows/ci-cd.yml','monitoring/dashboard.json'}
assert required.issubset(set(files)), 'Required handover/lock files must be tracked before packaging'
excluded={'.env','.venv','.tools','.terraform','node_modules','dist','__pycache__','.git'}
for name in filter(None,files):
    path=pathlib.PurePosixPath(name)
    assert not (set(path.parts)&excluded),name
    assert '.tfstate' not in path.name and not path.name.startswith('kubeconfig'),name
    assert not (path.name.startswith('.env') and path.name!='.env.example'),name
    assert not name.endswith(('.tfplan','.pem','.key','.zip')),name
    assert not (name.endswith('.tfvars') and not name.endswith('.example')),name
out=pathlib.Path(args.output).resolve()
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for name in filter(None,files):z.write(name,'final-devops-project/'+name)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    prefix='final-devops-project/'
    manifest=json.loads(z.read(prefix+'images/manifest.json'))
    media={n.removeprefix(prefix) for n in z.namelist() if n.startswith(prefix+'images/') and n.endswith(('.png','.webm'))}
    assert media=={item['file'] for item in manifest},'Every screenshot/video must appear in the manifest'
    for item in manifest:
        assert hashlib.sha256(z.read(prefix+item['file'])).hexdigest()==item['sha256'],item['file']
    print(f'PASSED: {out}; {len(z.namelist())} tracked files; {out.stat().st_size} bytes; excludes secrets/state/dependencies')
