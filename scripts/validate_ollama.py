"""Run real local inference through the running PromiseTrap API. Not a mock."""
import argparse
import io
import sys
import time
from pathlib import Path
import httpx

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',default='gemma3:4b')
    parser.add_argument('--vision',action='store_true')
    parser.add_argument('--provider',choices=['ollama','gemma'],default='ollama')
    args=parser.parse_args()
    client=httpx.Client(base_url='http://127.0.0.1:8000/api/v1',timeout=20,trust_env=False)
    def post(path,**kwargs):
        r=client.post(path,**kwargs);r.raise_for_status();return r.json()
    case=post('/investigations',json={'title':'Live '+args.provider+' validation'+(' · image evidence' if args.vision else ' · text evidence'),'description':'Synthetic evidence processed with actual '+args.provider+' inference, not authored output.'})
    cid=case['id']
    root=Path(__file__).resolve().parents[1]
    if args.vision:
        from PIL import Image,ImageDraw,ImageFont
        image=Image.new('RGB',(1100,760),'#ece6d8')
        draw=ImageDraw.Draw(image)
        try:
            large=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',44)
            small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
        except OSError:
            large=ImageFont.load_default(size=44);small=ImageFont.load_default(size=30)
        draw.text((65,60),'SYNTHETIC TEST EVIDENCE',font=small,fill='#786445')
        draw.text((65,140),'Launchpad Fellowship',font=large,fill='#242620')
        draw.multiline_text((65,260),'Free registration.\nINR 20,000 fixed monthly stipend.\nGuaranteed certificate.\nOpen to undergraduate students.',font=large,fill='#242620',spacing=28)
        data=io.BytesIO();image.save(data,format='PNG')
        post('/investigations/'+cid+'/sources',files={'files':('synthetic-advertisement.png',data.getvalue(),'image/png')})
    else:
        text=(root/'examples/internship-case/advertisement.txt').read_text(encoding='utf-8')
        post('/investigations/'+cid+'/sources/text',json={'filename':'advertisement.txt','text':text})
    for filename in ['registration.txt','offer.txt']:
        post('/investigations/'+cid+'/sources/text',json={'filename':filename,'text':(root/'examples/internship-case'/filename).read_text(encoding='utf-8')})
    post('/investigations/'+cid+'/analyze',json={'provider':args.provider,'model':args.model if args.provider=='ollama' else None})
    print('Started REAL inference:',cid,args.provider,args.model if args.provider=='ollama' else 'configured Gemma 4',flush=True)
    last=None
    deadline=time.monotonic()+900
    while time.monotonic()<deadline:
        r=client.get('/investigations/'+cid);r.raise_for_status();case=r.json()
        if case['stage']!=last:
            print(case['stage'],flush=True);last=case['stage']
        if case['status']!='processing':
            print('Status:',case['status'],'Model:',case['model_identifier'],flush=True)
            print('Claims:',len(case['claims']),'Findings:',len(case['findings']),flush=True)
            for f in case['findings']:
                print(f['status'],':',f['title'],'(text verified:',f['evidence_verified'],')',flush=True)
            if case.get('error_message'):
                print(case['error_message'],flush=True)
            for source in case['sources']:
                count=sum(c['source_id']==source['id'] for c in case['claims'])
                print(source['filename'],':',count,'claims;',source['extraction_status'],flush=True)
            if case['status']=='failed' or not case['claims']:
                return 1
            if args.vision and not any(c['source_id']==case['sources'][0]['id'] for c in case['claims']):
                print('Image extraction did not return claims',flush=True)
                return 1
            for fmt in ['json','markdown','pdf']:
                r=client.get('/investigations/'+cid+'/report',params={'format':fmt});r.raise_for_status()
                print('Export verified:',fmt,len(r.content),'bytes',flush=True)
            return 0
        time.sleep(2)
    print('Validation timed out; persisted investigation is available for inspection.',flush=True)
    return 1

if __name__=='__main__':
    sys.exit(main())
