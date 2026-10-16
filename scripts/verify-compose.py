#!/usr/bin/env python3
import json,subprocess,time,urllib.request
base='http://127.0.0.1:3000'
def request(path,method='GET',data=None):
    r=urllib.request.Request(base+path,method=method,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(r,timeout=10) as response:return json.load(response)
ticket=request('/api/tasks','POST',{'title':'Synthetic persistence verification','assignee':'Demo Student'})
subprocess.run(['docker','compose','restart'],check=True)
for _ in range(60):
    try:
        assert request(f"/api/tasks/{ticket['id']}")['title']==ticket['title']
        break
    except Exception:time.sleep(1)
else:raise AssertionError('Database persistence or recovery failed')
print('PASSED: ticket',ticket['id'],'survived normal full-stack Compose restart')
subprocess.run(['docker','compose','exec','-T','postgres','psql','-U','taskboard','-d','taskboard','-c','SELECT id,title,status,priority,assignee FROM tasks;'],check=True)
# This synthetic persistence ticket is intentionally retained as visible demo data.
