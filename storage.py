import sqlite3
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

DB = Path(__file__).parent / "interview_sessions.db"

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT, company TEXT, questions_answered INTEGER,
        report TEXT, created_at TEXT)""")

def save_session(profile, answers, report):
    with sqlite3.connect(DB) as con:
        con.execute("INSERT INTO sessions (role,company,questions_answered,report,created_at) VALUES (?,?,?,?,?)",
            (profile.get("job_title",""), profile.get("company",""), len(answers),
             report, datetime.now(timezone.utc).isoformat(timespec="seconds")))

def load_sessions():
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query("SELECT id,role,company,questions_answered,created_at FROM sessions ORDER BY id DESC", con)
