#!/usr/bin/env python3
"""Bounded in-cluster HTTP client; its CPU is separate from the backend HPA."""
import argparse,datetime,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--context',required=True,help='Explicit agreed Kubernetes context')
p.add_argument('--namespace',default='taskboard-loadtest')
p.add_argument('--seconds',type=int,default=180)
p.add_argument('--workers',type=int,default=24)
args=p.parse_args()
if not 1<=args.seconds<=180 or not 1<=args.workers<=24:p.error('Bounds: 180 seconds and 24 workers maximum')
if not re.fullmatch(r'taskboard-[a-z0-9-]+',args.namespace):p.error('Use a dedicated taskboard-* load-test namespace')
context=args.context;k=['kubectl','--context',context];ns=args.namespace
current=subprocess.check_output(['kubectl','config','current-context'],text=True).strip()
if current!=context:raise SystemExit('Select the agreed context explicitly before starting load')
job_name='bounded-load-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
namespace={'apiVersion':'v1','kind':'Namespace','metadata':{'name':ns}}
subprocess.run(k+['apply','-f','-'],input=json.dumps(namespace).encode(),check=True)
cm=json.loads(subprocess.check_output(k+['create','configmap',job_name,'-n',ns,'--from-file=load-test.py='+str(Path(__file__).with_name('load-test.py')),'--dry-run=client','-o','json']))
subprocess.run(k+['apply','-f','-'],input=json.dumps(cm).encode(),check=True)
image=subprocess.check_output(k+['get','deployment','taskboard-backend','-n','taskboard','-o','jsonpath={.spec.template.spec.containers[0].image}'],text=True)
url='http://taskboard-backend.taskboard.svc.cluster.local:8000/api/tasks'
job={'apiVersion':'batch/v1','kind':'Job','metadata':{'name':job_name,'namespace':ns},'spec':{'activeDeadlineSeconds':args.seconds+60,'backoffLimit':0,'ttlSecondsAfterFinished':3600,'template':{'metadata':{'labels':{'app':'taskboard-load-generator'}},'spec':{'restartPolicy':'Never','automountServiceAccountToken':False,'securityContext':{'runAsNonRoot':True,'runAsUser':10001,'seccompProfile':{'type':'RuntimeDefault'}},'containers':[{'name':'load','image':image,'command':['python','/load/load-test.py',url,'--seconds',str(args.seconds),'--workers',str(args.workers)],'resources':{'requests':{'cpu':'500m','memory':'64Mi'},'limits':{'cpu':'1000m','memory':'128Mi'}},'securityContext':{'allowPrivilegeEscalation':False,'capabilities':{'drop':['ALL']}},'volumeMounts':[{'name':'script','mountPath':'/load','readOnly':True}]}],'volumes':[{'name':'script','configMap':{'name':job_name}}]}}}}
subprocess.run(k+['apply','-f','-'],input=json.dumps(job).encode(),check=True)

subprocess.run(k+['wait','-n',ns,'--for=condition=Complete','job/'+job_name,'--timeout='+str(args.seconds+90)+'s'],check=True)
subprocess.run(k+['logs','-n',ns,'job/'+job_name],check=True)
print('Record CPU and actual Ready replicas; request count alone is not scaling evidence.')
print('Job/config-map evidence namespace:',ns,'job:',job_name)
