#!/usr/bin/env python3
"""Bounded HTTP load; request counts are not proof of HPA scaling."""
import argparse,concurrent.futures,time,urllib.request,urllib.parse
p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('--seconds',type=int,default=180);p.add_argument('--workers',type=int,default=12);a=p.parse_args()
assert 1<=a.seconds<=300 and 1<=a.workers<=32, 'Bounds: 300s, 32 workers'
u=urllib.parse.urlparse(a.url)
assert u.scheme in ('http','https') and u.path.startswith('/api/tasks'), 'Use your project tasks endpoint'
end=time.monotonic()+a.seconds
start=time.monotonic()
def worker(_):
    good=bad=0
    while time.monotonic()<end:
        try:
            with urllib.request.urlopen(a.url,timeout=5) as r:r.read();good+=r.status==200
        except Exception:bad+=1
    return good,bad
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool: results=list(pool.map(worker,range(a.workers)))
print({'duration_seconds':round(time.monotonic()-start,1),'workers':a.workers,'ok':sum(x[0] for x in results),'failed':sum(x[1] for x in results)})
