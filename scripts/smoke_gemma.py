"""Optional LIVE access test; requires backend .env. Never prints the key."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'apps'/'api'))
from dotenv import load_dotenv
load_dotenv()
from app.gemma import GemmaClient
if __name__=='__main__':
    client=GemmaClient()
    print('Live model:',client.model)
    print('Response:',client.verify_access())
