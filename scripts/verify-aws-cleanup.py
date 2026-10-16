#!/usr/bin/env python3
"""Read-only checks of the exact resources recorded for this capstone demo.

Run after Terraform destroy. AWS credentials stay in the normal CLI provider.
This deliberately does not query the billable Cost Explorer API.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--account', required=True)
    parser.add_argument('--region', default='ap-south-1')
    parser.add_argument('--inventory', default='evidence/logs/aws-cleanup-plan-inventory.json')
    parser.add_argument('--output', default='evidence/logs/aws-cleanup-verification.json')
    args = parser.parse_args()
    aws = shutil.which('aws') or str(Path('.tools/aws').resolve())

    def call(*command, absent=()):
        result = subprocess.run([aws, '--region', args.region, '--output', 'json',
                                 '--no-cli-pager', *command], capture_output=True, text=True)
        if result.returncode:
            if any(f'({code})' in result.stderr for code in absent):
                return None
            raise RuntimeError(f'{command[0]} {command[1]} failed: {result.stderr.strip()}')
        return json.loads(result.stdout or '{}')

    identity = call('sts', 'get-caller-identity')
    inventory = json.loads(Path(args.inventory).read_text())
    assert identity['Account'] == args.account == inventory['account'], 'Wrong account'
    resources = inventory['resources']

    def resource_id(kind):
        matches = [r['id'] for r in resources if r['type'] == kind]
        assert len(matches) == 1, (kind, matches)
        return matches[0]

    vpc = resource_id('aws_vpc')
    cluster = resource_id('aws_eks_cluster')
    workers = json.loads(Path('evidence/logs/aws-worker-instances.json').read_text())
    volumes = sorted({d['Ebs']['VolumeId'] for w in workers for d in w['Devices']})
    checks = []

    def record(name, passed, detail):
        checks.append({'check': name, 'result': 'PASSED' if passed else 'FAILED', 'observed': detail})

    def check_cluster():
        value = call('eks', 'describe-cluster', '--name', cluster, absent=('ResourceNotFoundException',))
        return ('EKS cluster absent', value is None, None if value is None else value['cluster']['status'])

    def check_vpc():
        value = call('ec2', 'describe-vpcs', '--filters', f'Name=vpc-id,Values={vpc}')['Vpcs']
        return ('VPC absent', not value, [v['VpcId'] for v in value])

    def check_workers():
        value = call('ec2', 'describe-instances', '--instance-ids', *[w['InstanceId'] for w in workers],
                     absent=('InvalidInstanceID.NotFound',))
        states = [] if value is None else [{'id': i['InstanceId'], 'state': i['State']['Name']}
                    for r in value['Reservations'] for i in r['Instances']]
        return ('Project workers terminated', all(i['state'] == 'terminated' for i in states), states)

    def check_volume(volume):
        value = call('ec2', 'describe-volumes', '--volume-ids', volume, absent=('InvalidVolume.NotFound',))
        return (f'EBS volume {volume} deleted', value is None, None if value is None else value['Volumes'][0]['State'])

    def check_snapshots():
        value = call('ec2', 'describe-snapshots', '--owner-ids', 'self', '--filters',
                     'Name=volume-id,Values=' + ','.join(volumes))['Snapshots']
        return ('No retained snapshots of project volumes', not value, [v['SnapshotId'] for v in value])

    def check_nat():
        value = call('ec2', 'describe-nat-gateways', '--filter', f'Name=vpc-id,Values={vpc}')['NatGateways']
        states = [{'id': n['NatGatewayId'], 'state': n['State']} for n in value]
        return ('NAT gateways deleted', all(n['state'] == 'deleted' for n in states), states)

    def check_eip():
        value = call('ec2', 'describe-addresses', '--allocation-ids', resource_id('aws_eip'),
                     absent=('InvalidAllocationID.NotFound',))
        return ('Elastic IP released', value is None, None if value is None else 'still allocated')

    def check_elb(kind, key):
        value = call('elbv2', f'describe-{kind}')[key]
        owned = [v.get('LoadBalancerArn', v.get('TargetGroupArn')) for v in value if v.get('VpcId') == vpc]
        return (f'Project {kind} absent', not owned, owned)

    def check_enis():
        value = call('ec2', 'describe-network-interfaces', '--filters', f'Name=vpc-id,Values={vpc}')['NetworkInterfaces']
        return ('Project network interfaces absent', not value, [v['NetworkInterfaceId'] for v in value])

    def check_asgs():
        groups = call('autoscaling', 'describe-auto-scaling-groups')['AutoScalingGroups']
        subnets = {r['id'] for r in resources if r['type'] == 'aws_subnet'}
        owned = [g['AutoScalingGroupName'] for g in groups if set(g['VPCZoneIdentifier'].split(',')) & subnets]
        return ('Project Auto Scaling groups absent', not owned, owned)

    def check_logs():
        value = call('logs', 'describe-log-groups', '--log-group-name-prefix', f'/aws/eks/{cluster}/cluster')['logGroups']
        owned = [g['logGroupName'] for g in value if g['logGroupName'] == f'/aws/eks/{cluster}/cluster']
        return ('Project CloudWatch log group absent', not owned, owned)

    def check_role(role):
        value = call('iam', 'get-role', '--role-name', role, absent=('NoSuchEntity',))
        return (f'IAM role {role} absent', value is None, None if value is None else 'still exists')

    def check_oidc(arn):
        value = call('iam', 'get-open-id-connect-provider', '--open-id-connect-provider-arn', arn,
                     absent=('NoSuchEntity',))
        return (f'OIDC provider {arn} absent', value is None, None if value is None else 'still exists')

    def check_kms():
        value = call('kms', 'describe-key', '--key-id', inventory['kms_key_id'])['KeyMetadata']
        detail = {k: value[k] for k in ('KeyId', 'KeyState', 'Enabled', 'DeletionDate') if k in value}
        if isinstance(detail.get('DeletionDate'), (int, float)):
            detail['DeletionDate'] = datetime.datetime.fromtimestamp(detail['DeletionDate'], datetime.timezone.utc).isoformat()
        return ('KMS key disabled and scheduled for deletion', value['KeyState'] == 'PendingDeletion' and not value['Enabled'], detail)

    jobs = [check_cluster, check_vpc, check_workers, check_nat, check_eip, check_enis, check_asgs,
            check_logs, check_kms, check_snapshots, lambda: check_elb('load-balancers', 'LoadBalancers'),
            lambda: check_elb('target-groups', 'TargetGroups')]
    jobs += [lambda v=v: check_volume(v) for v in volumes]
    jobs += [lambda r=r: check_role(r['id']) for r in resources if r['type'] == 'aws_iam_role']
    jobs += [lambda r=r: check_oidc(r['id']) for r in resources if r['type'] == 'aws_iam_openid_connect_provider']
    with ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(lambda job: job(), jobs):
            record(*result)

    state = call('freetier', 'get-account-plan-state', '--region', 'us-east-1')
    record('Account remains ACTIVE FREE', (state['accountPlanType'], state['accountPlanStatus']) == ('FREE', 'ACTIVE'),
           {k: state[k] for k in ('accountPlanType', 'accountPlanStatus', 'accountPlanRemainingCredits', 'accountPlanExpirationDate')})
    tf = shutil.which('terraform') or str(Path('.tools/terraform').resolve())
    state_list = subprocess.check_output([tf, '-chdir=terraform', 'state', 'list'], text=True).strip()
    record('Terraform state contains no managed resources', not state_list, state_list.splitlines())
    deploy_flag = subprocess.check_output([str(Path('.tools/gh').resolve()), 'variable', 'get', 'DEPLOY_ENABLED'], text=True).strip()
    record('CI deployment disabled', deploy_flag == 'false', deploy_flag)
    # Verify preservation separately: this machine/account had this preexisting instance.
    other = call('ec2', 'describe-instances', '--instance-ids', 'i-05e7775e28a9a1a1c')
    preserved = other['Reservations'][0]['Instances'][0]
    record('Unrelated preexisting EC2 left running', preserved['State']['Name'] == 'running',
           {'id': preserved['InstanceId'], 'type': preserved['InstanceType'], 'state': preserved['State']['Name']})
    summary = {'result': 'PASSED' if all(c['result'] == 'PASSED' for c in checks) else 'FAILED',
               'captured_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'account': args.account, 'region': args.region, 'scope': {'vpc': vpc, 'cluster': cluster},
               'checks': checks,
               'billing_note': 'Credit and billing reports can lag. No Paid-plan upgrade performed. KMS scheduled-deletion keys are not charged; final billing is not yet settled. Unrelated existing resources are outside this cleanup.'}
    Path(args.output).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 0 if summary['result'] == 'PASSED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
