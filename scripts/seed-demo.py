#!/usr/bin/env python3
"""Add clearly synthetic helpdesk tickets, skipping titles already present."""
import json,sys,urllib.request
base=(sys.argv[1] if len(sys.argv)>1 else 'http://localhost:3000').rstrip('/')+'/api/tasks'
with urllib.request.urlopen(base) as r:titles={x['title'] for x in json.load(r)}
for title,description,priority,status,assignee in [
 ('[Demo] Deployment readiness probe failing','Investigate the release API database connection.','HIGH','IN_PROGRESS','Demo Engineer'),
 ('[Demo] Request staging namespace access','Review namespace RBAC for the release team.','MEDIUM','TODO','Demo Operator'),
 ('[Demo] Verify rollback runbook','Record the release revision and rehearse recovery.','HIGH','TODO','Demo Student'),
 ('[Demo] Confirm metrics scrape recovery','Validate the Prometheus target after the service repair.','LOW','DONE','Demo Engineer')]:
 if title in titles:continue
 data=dict(title=title,description=description,priority=priority,status=status,assignee=assignee)
 req=urllib.request.Request(base,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req) as r:assert r.status==201
print('PASSED: synthetic helpdesk demo tickets available')
