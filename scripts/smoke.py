#!/usr/bin/env python3
"""Synthetic CRUD via the same origin used by the browser; cleans up its own task."""
import json,sys,urllib.request,urllib.error
base=(sys.argv[1] if len(sys.argv)>1 else 'http://localhost:3000').rstrip('/')
def request(path, method='GET', data=None):
    req=urllib.request.Request(base+path,method=method,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=10) as r:
        return r.status,json.loads(r.read()) if r.status!=204 else None
assert request('/health')[1]['status']=='UP'
assert request('/ready')[1]['status']=='READY'
status,t=request('/api/tasks','POST',{'title':'Synthetic smoke task','assignee':'Demo Student','priority':'HIGH'})
assert status==201
try:
    path=f"/api/tasks/{t['id']}"
    assert request(path)[1]['title']=='Synthetic smoke task'
    assert request(path,'PUT',{'status':'DONE'})[1]['status']=='DONE'
    assert request('/api/tasks/stats')[1]['done']>=1
    assert any(x['id']==t['id'] for x in request('/api/tasks')[1])
finally:
    assert request(f"/api/tasks/{t['id']}",'DELETE')[0]==204
try: request(path)
except urllib.error.HTTPError as e: assert e.code==404
else: raise AssertionError('Deleted task still exists')
print('PASSED: same-origin health, readiness, create, read, update, statistics, list, delete, 404')
