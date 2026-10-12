import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from threading import RLock

ROOT = Path(os.getenv('PROMISETRAP_DATA_DIR', 'data')).resolve()
ROOT.mkdir(parents=True, exist_ok=True)
LOCK = RLock()

def now():
    return datetime.now(timezone.utc).isoformat()

def connect():
    con = sqlite3.connect(ROOT / 'promisetrap.db', timeout=30)
    con.execute('PRAGMA foreign_keys=ON')
    return con

def migrate():
    with connect() as con:
        con.executescript('''CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_version VALUES(1);
        CREATE TABLE IF NOT EXISTS investigations(id TEXT PRIMARY KEY, payload TEXT NOT NULL);''')
        con.execute('CREATE TABLE IF NOT EXISTS extraction_cache(key TEXT PRIMARY KEY,payload TEXT NOT NULL)')

def cached(key):
    with connect() as con:
        row=con.execute('SELECT payload FROM extraction_cache WHERE key=?',(key,)).fetchone()
    return json.loads(row[0]) if row else None

def cache(key,claims):
    with LOCK,connect() as con:
        con.execute('INSERT OR REPLACE INTO extraction_cache VALUES(?,?)',(key,json.dumps(claims)))

def save(case):
    case['updated_at'] = now()
    with LOCK, connect() as con:
        con.execute('INSERT INTO investigations VALUES(?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload', (case['id'], json.dumps(case)))

def get(case_id):
    with connect() as con:
        row = con.execute('SELECT payload FROM investigations WHERE id=?', (case_id,)).fetchone()
    return json.loads(row[0]) if row else None

def all_cases():
    with connect() as con:
        return [json.loads(r[0]) for r in con.execute('SELECT payload FROM investigations ORDER BY rowid DESC')]

migrate()
