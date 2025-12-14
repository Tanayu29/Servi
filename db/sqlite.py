import sqlite3
import os
import sys
import threading
from datetime import datetime
from config.loader import load_config

# -----------------------------
# DB パス解決（exe / python 両対応）
# -----------------------------
def get_project_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_db_path():
    config = load_config()
    db_path = config["database"]["path"]

    base_dir = (
        os.path.dirname(sys.executable)
        if getattr(sys, "frozen", False)
        else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )

    full_path = os.path.join(base_dir, db_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    return full_path

DB_PATH = get_db_path()

# -----------------------------
# SQLite 同時書き込み対策
# -----------------------------
_db_lock = threading.Lock()


def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# 初期化
# -----------------------------
def init_db():
    with _db_lock:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT,
            message TEXT,
            created_at TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            created_by TEXT,
            approved INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)

        conn.commit()
        conn.close()


# -----------------------------
# log 操作
# -----------------------------
def insert_log(level: str, message: str):
    with _db_lock:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO log (level, message, created_at)
        VALUES (?, ?, ?)
        """, (level, message, datetime.now().isoformat()))

        conn.commit()
        conn.close()


# -----------------------------
# knowledge 操作
# -----------------------------
def insert_knowledge(title, content, created_by):
    with _db_lock:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO knowledge
        (title, content, created_by, approved, created_at)
        VALUES (?, ?, ?, 0, ?)
        """, (
            title,
            content,
            created_by,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()


def list_unapproved_knowledge():
    with _db_lock:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT id, title, created_by, created_at
        FROM knowledge
        WHERE approved = 0
        ORDER BY created_at
        """)

        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def approve_knowledge(knowledge_id: int) -> bool:
    with _db_lock:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        UPDATE knowledge
        SET approved = 1
        WHERE id = ?
        """, (knowledge_id,))

        conn.commit()
        updated = cur.rowcount
        conn.close()

        return updated > 0


# -----------------------------
# ★ Knowledge 検索（今回の原因）
# -----------------------------
def search_knowledge(keyword: str, approved_only: bool = True):
    """
    title / content を LIKE 検索
    """
    with _db_lock:
        conn = get_connection()
        cur = conn.cursor()

        sql = """
        SELECT id, title, content, created_by, approved, created_at
        FROM knowledge
        WHERE (title LIKE ? OR content LIKE ?)
        """

        params = [f"%{keyword}%", f"%{keyword}%"]

        if approved_only:
            sql += " AND approved = 1"

        sql += " ORDER BY created_at DESC"

        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]
