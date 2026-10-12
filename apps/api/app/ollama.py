"""Explicit local validation provider. Never reported as Gemma 4 cloud inference."""
import base64
import os
from urllib.parse import urlparse
import httpx
from promisegraph.schemas import Extraction
from .gemma import GemmaClient, SYSTEM

def base_url():
    url=os.getenv('OLLAMA_BASE_URL','http://127.0.0.1:11434').rstrip('/')
    parsed=urlparse(url)
    if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost','::1') or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise RuntimeError('OLLAMA_BASE_URL must be an HTTP loopback address without credentials or paths.')
    return url

def installed_models():
    try:
        r=httpx.get(base_url()+'/api/tags',timeout=2,trust_env=False)
        r.raise_for_status()
        return [{'name':m['name'],'capabilities':m.get('capabilities',[])} for m in r.json().get('models',[]) if 'embedding' not in m.get('capabilities',[]) or 'completion' in m.get('capabilities',[])]
    except (httpx.HTTPError,RuntimeError,ValueError):
        return []

class OllamaClient(GemmaClient):
    def __init__(self,model=None):
        self.url=base_url()
        self.model_name=model or os.getenv('OLLAMA_MODEL','gemma3:4b')
        if not self.model_name or len(self.model_name)>160:
            raise RuntimeError('Invalid Ollama model name')
        self.model='ollama:'+self.model_name
        self.provider='ollama'
        self._format='json'
        self.capabilities=[]

    def verify_access(self):
        r=httpx.post(self.url+'/api/show',json={'model':self.model_name},timeout=10,trust_env=False)
        if r.status_code==404:
            raise RuntimeError(f'Ollama model {self.model_name} is not installed. Choose an installed model.')
        r.raise_for_status()
        self.capabilities=r.json().get('capabilities',[])
        return self.generate('Return JSON with a single key status and value READY.',128)

    def generate(self,contents,output_tokens=8192):
        parts=contents if isinstance(contents,list) else [contents]
        images,text=[],[]
        for part in parts:
            if isinstance(part,str):
                text.append(part)
            elif getattr(part,'inline_data',None):
                images.append(base64.b64encode(part.inline_data.data).decode())
        if images and 'vision' not in self.capabilities:
            raise RuntimeError(f'{self.model_name} does not support image inputs. Choose a vision model or use text sources.')
        body={'model':self.model_name,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':'\n'.join(text),'images':images}],
              'stream':False,'format':self._format,'options':{'temperature':0,'num_predict':output_tokens,'num_ctx':16384},'keep_alive':'5m'}
        if 'thinking' in self.capabilities:
            body['think']=False
        r=httpx.post(self.url+'/api/chat',json=body,timeout=httpx.Timeout(240,connect=10),trust_env=False)
        r.raise_for_status()
        data=r.json()
        if not data.get('done') or data.get('done_reason')=='length':
            raise ValueError('Ollama generation was incomplete')
        if data.get('model')!=self.model_name:
            raise ValueError('Ollama returned an unexpected model identity')
        result=data.get('message',{}).get('content','')
        if not result:
            raise ValueError('Ollama returned no content')
        return result

    def extract_claims(self,source,images):
        self._format=Extraction.model_json_schema()
        try:
            return super().extract_claims(source,images)
        finally:
            self._format='json'
