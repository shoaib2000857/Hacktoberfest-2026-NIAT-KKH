import json
import pytest
from app.ollama import OllamaClient, base_url

def test_local_only_endpoint(monkeypatch):
    for url in ['https://ollama.com','http://192.168.1.1:11434','http://localhost:11434/path','http://user:pass@localhost:11434']:
        monkeypatch.setenv('OLLAMA_BASE_URL',url)
        with pytest.raises(RuntimeError,match='loopback'):
            base_url()

def test_ollama_identity_and_structured_extraction(monkeypatch):
    import app.ollama
    calls=[]
    class Response:
        status_code=200
        def __init__(self,data):self.data=data
        def raise_for_status(self):pass
        def json(self):return self.data
    def post(url,json=None,**kwargs):
        calls.append((url,json))
        if url.endswith('/api/show'):return Response({'capabilities':['completion','vision']})
        if isinstance(json['format'],dict):
            content={'claims':[{'id':'a','source_id':'s1','category':'financial','subject':'registration','predicate':'required_fee','value':0,'original_text':'Free registration.','normalized_summary':'Registration is free'}]}
        else:content={'status':'READY'}
        return Response({'model':'gemma3:4b','done':True,'message':{'content':__import__('json').dumps(content)}})
    monkeypatch.setattr(app.ollama.httpx,'post',post)
    c=OllamaClient('gemma3:4b')
    c.verify_access()
    claims=c.extract_claims({'id':'s1','filename':'ad','extracted_text':'Free registration.'},[])
    assert c.model=='ollama:gemma3:4b' and len(claims)==1
    assert isinstance(calls[-1][1]['format'],dict)

def test_text_model_rejects_image(monkeypatch):
    from google.genai import types
    c=OllamaClient('qwen3:4b');c.capabilities=['completion']
    with pytest.raises(RuntimeError,match='does not support image'):
        c.generate([types.Part.from_bytes(data=b'image',mime_type='image/png'),'Read this'])
