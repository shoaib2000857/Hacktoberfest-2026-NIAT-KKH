"""Separately identified LIVE multimodal test. Requires running API and a real key."""
import argparse
import json
import sys
import time
from pathlib import Path
import httpx

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--scenario',choices=['internship','scholarship','optional','deadline'],default='internship')
    parser.add_argument('--output',type=Path,help='Save the actual response (may contain source text) locally.')
    args=parser.parse_args()
    with httpx.Client(base_url='http://127.0.0.1:8000/api/v1',timeout=20,trust_env=False) as client:
        health=client.get('/health');health.raise_for_status()
        if not health.json()['gemma_configured']:
            print('LIVE GEMMA NOT RUN: configure GEMINI_API_KEY in backend .env, then restart. No fallback.')
            return 1
        r=client.post('/examples/advanced/'+args.scenario,params={'images':'true'});r.raise_for_status();cid=r.json()['id']
        r=client.post('/investigations/'+cid+'/analyze',json={'provider':'gemma'});r.raise_for_status()
        print('Actual Gemma 4 image inference started:',cid,flush=True)
        deadline=time.monotonic()+900;stage=None
        while time.monotonic()<deadline:
            r=client.get('/investigations/'+cid);r.raise_for_status();case=r.json()
            if stage!=case['stage']:
                stage=case['stage'];print(stage,flush=True)
            if case['status']!='processing':
                print('Actual model:',case['model_identifier'],'status:',case['status'],'claims:',len(case['claims']),'findings:',len(case['findings']),flush=True)
                print('Image quotations require visual review; compare every excerpt with its source. A smoke response alone does not establish extraction accuracy.')
                if args.output:
                    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(case,indent=2)+'\n')
                if case.get('error_message'):print(case['error_message'])
                return 0 if case['status']=='completed' and case['claims'] and str(case['model_identifier']).startswith('gemma-4-') else 1
            time.sleep(2)
        print('Live evaluation timed out; the persisted case is available for inspection.')
        return 1

if __name__=='__main__':
    try:sys.exit(main())
    except httpx.HTTPError as exc:
        print('Live validation failed:',type(exc).__name__)
        sys.exit(1)
