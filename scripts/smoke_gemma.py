"""Optional LIVE access test; requires backend .env. Never prints the key."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'apps'/'api'))
from dotenv import load_dotenv
load_dotenv()
from app.gemma import GemmaClient
if __name__=='__main__':
    try:
        client=GemmaClient()
        print('Live model:',client.model,flush=True)
        print('Response:',client.verify_access(),flush=True)
    except Exception as exc:
        print('Smoke test failed:',type(exc).__name__,'provider status:',getattr(exc,'code',None),flush=True)
        import os
        message=str(exc).replace(os.getenv('GEMINI_API_KEY','') or 'NO_KEY_TO_REDACT','[REDACTED]')
        print('Details:',message[:300],flush=True)
        sys.exit(1)
