import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")

def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT,
        timestamp TEXT,
        agent TEXT,
        status TEXT,
        message TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT,
        title TEXT,
        summary TEXT,
        markdown_body TEXT,
        created_by TEXT,
        created_at TEXT,
        approved INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def insert_log(request_id, agent, status, message):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO logs (request_id, timestamp, agent, status, message)
    VALUES (?, ?, ?, ?, ?)
    """, (
        request_id,
        datetime.now().isoformat(),
        agent,
        status,
        message
    ))

    conn.commit()
    conn.close()

def insert_knowledge(request_id, title, summary, body, user):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO knowledge
    (request_id, title, summary, markdown_body, created_by, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request_id,
        title,
        summary,
        body,
        user,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
