#!/usr/bin/env python3
"""Read-only deployment guard. Never upgrades an account or creates resources."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--account', required=True, help='Agreed 12-digit AWS account')
    parser.add_argument('--minimum-credits', type=float, default=20.0)
    args = parser.parse_args()
    aws = shutil.which('aws')
    if not aws:
        local = Path(__file__).resolve().parents[1] / '.tools/aws'
        if local.exists():
            aws = str(local)
    if not aws:
        raise RuntimeError('AWS CLI is required; no resources were created')
    result = subprocess.run(
        [aws, 'freetier', 'get-account-plan-state', '--region', 'us-east-1',
         '--output', 'json', '--no-cli-pager'],
        check=True, text=True, capture_output=True,
    )
    state = json.loads(result.stdout)
    if state.get('accountId') != args.account:
        raise RuntimeError('Wrong AWS account; refusing deployment')
    if (state.get('accountPlanType'), state.get('accountPlanStatus')) != ('FREE', 'ACTIVE'):
        raise RuntimeError('An ACTIVE FREE account plan is required; no upgrade is authorized')
    credit = state.get('accountPlanRemainingCredits', {})
    if credit.get('unit') != 'USD' or credit.get('amount', 0) < args.minimum_credits:
        raise RuntimeError('Insufficient verified credits; refusing deployment')
    expiration = datetime.datetime.fromisoformat(state['accountPlanExpirationDate'].replace('Z', '+00:00'))
    if expiration - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(hours=4):
        raise RuntimeError('Free plan expires too soon for the demo and cleanup')
    print(json.dumps({'captured_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      'result': 'PASSED', 'account': args.account, 'plan': 'FREE',
                      'status': 'ACTIVE', 'remaining_credits_usd': credit['amount'],
                      'expires_at': expiration.isoformat(),
                      'note': 'Read-only guard; credits are consumed by usage. No account upgrade performed.'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, ValueError, KeyError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        sys.exit(1)
