#!/usr/bin/env python3
"""Scan tracked working-tree text, including uncommitted changes, with Gitleaks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
report = Path(sys.argv[1]).resolve()
names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=root).decode().split('\0')
with tempfile.TemporaryDirectory(prefix='helpdesk-secret-scan-') as tmp:
    target = Path(tmp)
    for name in filter(None, names):
        source = root / name
        if not source.is_file() or source.is_symlink():
            continue
        data = source.read_bytes()
        if b'\0' in data or len(data) > 2_000_000:
            continue
        try:
            data.decode('utf-8')
        except UnicodeDecodeError:
            continue
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    result = subprocess.run(['gitleaks', 'dir', '--config', str(root/'security/gitleaks.toml'), '--redact', '--no-banner', '--report-format',
                             'json', '--report-path', str(report), '.'], cwd=target)
    if report.exists():
        findings = json.loads(report.read_text())
        for finding in findings:
            finding['File'] = finding['File'].removeprefix(str(target) + '/')
        report.write_text(json.dumps(findings, indent=2) + '\n')
    sys.exit(result.returncode)
