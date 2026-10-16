#!/usr/bin/env python3
"""Create the classroom runtime secret without exposing password in shell arguments/logs."""
import argparse, secrets, subprocess, json, base64
from urllib.parse import quote
p=argparse.ArgumentParser(); p.add_argument('--namespace',default='taskboard'); p.add_argument('--release',default='taskboard'); args=p.parse_args()
name='taskboard-runtime'
exists=subprocess.run(['kubectl','get','secret',name,'-n',args.namespace],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
if exists.returncode==0:
    raise SystemExit('Secret exists; preserved. Rotate it separately with a database password change.')
password=secrets.token_urlsafe(32)
values={'POSTGRES_USER':'taskboard','POSTGRES_PASSWORD':password,'DATABASE_URL':f'postgresql+psycopg://taskboard:{quote(password,safe="")}@{args.release}-postgres:5432/taskboard'}
obj={'apiVersion':'v1','kind':'Secret','metadata':{'name':name,'namespace':args.namespace},'type':'Opaque','data':{k:base64.b64encode(v.encode()).decode() for k,v in values.items()}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(obj).encode(),check=True)
