import {fileURLToPath} from 'node:url';
const evidenceDir = process.env.EVIDENCE_DIR || fileURLToPath(new URL('../../evidence/', import.meta.url));
import {chromium} from '@playwright/test';
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
try {
 for(const [name,url] of [
  ['ci-security-release',process.env.CI_RUN_URL||'https://github.com/NoteLegend/devOps-TaskBoard/actions/runs/39583131700'],
  ['ghcr-backend','https://github.com/users/NoteLegend/packages/container/package/devops-taskboard-backend'],
  ['ghcr-frontend','https://github.com/users/NoteLegend/packages/container/package/devops-taskboard-frontend'],
  ['git-history','https://github.com/NoteLegend/devOps-TaskBoard/commits/main/']
 ]) {
  const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});
  if(response.status()!==200)throw Error(`${url}: ${response.status()}`);
  await page.waitForTimeout(4000);
  await page.screenshot({path:`${evidenceDir}/${name}.png`,fullPage:true});
  console.log('CAPTURED',response.status(),url);
 }
} finally {await browser.close();}
