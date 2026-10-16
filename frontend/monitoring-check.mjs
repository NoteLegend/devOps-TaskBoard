import {chromium} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
try {
 const targets=await (await fetch('http://127.0.0.1:9090/api/v1/targets')).json();
 const application=targets.data.activeTargets.filter(t=>t.labels.namespace==='taskboard');
 if(!application.length||application.some(t=>t.health!=='up'))throw Error('Application Prometheus target is not UP');
 fs.writeFileSync('../evidence/logs/prometheus-targets.json',JSON.stringify(application.map(t=>({labels:t.labels,health:t.health,scrapeUrl:t.scrapeUrl,lastError:t.lastError})),null,2));
 const results={};
 for(const q of ['up{namespace="taskboard"}','sum(http_requests_total{namespace="taskboard"})','sum(rate(http_requests_total{namespace="taskboard"}[2m]))','kube_deployment_status_replicas_available{namespace="taskboard",deployment="taskboard-backend"}']){
   const r=await(await fetch(`http://127.0.0.1:9090/api/v1/query?query=${encodeURIComponent(q)}`)).json();
   if(r.status!=='success'||!r.data.result.length)throw Error(`No metric data for ${q}`);
   results[q]=r.data.result;
 }
 fs.writeFileSync('../evidence/logs/prometheus-queries.json',JSON.stringify(results,null,2));
 await page.goto('http://127.0.0.1:9090/targets');
 await page.getByText('taskboard',{exact:false}).first().waitFor();
 await page.screenshot({path:'../evidence/prometheus-targets-local.png',fullPage:true});
 const secret=execFileSync('../.tools/kubectl',['get','secret','monitoring-grafana','-n','monitoring','-o','jsonpath={.data.admin-password}'],{encoding:'utf8'});
 const password=Buffer.from(secret,'base64').toString();
 await page.goto('http://127.0.0.1:3001/login');
 await page.getByLabel('Email or username').fill('admin');
 await page.getByLabel('Password',{exact:true}).fill(password);
 await page.getByRole('button',{name:'Log in',exact:true}).click();
 await page.waitForURL(url=>!url.pathname.includes('/login'));
 await page.goto('http://127.0.0.1:3001/d/taskboard-release');
 await page.getByText('Request rate',{exact:true}).waitFor();
 await page.waitForTimeout(5000);
 await page.screenshot({path:'../evidence/grafana-dashboard-local.png',fullPage:true});
 console.log('PASSED: application Prometheus targets UP, counters and rates populated, authenticated Grafana dashboard rendered; LOCAL cluster');
} finally {await browser.close();}
