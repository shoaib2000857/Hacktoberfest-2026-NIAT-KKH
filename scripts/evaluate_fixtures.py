"""Offline release evaluation: real API + PromiseGraph, authored claims, no inference."""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'apps'/'api'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='promisetrap-evaluation-') as directory:
        os.environ['PROMISETRAP_DATA_DIR']=directory
        from fastapi.testclient import TestClient
        from app.main import app
        expected=json.loads((ROOT/'examples'/'advanced'/'expected.json').read_text())
        rows=[]
        with TestClient(app) as client:
            for name,target in expected.items():
                response=client.post('/api/v1/examples/advanced/'+name)
                response.raise_for_status();case=response.json()
                actual=sorted(f['status'] for f in case['findings'])
                row={'scenario':name,'claims':len(case['claims']),'expected':sorted(target['expected']),'actual':actual,'passed':actual==sorted(target['expected']) and len(case['claims'])==target['claims'],'financial':case['financial']['currencies'],'model':'Authored fixture; no model inference'}
                rows.append(row)
        report={'method':'Real FastAPI routes and PromiseGraph, authored fictional claims. No Google or Ollama request.','scenarios':rows}
        text=json.dumps(report,indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text+'\n')
        print(text)
        return 0 if all(r['passed'] for r in rows) else 1

if __name__=='__main__':sys.exit(main())
