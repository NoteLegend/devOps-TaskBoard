#!/usr/bin/env python3
"""Wait for consecutive successful same-origin backend/Ingress checks before CRUD."""
import argparse,json,time,urllib.request
p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('--seconds',type=int,default=120);a=p.parse_args()
end=time.monotonic()+a.seconds
successes=0
while time.monotonic()<end:
    try:
        for path in ['/ready','/api/tasks/stats']:
            with urllib.request.urlopen(a.url.rstrip('/')+path,timeout=5) as r:data=json.load(r)
            assert data.get('status')=='READY' if path=='/ready' else isinstance(data.get('total'),int)
        successes+=1
        if successes==3:
            print('PASSED: same-origin readiness and API routing stable for three consecutive checks')
            break
    except Exception:successes=0
    time.sleep(2)
else:raise SystemExit('FAILED: Ingress/API did not become stable within bounded timeout')
