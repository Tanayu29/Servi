Servi Project Dump
Generated at: 12/16/2025 10:42:49

==== Directory Structure ====
フォルダー パスの一覧
ボリューム シリアル番号は B00B-A028 です
C:.
│  approve.spec
│  build.ps1
│  config.yaml
│  export_project_md.ps1
│  export_tree.ps1
│  main.py
│  orchestrator.py
│  release.ps1
│  servi.spec
│  servi_main.py
│  servi_project_dump.md
│  structure.txt
│  writer.py
│  
├─agents
│  │  base.py
│  │  drop_watcher.py
│  │  knowledge.py
│  │  knowledge_approval.py
│  │  knowledge_search.py
│  │  __init__.py
│  │  
│  └─__pycache__
│          base.cpython-311.pyc
│          base.cpython-314.pyc
│          knowledge.cpython-311.pyc
│          knowledge.cpython-314.pyc
│          knowledge_approval.cpython-311.pyc
│          knowledge_approval.cpython-314.pyc
│          knowledge_search.cpython-311.pyc
│          knowledge_search.cpython-314.pyc
│          __init__.cpython-311.pyc
│          __init__.cpython-314.pyc
│          
├─build
│  ├─approve
│  │  │  Analysis-00.toc
│  │  │  approve.pkg
│  │  │  base_library.zip
│  │  │  EXE-00.toc
│  │  │  PKG-00.toc
│  │  │  PYZ-00.pyz
│  │  │  PYZ-00.toc
│  │  │  warn-approve.txt
│  │  │  xref-approve.html
│  │  │  
│  │  └─localpycs
│  │          pyimod01_archive.pyc
│  │          pyimod02_importers.pyc
│  │          pyimod03_ctypes.pyc
│  │          pyimod04_pywin32.pyc
│  │          struct.pyc
│  │          
│  └─servi
│      │  Analysis-00.toc
│      │  base_library.zip
│      │  EXE-00.toc
│      │  PKG-00.toc
│      │  PYZ-00.pyz
│      │  PYZ-00.toc
│      │  servi.pkg
│      │  warn-servi.txt
│      │  xref-servi.html
│      │  
│      └─localpycs
│              pyimod01_archive.pyc
│              pyimod02_importers.pyc
│              pyimod03_ctypes.pyc
│              pyimod04_pywin32.pyc
│              struct.pyc
│              
├─cli
│      approve.py
│      
├─config
│  │  loader.py
│  │  
│  └─__pycache__
│          loader.cpython-311.pyc
│          
├─data
│      app.db
│      
├─db
│  │  sqlite.py
│  │  __init__.py
│  │  
│  └─__pycache__
│          sqlite.cpython-311.pyc
│          sqlite.cpython-314.pyc
│          __init__.cpython-311.pyc
│          __init__.cpython-314.pyc
│          
├─dist
│      approve.exe
│      servi.exe
│      
├─docs
│      00_overview.md
│      01_goals.md
│      02_tasks.md
│      03_architecture.md
│      04_agents.md
│      05_agent_protocol.md
│      06_rules.md
│      99_notes.md
│      
├─protocols
│      schemas.py
│      
└─__pycache__
        orchestrator.cpython-311.pyc
        orchestrator.cpython-314.pyc
        writer.cpython-311.pyc
        writer.cpython-314.pyc
        


==== Source Files ====

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\main.py
TYPE: *.py
---- CONTENT ----
from orchestrator import OrchestratorAgent
from db.sqlite import init_db

if __name__ == "__main__":
    init_db()

    orch = OrchestratorAgent()

    request = {
        "task_type": "knowledge.approve",
        "user_context": {
            "user_id": "yuya",
            "role": "admin"
        },
        "input": {
            "knowledge_id": 1
        }
    }

    response = orch.handle_request(request)
    print(response)
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\orchestrator.py
TYPE: *.py
---- CONTENT ----
import os
import sys
import uuid
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


from agents.knowledge import KnowledgeAgent
from agents.knowledge_search import KnowledgeSearchAgent
from agents.knowledge_approval import KnowledgeApprovalAgent
from writer import WriterAgent


writer = WriterAgent()


class OrchestratorAgent:

    def handle_request(self, raw_request: dict) -> dict:
        request = self._normalize_request(raw_request)

        try:
            category = self._classify_task(request)
            agent = self._select_agent(category)

            response = agent.execute(request)

            writer.enqueue("log", {
                "request_id": request["request_id"],
                "agent": agent.name,
                "status": response.get("status"),
                "message": "execution finished"
            })

            if response.get("status") == "success":
                self._post_process_success(category, request, response)

            return response

        except Exception as e:
            writer.enqueue("log", {
                "request_id": request.get("request_id"),
                "agent": "OrchestratorAgent",
                "status": "failed",
                "message": str(e)
            })

            return {
                "request_id": request.get("request_id"),
                "status": "failed",
                "agent": "OrchestratorAgent",
                "errors": [str(e)]
            }

    # ---------------------

    def _normalize_request(self, raw: dict) -> dict:
        raw = raw.copy()
        raw["request_id"] = str(uuid.uuid4())
        raw["timestamp"] = datetime.datetime.now().isoformat()
        raw.setdefault("user_context", {})
        return raw

    def _classify_task(self, request: dict) -> str:
        task_type = request.get("task_type", "")

        if task_type.startswith("knowledge.generate"):
            return "knowledge_generate"

        if task_type.startswith("knowledge.search"):
            return "knowledge_search"

        if task_type.startswith("knowledge.approve"):
            return "knowledge_approve"

        raise ValueError(f"Unsupported task_type: {task_type}")

    def _select_agent(self, category: str):
        if category == "knowledge_generate":
            return KnowledgeAgent()

        if category == "knowledge_search":
            return KnowledgeSearchAgent()

        if category == "knowledge_approve":
            return KnowledgeApprovalAgent()

        raise ValueError(f"No agent for category: {category}")

    def _post_process_success(self, category, request, response):

        if category == "knowledge_generate":
            result = response["result"]
            user_id = request.get("user_context", {}).get("user_id", "unknown")

            writer.enqueue("knowledge", {
                "request_id": request["request_id"],
                "title": result.get("title"),
                "summary": result.get("summary"),
                "body": result.get("markdown_body"),
                "user": user_id
            })

        if category == "knowledge_approve":
            knowledge_id = response["result"]["knowledge_id"]

            writer.enqueue("approve", {
                "knowledge_id": knowledge_id
            })
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\servi_main.py
TYPE: *.py
---- CONTENT ----
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from orchestrator import OrchestratorAgent
from agents.drop_watcher import DropWatcherAgent
from config.loader import load_config
from db.sqlite import init_db


def main():
    print("=== Servi 襍ｷ蜍穂ｸｭ ===")

    config = load_config()
    init_db()

    watcher = DropWatcherAgent(
        input_dir=os.path.join(BASE_DIR, "input"),
        processed_dir=os.path.join(BASE_DIR, "processed"),
        error_dir=os.path.join(BASE_DIR, "error"),
    )

    print("Drop繝輔か繝ｫ繝逶｣隕悶ｒ髢句ｧ・)

    while True:
        watcher.run_once()
        time.sleep(5)


if __name__ == "__main__":
    main()
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\writer.py
TYPE: *.py
---- CONTENT ----
import threading
import queue
from db import sqlite

class WriterAgent:
    def __init__(self):
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def enqueue(self, action: str, payload: dict):
        self.queue.put((action, payload))

    def _run(self):
        while True:
            action, payload = self.queue.get()
            try:
                if action == "log":
                    sqlite.insert_log(**payload)
                elif action == "knowledge":
                    sqlite.insert_knowledge(**payload)
            finally:
                self.queue.task_done()
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\base.py
TYPE: *.py
---- CONTENT ----
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    name = "BaseAgent"

    @abstractmethod
    def execute(self, request: dict) -> dict:
        pass
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\drop_watcher.py
TYPE: *.py
---- CONTENT ----
import os
import shutil
from db.sqlite import insert_knowledge, insert_log


class DropWatcherAgent:
    def __init__(self, input_dir, processed_dir, error_dir):
        self.input_dir = input_dir
        self.processed_dir = processed_dir
        self.error_dir = error_dir

        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.error_dir, exist_ok=True)

    def run_once(self):
        for fname in os.listdir(self.input_dir):
            path = os.path.join(self.input_dir, fname)
            if not os.path.isfile(path):
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                insert_knowledge(
                    title=fname,
                    content=content,
                    source="drop_folder",
                    approved=0,
                )

                shutil.move(path, os.path.join(self.processed_dir, fname))
                insert_log("INFO", f"processed file: {fname}")

            except Exception as e:
                shutil.move(path, os.path.join(self.error_dir, fname))
                insert_log("ERROR", f"{fname}: {e}")
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\knowledge.py
TYPE: *.py
---- CONTENT ----
from agents.base import BaseAgent

class KnowledgeAgent(BaseAgent):
    name = "KnowledgeAgent"

    def execute(self, request):
        sources = request.get("input", {}).get("sources", [])
        summary = f"{len(sources)} 莉ｶ縺ｮ諠・ｱ縺九ｉ逕滓・"

        return {
            "status": "success",
            "agent": self.name,
            "result": {
                "title": "莉ｮ繝翫Ξ繝・ず",
                "summary": summary,
                "markdown_body": "## 譛ｬ譁・
            },
            "human_review_required": True
        }
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\knowledge_approval.py
TYPE: *.py
---- CONTENT ----
from agents.base import BaseAgent

class KnowledgeApprovalAgent(BaseAgent):
    name = "KnowledgeApprovalAgent"

    def execute(self, request: dict) -> dict:
        input_data = request.get("input", {})
        knowledge_id = input_data.get("knowledge_id")

        if knowledge_id is None:
            return {
                "status": "failed",
                "agent": self.name,
                "errors": ["knowledge_id is required"]
            }

        return {
            "status": "success",
            "agent": self.name,
            "result": {
                "knowledge_id": knowledge_id,
                "approved": True
            },
            "human_review_required": False,
            "warnings": [],
            "errors": []
        }
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\knowledge_search.py
TYPE: *.py
---- CONTENT ----
from agents.base import BaseAgent
from db.sqlite import search_knowledge

class KnowledgeSearchAgent(BaseAgent):
    name = "KnowledgeSearchAgent"

    def execute(self, request: dict) -> dict:
        input_data = request.get("input", {})
        query = input_data.get("query", "")
        limit = input_data.get("limit", 10)
        approved_only = input_data.get("approved_only", True)

        if not query:
            return {
                "status": "failed",
                "agent": self.name,
                "errors": ["query is empty"]
            }

        results = search_knowledge(query, limit, approved_only)

        return {
            "status": "success",
            "agent": self.name,
            "result": {
                "count": len(results),
                "items": results
            },
            "human_review_required": False,
            "warnings": [],
            "errors": []
        }
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\__init__.py
TYPE: *.py
---- CONTENT ----
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\cli\approve.py
TYPE: *.py
---- CONTENT ----
import sys
import os

# =====================================
# 笘・import 繧医ｊ蜈医↓繝代せ繧帝壹☆・域怙驥崎ｦ・ｼ・
# =====================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PyInstaller exe 螳溯｡梧凾
if getattr(sys, "frozen", False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

sys.path.insert(0, PROJECT_ROOT)
# =====================================

from orchestrator import OrchestratorAgent
from db.sqlite import init_db, list_unapproved_knowledge
from config.loader import load_config

config = load_config()
default_role = config["security"]["default_role"]

def print_knowledge_list(items):
    print("\n=== 譛ｪ謇ｿ隱阪リ繝ｬ繝・ず荳隕ｧ ===")

    if not items:
        print("譛ｪ謇ｿ隱阪リ繝ｬ繝・ず縺ｯ縺ゅｊ縺ｾ縺帙ｓ")
        return

    for item in items:
        print(
            f"[{item['id']}] "
            f"{item['title']} | "
            f"{item['created_by']} | "
            f"{item['created_at']}"
        )


def main():
    init_db()
    orch = OrchestratorAgent()

    while True:
        items = list_unapproved_knowledge()
        print_knowledge_list(items)

        if not items:
            break

        user_input = input(
            "\n謇ｿ隱阪☆繧紀D繧貞・蜉幢ｼ・縺ｧ邨ゆｺ・/ r縺ｧ蜀崎｡ｨ遉ｺ・・ "
        ).strip()

        if user_input.lower() == "q":
            break
        if user_input.lower() == "r":
            continue
        if not user_input.isdigit():
            print("謨ｰ蛟､ID繧貞・蜉帙＠縺ｦ縺上□縺輔＞")
            continue

        knowledge_id = int(user_input)

        request = {
            "task_type": "knowledge.approve",
            "user_context": {
                "user_id": "cli_user",
                "role": default_role
            },
            "input": {
                "knowledge_id": knowledge_id
            }
        }

        response = orch.handle_request(request)

        if response.get("status") == "success":
            print(f">>> 繝翫Ξ繝・ず {knowledge_id} 繧呈価隱阪＠縺ｾ縺励◆")
        else:
            print("謇ｿ隱阪↓螟ｱ謨励＠縺ｾ縺励◆:", response.get("errors"))

    print("\nCLI 謇ｿ隱攻I繧堤ｵゆｺ・＠縺ｾ縺・)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("=== 閾ｴ蜻ｽ逧・お繝ｩ繝ｼ ===")
        traceback.print_exc()
        input("\nEnter繧ｭ繝ｼ縺ｧ邨ゆｺ・)
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\config\loader.py
TYPE: *.py
---- CONTENT ----
import os
import sys
import yaml


def get_base_dir():
    """
    螳溯｡檎腸蠅・↓蠢懊§縺溘・繝ｼ繧ｹ繝・ぅ繝ｬ繧ｯ繝医Μ繧定ｿ斐☆
    - python螳溯｡梧凾: 繝励Ο繧ｸ繧ｧ繧ｯ繝医Ν繝ｼ繝・
    - exe螳溯｡梧凾   : exe縺ｮ縺ゅｋ繝・ぅ繝ｬ繧ｯ繝医Μ
    """
    if getattr(sys, "frozen", False):
        # PyInstaller exe
        return os.path.dirname(sys.executable)
    else:
        # python
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    base_dir = get_base_dir()
    config_path = os.path.join(base_dir, "config.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.yaml not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\db\sqlite.py
TYPE: *.py
---- CONTENT ----
import sqlite3
import os
import sys
import threading
from datetime import datetime
from config.loader import load_config

# -----------------------------
# DB 繝代せ隗｣豎ｺ・・xe / python 荳｡蟇ｾ蠢懶ｼ・
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
# SQLite 蜷梧凾譖ｸ縺崎ｾｼ縺ｿ蟇ｾ遲・
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
# 蛻晄悄蛹・
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
# log 謫堺ｽ・
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
# knowledge 謫堺ｽ・
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
# 笘・Knowledge 讀懃ｴ｢・井ｻ雁屓縺ｮ蜴溷屏・・
# -----------------------------
def search_knowledge(keyword: str, approved_only: bool = True):
    """
    title / content 繧・LIKE 讀懃ｴ｢
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
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\db\__init__.py
TYPE: *.py
---- CONTENT ----
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\protocols\schemas.py
TYPE: *.py
---- CONTENT ----
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\build.ps1
TYPE: *.ps1
---- CONTENT ----
# ==============================
# Servi build script
# ==============================

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

Write-Host "=== Servi Build Start ==="

# Python 螳溯｡後ヱ繧ｹ・亥ｿ・ｦ√↑繧牙､画峩・・
$PYTHON = "python"

# 蜃ｺ蜉帶紛逅・
if (Test-Path "dist") {
    Write-Host "Cleaning dist/"
    Remove-Item dist -Recurse -Force
}

if (Test-Path "build") {
    Remove-Item build -Recurse -Force
}

# ------------------------------
# servi.exe
# ------------------------------
Write-Host "Building servi.exe"

& $PYTHON -m PyInstaller `
    servi_main.py `
    --onefile `
    --name servi `
    --clean `
    --paths . `
    --hidden-import=yaml

if ($LASTEXITCODE -ne 0) {
    throw "servi.exe build failed"
}

# ------------------------------
# approve.exe
# ------------------------------
Write-Host "Building approve.exe"

& $PYTHON -m PyInstaller `
    cli/approve.py `
    --onefile `
    --name approve `
    --clean `
    --paths . `
    --hidden-import=yaml

if ($LASTEXITCODE -ne 0) {
    throw "approve.exe build failed"
}

Write-Host "=== Build Completed ==="
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\export_project_md.ps1
TYPE: *.ps1
---- CONTENT ----
Write-Host 'Exporting project to single file...'

$OutputFile = 'servi_project_dump.md'

$writer = New-Object System.IO.StreamWriter($OutputFile, $false, [System.Text.Encoding]::UTF8)

try {
    $writer.WriteLine('Servi Project Dump')
    $writer.WriteLine('Generated at: ' + (Get-Date))
    $writer.WriteLine('')
    $writer.WriteLine('==== Directory Structure ====')

    $tree = tree /F | Out-String
    $writer.WriteLine($tree)

    $writer.WriteLine('')
    $writer.WriteLine('==== Source Files ====')

    $extensions = @('*.py', '*.ps1', '*.yaml', '*.yml', '*.md', '*.spec')

    foreach ($ext in $extensions) {

        Get-ChildItem -Recurse -File -Filter $ext |
        Where-Object {
            $_.FullName -notmatch '\\dist\\|\\build\\|\\__pycache__\\'
        } |
        ForEach-Object {

            $writer.WriteLine('')
            $writer.WriteLine('---- FILE START ----')
            $writer.WriteLine('PATH: ' + $_.FullName)
            $writer.WriteLine('TYPE: ' + $ext)
            $writer.WriteLine('---- CONTENT ----')

            foreach ($line in Get-Content $_.FullName) {
                $writer.WriteLine($line)
            }

            $writer.WriteLine('---- FILE END ----')
        }
    }
}
finally {
    $writer.Close()
}

Write-Host 'Export completed successfully.'
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\export_tree.ps1
TYPE: *.ps1
---- CONTENT ----
# ==============================
# Folder structure exporter
# ==============================

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

$OUTPUT = "structure.txt"

Write-Host "Exporting folder structure..."

# dist / build / __pycache__ 繧帝勁螟・
tree $PROJECT_ROOT /F `
    | Select-String -NotMatch "\\dist\\|\\build\\|__pycache__" `
    | Out-File $OUTPUT -Encoding utf8

Write-Host "Saved to $OUTPUT"
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\release.ps1
TYPE: *.ps1
---- CONTENT ----
# ==============================
# Servi Release Script
# ==============================

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

Write-Host "=== Servi Release Start ==="

# ------------------------------
# Build exe
# ------------------------------
Write-Host "Running build.ps1"
.\build.ps1

# ------------------------------
# Copy config.yaml
# ------------------------------
$DIST_DIR = Join-Path $PROJECT_ROOT "dist"
$CONFIG_SRC = Join-Path $PROJECT_ROOT "config.yaml"
$CONFIG_DST = Join-Path $DIST_DIR "config.yaml"

if (-Not (Test-Path $CONFIG_SRC)) {
    throw "config.yaml not found in project root"
}

Write-Host "Copying config.yaml to dist/"
Copy-Item $CONFIG_SRC $CONFIG_DST -Force

# ------------------------------
# Copy data directory (optional but recommended)
# ------------------------------
$DATA_SRC = Join-Path $PROJECT_ROOT "data"
$DATA_DST = Join-Path $DIST_DIR "data"

if (Test-Path $DATA_SRC) {
    Write-Host "Copying data/ to dist/"
    if (Test-Path $DATA_DST) {
        Remove-Item $DATA_DST -Recurse -Force
    }
    Copy-Item $DATA_SRC $DATA_DST -Recurse -Force
}

# ------------------------------
# Export folder structure
# ------------------------------
Write-Host "Exporting folder structure"
.\export_tree.ps1

Write-Host "=== Release Completed ==="
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\config.yaml
TYPE: *.yaml
---- CONTENT ----
app:
  name: Servi
  mode: business        # business / personal
  log_level: INFO

database:
  type: sqlite
  path: data/app.db     # 逶ｸ蟇ｾ繝代せ・・xe蝓ｺ貅厄ｼ・

security:
  default_role: user
  admin_users:
    - cli_user
    - admin

features:
  knowledge:
    enabled: true
    approval_required: true

  side_business:
    enabled: false      # 蛟倶ｺｺ蛻ｩ逕ｨ譎・true
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\servi_project_dump.md
TYPE: *.md
---- CONTENT ----
Servi Project Dump
Generated at: 12/16/2025 10:42:49

==== Directory Structure ====
フォルダー パスの一覧
ボリューム シリアル番号は B00B-A028 です
C:.
│  approve.spec
│  build.ps1
│  config.yaml
│  export_project_md.ps1
│  export_tree.ps1
│  main.py
│  orchestrator.py
│  release.ps1
│  servi.spec
│  servi_main.py
│  servi_project_dump.md
│  structure.txt
│  writer.py
│  
├─agents
│  │  base.py
│  │  drop_watcher.py
│  │  knowledge.py
│  │  knowledge_approval.py
│  │  knowledge_search.py
│  │  __init__.py
│  │  
│  └─__pycache__
│          base.cpython-311.pyc
│          base.cpython-314.pyc
│          knowledge.cpython-311.pyc
│          knowledge.cpython-314.pyc
│          knowledge_approval.cpython-311.pyc
│          knowledge_approval.cpython-314.pyc
│          knowledge_search.cpython-311.pyc
│          knowledge_search.cpython-314.pyc
│          __init__.cpython-311.pyc
│          __init__.cpython-314.pyc
│          
├─build
│  ├─approve
│  │  │  Analysis-00.toc
│  │  │  approve.pkg
│  │  │  base_library.zip
│  │  │  EXE-00.toc
│  │  │  PKG-00.toc
│  │  │  PYZ-00.pyz
│  │  │  PYZ-00.toc
│  │  │  warn-approve.txt
│  │  │  xref-approve.html
│  │  │  
│  │  └─localpycs
│  │          pyimod01_archive.pyc
│  │          pyimod02_importers.pyc
│  │          pyimod03_ctypes.pyc
│  │          pyimod04_pywin32.pyc
│  │          struct.pyc
│  │          
│  └─servi
│      │  Analysis-00.toc
│      │  base_library.zip
│      │  EXE-00.toc
│      │  PKG-00.toc
│      │  PYZ-00.pyz
│      │  PYZ-00.toc
│      │  servi.pkg
│      │  warn-servi.txt
│      │  xref-servi.html
│      │  
│      └─localpycs
│              pyimod01_archive.pyc
│              pyimod02_importers.pyc
│              pyimod03_ctypes.pyc
│              pyimod04_pywin32.pyc
│              struct.pyc
│              
├─cli
│      approve.py
│      
├─config
│  │  loader.py
│  │  
│  └─__pycache__
│          loader.cpython-311.pyc
│          
├─data
│      app.db
│      
├─db
│  │  sqlite.py
│  │  __init__.py
│  │  
│  └─__pycache__
│          sqlite.cpython-311.pyc
│          sqlite.cpython-314.pyc
│          __init__.cpython-311.pyc
│          __init__.cpython-314.pyc
│          
├─dist
│      approve.exe
│      servi.exe
│      
├─docs
│      00_overview.md
│      01_goals.md
│      02_tasks.md
│      03_architecture.md
│      04_agents.md
│      05_agent_protocol.md
│      06_rules.md
│      99_notes.md
│      
├─protocols
│      schemas.py
│      
└─__pycache__
        orchestrator.cpython-311.pyc
        orchestrator.cpython-314.pyc
        writer.cpython-311.pyc
        writer.cpython-314.pyc
        


==== Source Files ====

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\main.py
TYPE: *.py
---- CONTENT ----
from orchestrator import OrchestratorAgent
from db.sqlite import init_db

if __name__ == "__main__":
    init_db()

    orch = OrchestratorAgent()

    request = {
        "task_type": "knowledge.approve",
        "user_context": {
            "user_id": "yuya",
            "role": "admin"
        },
        "input": {
            "knowledge_id": 1
        }
    }

    response = orch.handle_request(request)
    print(response)
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\orchestrator.py
TYPE: *.py
---- CONTENT ----
import os
import sys
import uuid
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


from agents.knowledge import KnowledgeAgent
from agents.knowledge_search import KnowledgeSearchAgent
from agents.knowledge_approval import KnowledgeApprovalAgent
from writer import WriterAgent


writer = WriterAgent()


class OrchestratorAgent:

    def handle_request(self, raw_request: dict) -> dict:
        request = self._normalize_request(raw_request)

        try:
            category = self._classify_task(request)
            agent = self._select_agent(category)

            response = agent.execute(request)

            writer.enqueue("log", {
                "request_id": request["request_id"],
                "agent": agent.name,
                "status": response.get("status"),
                "message": "execution finished"
            })

            if response.get("status") == "success":
                self._post_process_success(category, request, response)

            return response

        except Exception as e:
            writer.enqueue("log", {
                "request_id": request.get("request_id"),
                "agent": "OrchestratorAgent",
                "status": "failed",
                "message": str(e)
            })

            return {
                "request_id": request.get("request_id"),
                "status": "failed",
                "agent": "OrchestratorAgent",
                "errors": [str(e)]
            }

    # ---------------------

    def _normalize_request(self, raw: dict) -> dict:
        raw = raw.copy()
        raw["request_id"] = str(uuid.uuid4())
        raw["timestamp"] = datetime.datetime.now().isoformat()
        raw.setdefault("user_context", {})
        return raw

    def _classify_task(self, request: dict) -> str:
        task_type = request.get("task_type", "")

        if task_type.startswith("knowledge.generate"):
            return "knowledge_generate"

        if task_type.startswith("knowledge.search"):
            return "knowledge_search"

        if task_type.startswith("knowledge.approve"):
            return "knowledge_approve"

        raise ValueError(f"Unsupported task_type: {task_type}")

    def _select_agent(self, category: str):
        if category == "knowledge_generate":
            return KnowledgeAgent()

        if category == "knowledge_search":
            return KnowledgeSearchAgent()

        if category == "knowledge_approve":
            return KnowledgeApprovalAgent()

        raise ValueError(f"No agent for category: {category}")

    def _post_process_success(self, category, request, response):

        if category == "knowledge_generate":
            result = response["result"]
            user_id = request.get("user_context", {}).get("user_id", "unknown")

            writer.enqueue("knowledge", {
                "request_id": request["request_id"],
                "title": result.get("title"),
                "summary": result.get("summary"),
                "body": result.get("markdown_body"),
                "user": user_id
            })

        if category == "knowledge_approve":
            knowledge_id = response["result"]["knowledge_id"]

            writer.enqueue("approve", {
                "knowledge_id": knowledge_id
            })
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\servi_main.py
TYPE: *.py
---- CONTENT ----
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from orchestrator import OrchestratorAgent
from agents.drop_watcher import DropWatcherAgent
from config.loader import load_config
from db.sqlite import init_db


def main():
    print("=== Servi 襍ｷ蜍穂ｸｭ ===")

    config = load_config()
    init_db()

    watcher = DropWatcherAgent(
        input_dir=os.path.join(BASE_DIR, "input"),
        processed_dir=os.path.join(BASE_DIR, "processed"),
        error_dir=os.path.join(BASE_DIR, "error"),
    )

    print("Drop繝輔か繝ｫ繝逶｣隕悶ｒ髢句ｧ・)

    while True:
        watcher.run_once()
        time.sleep(5)


if __name__ == "__main__":
    main()
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\writer.py
TYPE: *.py
---- CONTENT ----
import threading
import queue
from db import sqlite

class WriterAgent:
    def __init__(self):
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def enqueue(self, action: str, payload: dict):
        self.queue.put((action, payload))

    def _run(self):
        while True:
            action, payload = self.queue.get()
            try:
                if action == "log":
                    sqlite.insert_log(**payload)
                elif action == "knowledge":
                    sqlite.insert_knowledge(**payload)
            finally:
                self.queue.task_done()
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\base.py
TYPE: *.py
---- CONTENT ----
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    name = "BaseAgent"

    @abstractmethod
    def execute(self, request: dict) -> dict:
        pass
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\drop_watcher.py
TYPE: *.py
---- CONTENT ----
import os
import shutil
from db.sqlite import insert_knowledge, insert_log


class DropWatcherAgent:
    def __init__(self, input_dir, processed_dir, error_dir):
        self.input_dir = input_dir
        self.processed_dir = processed_dir
        self.error_dir = error_dir

        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.error_dir, exist_ok=True)

    def run_once(self):
        for fname in os.listdir(self.input_dir):
            path = os.path.join(self.input_dir, fname)
            if not os.path.isfile(path):
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                insert_knowledge(
                    title=fname,
                    content=content,
                    source="drop_folder",
                    approved=0,
                )

                shutil.move(path, os.path.join(self.processed_dir, fname))
                insert_log("INFO", f"processed file: {fname}")

            except Exception as e:
                shutil.move(path, os.path.join(self.error_dir, fname))
                insert_log("ERROR", f"{fname}: {e}")
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\knowledge.py
TYPE: *.py
---- CONTENT ----
from agents.base import BaseAgent

class KnowledgeAgent(BaseAgent):
    name = "KnowledgeAgent"

    def execute(self, request):
        sources = request.get("input", {}).get("sources", [])
        summary = f"{len(sources)} 莉ｶ縺ｮ諠・ｱ縺九ｉ逕滓・"

        return {
            "status": "success",
            "agent": self.name,
            "result": {
                "title": "莉ｮ繝翫Ξ繝・ず",
                "summary": summary,
                "markdown_body": "## 譛ｬ譁・
            },
            "human_review_required": True
        }
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\knowledge_approval.py
TYPE: *.py
---- CONTENT ----
from agents.base import BaseAgent

class KnowledgeApprovalAgent(BaseAgent):
    name = "KnowledgeApprovalAgent"

    def execute(self, request: dict) -> dict:
        input_data = request.get("input", {})
        knowledge_id = input_data.get("knowledge_id")

        if knowledge_id is None:
            return {
                "status": "failed",
                "agent": self.name,
                "errors": ["knowledge_id is required"]
            }

        return {
            "status": "success",
            "agent": self.name,
            "result": {
                "knowledge_id": knowledge_id,
                "approved": True
            },
            "human_review_required": False,
            "warnings": [],
            "errors": []
        }
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\knowledge_search.py
TYPE: *.py
---- CONTENT ----
from agents.base import BaseAgent
from db.sqlite import search_knowledge

class KnowledgeSearchAgent(BaseAgent):
    name = "KnowledgeSearchAgent"

    def execute(self, request: dict) -> dict:
        input_data = request.get("input", {})
        query = input_data.get("query", "")
        limit = input_data.get("limit", 10)
        approved_only = input_data.get("approved_only", True)

        if not query:
            return {
                "status": "failed",
                "agent": self.name,
                "errors": ["query is empty"]
            }

        results = search_knowledge(query, limit, approved_only)

        return {
            "status": "success",
            "agent": self.name,
            "result": {
                "count": len(results),
                "items": results
            },
            "human_review_required": False,
            "warnings": [],
            "errors": []
        }
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\agents\__init__.py
TYPE: *.py
---- CONTENT ----
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\cli\approve.py
TYPE: *.py
---- CONTENT ----
import sys
import os

# =====================================
# 笘・import 繧医ｊ蜈医↓繝代せ繧帝壹☆・域怙驥崎ｦ・ｼ・
# =====================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PyInstaller exe 螳溯｡梧凾
if getattr(sys, "frozen", False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

sys.path.insert(0, PROJECT_ROOT)
# =====================================

from orchestrator import OrchestratorAgent
from db.sqlite import init_db, list_unapproved_knowledge
from config.loader import load_config

config = load_config()
default_role = config["security"]["default_role"]

def print_knowledge_list(items):
    print("\n=== 譛ｪ謇ｿ隱阪リ繝ｬ繝・ず荳隕ｧ ===")

    if not items:
        print("譛ｪ謇ｿ隱阪リ繝ｬ繝・ず縺ｯ縺ゅｊ縺ｾ縺帙ｓ")
        return

    for item in items:
        print(
            f"[{item['id']}] "
            f"{item['title']} | "
            f"{item['created_by']} | "
            f"{item['created_at']}"
        )


def main():
    init_db()
    orch = OrchestratorAgent()

    while True:
        items = list_unapproved_knowledge()
        print_knowledge_list(items)

        if not items:
            break

        user_input = input(
            "\n謇ｿ隱阪☆繧紀D繧貞・蜉幢ｼ・縺ｧ邨ゆｺ・/ r縺ｧ蜀崎｡ｨ遉ｺ・・ "
        ).strip()

        if user_input.lower() == "q":
            break
        if user_input.lower() == "r":
            continue
        if not user_input.isdigit():
            print("謨ｰ蛟､ID繧貞・蜉帙＠縺ｦ縺上□縺輔＞")
            continue

        knowledge_id = int(user_input)

        request = {
            "task_type": "knowledge.approve",
            "user_context": {
                "user_id": "cli_user",
                "role": default_role
            },
            "input": {
                "knowledge_id": knowledge_id
            }
        }

        response = orch.handle_request(request)

        if response.get("status") == "success":
            print(f">>> 繝翫Ξ繝・ず {knowledge_id} 繧呈価隱阪＠縺ｾ縺励◆")
        else:
            print("謇ｿ隱阪↓螟ｱ謨励＠縺ｾ縺励◆:", response.get("errors"))

    print("\nCLI 謇ｿ隱攻I繧堤ｵゆｺ・＠縺ｾ縺・)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("=== 閾ｴ蜻ｽ逧・お繝ｩ繝ｼ ===")
        traceback.print_exc()
        input("\nEnter繧ｭ繝ｼ縺ｧ邨ゆｺ・)
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\config\loader.py
TYPE: *.py
---- CONTENT ----
import os
import sys
import yaml


def get_base_dir():
    """
    螳溯｡檎腸蠅・↓蠢懊§縺溘・繝ｼ繧ｹ繝・ぅ繝ｬ繧ｯ繝医Μ繧定ｿ斐☆
    - python螳溯｡梧凾: 繝励Ο繧ｸ繧ｧ繧ｯ繝医Ν繝ｼ繝・
    - exe螳溯｡梧凾   : exe縺ｮ縺ゅｋ繝・ぅ繝ｬ繧ｯ繝医Μ
    """
    if getattr(sys, "frozen", False):
        # PyInstaller exe
        return os.path.dirname(sys.executable)
    else:
        # python
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    base_dir = get_base_dir()
    config_path = os.path.join(base_dir, "config.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.yaml not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\db\sqlite.py
TYPE: *.py
---- CONTENT ----
import sqlite3
import os
import sys
import threading
from datetime import datetime
from config.loader import load_config

# -----------------------------
# DB 繝代せ隗｣豎ｺ・・xe / python 荳｡蟇ｾ蠢懶ｼ・
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
# SQLite 蜷梧凾譖ｸ縺崎ｾｼ縺ｿ蟇ｾ遲・
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
# 蛻晄悄蛹・
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
# log 謫堺ｽ・
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
# knowledge 謫堺ｽ・
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
# 笘・Knowledge 讀懃ｴ｢・井ｻ雁屓縺ｮ蜴溷屏・・
# -----------------------------
def search_knowledge(keyword: str, approved_only: bool = True):
    """
    title / content 繧・LIKE 讀懃ｴ｢
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
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\db\__init__.py
TYPE: *.py
---- CONTENT ----
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\protocols\schemas.py
TYPE: *.py
---- CONTENT ----
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\build.ps1
TYPE: *.ps1
---- CONTENT ----
# ==============================
# Servi build script
# ==============================

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

Write-Host "=== Servi Build Start ==="

# Python 螳溯｡後ヱ繧ｹ・亥ｿ・ｦ√↑繧牙､画峩・・
$PYTHON = "python"

# 蜃ｺ蜉帶紛逅・
if (Test-Path "dist") {
    Write-Host "Cleaning dist/"
    Remove-Item dist -Recurse -Force
}

if (Test-Path "build") {
    Remove-Item build -Recurse -Force
}

# ------------------------------
# servi.exe
# ------------------------------
Write-Host "Building servi.exe"

& $PYTHON -m PyInstaller `
    servi_main.py `
    --onefile `
    --name servi `
    --clean `
    --paths . `
    --hidden-import=yaml

if ($LASTEXITCODE -ne 0) {
    throw "servi.exe build failed"
}

# ------------------------------
# approve.exe
# ------------------------------
Write-Host "Building approve.exe"

& $PYTHON -m PyInstaller `
    cli/approve.py `
    --onefile `
    --name approve `
    --clean `
    --paths . `
    --hidden-import=yaml

if ($LASTEXITCODE -ne 0) {
    throw "approve.exe build failed"
}

Write-Host "=== Build Completed ==="
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\export_project_md.ps1
TYPE: *.ps1
---- CONTENT ----
Write-Host 'Exporting project to single file...'

$OutputFile = 'servi_project_dump.md'

$writer = New-Object System.IO.StreamWriter($OutputFile, $false, [System.Text.Encoding]::UTF8)

try {
    $writer.WriteLine('Servi Project Dump')
    $writer.WriteLine('Generated at: ' + (Get-Date))
    $writer.WriteLine('')
    $writer.WriteLine('==== Directory Structure ====')

    $tree = tree /F | Out-String
    $writer.WriteLine($tree)

    $writer.WriteLine('')
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\docs\00_overview.md
TYPE: *.md
---- CONTENT ----
# 菴輔ｒ菴懊ｋ縺ｮ縺・
- 讌ｭ蜍吝柑邇・喧縺ｨ蜑ｯ讌ｭ謾ｯ謠ｴ繧貞・縺ｭ縺溘し繝昴・繝医ヤ繝ｼ繝ｫ
- 閾ｪ蟾ｱ蟄ｦ鄙呈ｩ溯・繧呈怏縺励∝柑邇・噪縺九▽菴ｿ縺医・菴ｿ縺・⊇縺ｩ邊ｾ蠎ｦ縺御ｸ翫′繧九
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\docs\01_goals.md
TYPE: *.md
---- CONTENT ----
# 繧ｷ繧ｹ繝・Β縺ｮ逶ｮ逧・
- 譌･蟶ｸ讌ｭ蜍吶・繝翫Ξ繝・ず繝吶・繧ｹ縺ｨ縺励※遏･隴倥ｒ闢・∴逧・｢ｺ縺ｪ繧｢繝峨ヰ繧､繧ｹ繧定｡後≧縲・
- 蜉ｹ邇・喧繝ｻ閾ｪ蜍募喧縺ｫ繧医ｊ譎る俣繧呈砂蜃ｺ縺吶ｋ縺薙→縺後〒縺阪∵怙鬮倥・繝ｯ繝ｼ繧ｯ繝ｩ繧､繝輔ヰ繝ｩ繝ｳ繧ｹ繧呈焔縺ｫ蜈･繧後ｋ縲
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\docs\02_tasks.md
TYPE: *.md
---- CONTENT ----
# 02_tasks.md
# 莉｣陦後＆縺帙◆縺・ｻ穂ｺ倶ｸ隕ｧ・磯ｲ蛹也沿・・

譛ｬ繝峨く繝･繝｡繝ｳ繝医・縲∵悽繧ｷ繧ｹ繝・Β縺御ｻ｣陦後☆繧倶ｻ穂ｺ九ｒ謨ｴ逅・＠縲・
蜷・ち繧ｹ繧ｯ繧偵←縺ｮ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医′諡・ｽ薙☆繧九°繧呈・遒ｺ縺ｫ縺吶ｋ縺溘ａ縺ｮ荳隕ｧ縺ｧ縺ゅｋ縲・

繧ｿ繧ｹ繧ｯ縺ｯ莉･荳九・隕ｳ轤ｹ縺ｧ謨ｴ逅・☆繧九・
- 遞ｮ鬘・ 蛻､譁ｭ邉ｻ / 菴懈･ｭ邉ｻ / 豺ｷ蜷・
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・
- 蜈･蜉帙→蜃ｺ蜉・
- 陬懆ｶｳ莠矩・ｼ井ｺｺ髢謎ｻ句・繝昴う繝ｳ繝医↑縺ｩ・・

---

## 1. 譌･蟶ｸ讌ｭ蜍咎未騾｣

### 1-1. 繝翫Ξ繝・ず繝吶・繧ｹ逕滓・
- 遞ｮ鬘・ 蛻､譁ｭ邉ｻ
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・ KnowledgeAgent
- 蜈･蜉・
  - 繝｡繝ｼ繝ｫ譛ｬ譁・
  - 豺ｻ莉倩ｳ・侭・・DF / Word / Excel・・
  - 繝√Ε繝・ヨ繝ｭ繧ｰ
- 蜃ｺ蜉・
  - Markdown蠖｢蠑上・繝翫Ξ繝・ず險倅ｺ・
  - 繧ｿ繧ｰ繝ｻ繧ｫ繝・ざ繝ｪ諠・ｱ
  - 鬘樔ｼｼ繝翫Ξ繝・ず縺ｸ縺ｮ繝ｪ繝ｳ繧ｯ
- 蜀・ｮｹ:
  - 讌ｭ蜍咏衍隴倥ｒ蜀榊茜逕ｨ蜿ｯ閭ｽ縺ｪ蠖｢縺ｫ謨ｴ逅・☆繧・
  - 諠・ｱ縺ｮ驥崎､・ｒ謗帝勁縺励∵歓雎｡蛹悶Ξ繝吶Ν繧定ｪｿ謨ｴ縺吶ｋ
- 陬懆ｶｳ:
  - 蛻晄悄縺ｯ莠ｺ髢薙↓繧医ｋ繝ｬ繝薙Η繝ｼ蜑肴署
  - 閾ｪ蜍募・髢九・陦後ｏ縺ｪ縺・

---

### 1-2. 繝医Λ繝悶Ν蟇ｾ蠢懊リ繝ｬ繝・ず蛹・
- 遞ｮ鬘・ 蛻､譁ｭ邉ｻ
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・ KnowledgeAgent
- 蜈･蜉・
  - 髫懷ｮｳ蟇ｾ蠢懆ｨ倬鹸
  - 蝠上＞蜷医ｏ縺帛ｱ･豁ｴ
  - 蟇ｾ蠢懃ｵ先棡
- 蜃ｺ蜉・
  - 繝医Λ繝悶Ν蟇ｾ蠢懊リ繝ｬ繝・ず
  - 鬘樔ｼｼ譯井ｻｶ繝ｪ繧ｹ繝・
  - 謗ｨ螂ｨ蟇ｾ蠢懈焔鬆・
- 蜀・ｮｹ:
  - 驕主悉莠倶ｾ九→縺ｮ鬘樔ｼｼ蠎ｦ蛻､螳・
  - 蜀咲匱髦ｲ豁｢隕ｳ轤ｹ縺ｧ縺ｮ謨ｴ逅・
- 陬懆ｶｳ:
  - 蛻､譁ｭ縺ｫ霑ｷ縺・こ繝ｼ繧ｹ縺ｯ莠ｺ髢薙↓繧ｨ繧ｹ繧ｫ繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ

---

### 1-3. 讌ｭ蜍呵・蜍募喧・・xcel謫堺ｽ懶ｼ・
- 遞ｮ鬘・ 菴懈･ｭ邉ｻ
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・ AutomationAgent
- 蜈･蜉・
  - Excel繝輔ぃ繧､繝ｫ
  - 謫堺ｽ懈焔鬆・ｮ夂ｾｩ
- 蜃ｺ蜉・
  - 蜉蟾･貂医∩Excel繝輔ぃ繧､繝ｫ
  - 螳溯｡後Ο繧ｰ
- 蜀・ｮｹ:
  - 螳壼梛逧・↑Excel謫堺ｽ懊ｒPython縺ｧ閾ｪ蜍募ｮ溯｡・
- 陬懆ｶｳ:
  - 蛻､譁ｭ縺ｯ陦後ｏ縺ｪ縺・
  - 螟ｱ謨玲凾縺ｯ繝ｭ繧ｰ繧定ｿ泌唆縺吶ｋ縺ｮ縺ｿ

---

### 1-4. 謇矩・嶌菴懈・
- 遞ｮ鬘・ 豺ｷ蜷茨ｼ亥愛譁ｭ + 譁・ｫ逕滓・・・
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・ KnowledgeAgent
- 陬懷勧繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝・ ReviewAgent・亥ｰ・擂・・
- 蜈･蜉・
  - 讌ｭ蜍吝・螳ｹ隱ｬ譏・
  - 譌｢蟄倩ｳ・侭
- 蜃ｺ蜉・
  - Markdown蠖｢蠑上・謇矩・嶌
- 蜀・ｮｹ:
  - 螻樔ｺｺ蛹悶＠繧・☆縺・･ｭ蜍吶ｒ蠖｢蠑冗衍蛹悶☆繧・
  - 隱ｰ縺瑚ｦ九※繧ょ・迴ｾ縺ｧ縺阪ｋ讒区・縺ｫ縺吶ｋ
- 陬懆ｶｳ:
  - 陦ｨ迴ｾ縺ｮ譛邨ら｢ｺ隱阪・莠ｺ髢薙′陦後≧

---

### 1-5. 繧ｿ繧ｹ繧ｯ邂｡逅・
- 遞ｮ鬘・ 蛻､譁ｭ邉ｻ
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・ PlanningAgent
- 蜈･蜉・
  - 繧ｿ繧ｹ繧ｯ蜀・ｮｹ
  - 譛滄剞
  - 蜆ｪ蜈亥ｺｦ
- 蜃ｺ蜉・
  - 繧ｿ繧ｹ繧ｯ繝ｪ繧ｹ繝・
  - 騾ｲ謐礼憾豕・
  - 繧｢繝ｩ繝ｼ繝磯夂衍
- 蜀・ｮｹ:
  - 譌･縲・・讌ｭ蜍吶ち繧ｹ繧ｯ繧堤ｮ｡逅・☆繧・
  - 驕・ｻｶ繧・℃雋闕ｷ繧呈､懃衍縺吶ｋ
- 陬懆ｶｳ:
  - 蜆ｪ蜈亥ｺｦ蛻､譁ｭ縺ｯ繝ｫ繝ｼ繝ｫ繝吶・繧ｹ縺九ｉ髢句ｧ・

---

## 2. 蜑ｯ讌ｭ髢｢騾｣

### 2-1. 繝医Ξ繝ｳ繝峨し繝ｼ繝√→雉ｼ蜈･繝ｻ螢ｲ萓｡謠先｡・
- 遞ｮ鬘・ 蛻､譁ｭ邉ｻ
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・ BusinessSupportAgent
- 蜈･蜉・
  - 蟶ょｴ繝・・繧ｿ
  - 繝医Ξ繝ｳ繝画ュ蝣ｱ
  - 驕主悉縺ｮ雋ｩ螢ｲ螳溽ｸｾ
- 蜃ｺ蜉・
  - 莉募・繧悟呵｣懊Μ繧ｹ繝・
  - 諠ｳ螳壼｣ｲ萓｡繝ｬ繝ｳ繧ｸ
  - 蛻ｩ逶願ｦ玖ｾｼ縺ｿ縺ｨ繝ｪ繧ｹ繧ｯ
- 蜀・ｮｹ:
  - 繝医Ξ繝ｳ繝画ｧ縺ｮ蛻・梵
  - 蛻ｩ逶翫′蜃ｺ繧句庄閭ｽ諤ｧ縺ｮ險隱槫喧
- 陬懆ｶｳ:
  - 譛邨ょ愛譁ｭ縺ｯ莠ｺ髢薙′陦後≧
  - 閾ｪ蜍慕匱豕ｨ縺ｯ陦後ｏ縺ｪ縺・

---

### 2-2. 蝨ｨ蠎ｫ邂｡逅・・邨檎炊邂｡逅・
- 遞ｮ鬘・ 菴懈･ｭ邉ｻ
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・ AutomationAgent
- 蜈･蜉・
  - 蝨ｨ蠎ｫ繝・・繧ｿ
  - 蜿門ｼ輔ョ繝ｼ繧ｿ
- 蜃ｺ蜉・
  - 蝨ｨ蠎ｫ荳隕ｧ
  - 邨檎炊髮・ｨ育ｵ先棡
- 蜀・ｮｹ:
  - 蝨ｨ蠎ｫ謨ｰ繝ｻ螢ｲ荳翫・蛻ｩ逶翫・邂｡逅・
- 陬懆ｶｳ:
  - 謨ｰ蛟､縺ｮ蛻､譁ｭ繝ｻ隧穂ｾ｡縺ｯ陦後ｏ縺ｪ縺・

---

## 3. 蜈ｨ闊ｬ讖溯・

### 3-1. 閾ｪ蟾ｱ蟄ｦ鄙呈ｩ溯・
- 遞ｮ鬘・ 蛻､譁ｭ邉ｻ・亥宛髯蝉ｻ倥″・・
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝・ LearningAgent
- 蜈･蜉・
  - 蜷・お繝ｼ繧ｸ繧ｧ繝ｳ繝医・螳溯｡後Ο繧ｰ
  - 謌仙粥繝ｻ螟ｱ謨怜ｱ･豁ｴ
- 蜃ｺ蜉・
  - 謾ｹ蝟・署譯・
  - 繝ｫ繝ｼ繝ｫ菫ｮ豁｣譯・
  - 繝励Ο繝ｳ繝励ヨ謾ｹ蝟・｡・
- 蜀・ｮｹ:
  - 驕主悉縺ｮ邨先棡縺九ｉ蛯ｾ蜷代ｒ蛻・梵縺吶ｋ
- 陬懆ｶｳ:
  - 繧ｷ繧ｹ繝・Β縺ｸ縺ｮ閾ｪ蜍募渚譏縺ｯ遖∵ｭ｢
  - 蠢・★莠ｺ髢薙・謇ｿ隱阪ｒ邨後ｋ

---

## 4. 蜈ｱ騾壽婿驥・
- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医・縲悟愛譁ｭ繧剃ｼｴ縺・ｲｬ蜍吶阪ｒ謖√▽繧ゅ・縺ｨ縺吶ｋ
- 蜊倡ｴ比ｽ懈･ｭ縺ｯ繝・・繝ｫ縺ｾ縺溘・髢｢謨ｰ縺ｨ縺励※螳溯｣・☆繧・
- 閾ｪ蠕句ｮ溯｡後ｈ繧翫ｂ縲梧署譯医→陬懷勧縲阪ｒ蜆ｪ蜈医☆繧・
- 縺吶∋縺ｦ縺ｮ蜃ｦ逅・・繝ｭ繧ｰ縺ｨ縺励※險倬鹸縺吶ｋ
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\docs\03_architecture.md
TYPE: *.md
---- CONTENT ----
# 03_architecture.md
# 蜈ｨ菴薙い繝ｼ繧ｭ繝・け繝√Ε險ｭ險・

譛ｬ繝峨く繝･繝｡繝ｳ繝医・縲∵悽繧ｷ繧ｹ繝・Β縺ｫ縺翫￠繧句・菴捺ｧ区・繧定ｨ隱槫喧縺励・
蜷・さ繝ｳ繝昴・繝阪Φ繝医・蠖ｹ蜑ｲ縺ｨ雋ｬ莉ｻ遽・峇繧呈・遒ｺ縺ｫ縺吶ｋ縺薙→繧堤岼逧・→縺吶ｋ縲・

譛ｬ繧ｷ繧ｹ繝・Β縺ｯ縲御ｺｺ髢薙・莉｣繧上ｊ縺ｫ閠・∴縲∽ｽ懈･ｭ繧定｣懷勧繝ｻ莉｣陦後☆繧九阪％縺ｨ繧堤岼逧・→縺励・
螳悟・閾ｪ蠕九〒縺ｯ縺ｪ縺上∽ｺｺ髢謎ｸｻ蟆弱・AI陬懷勧繧貞渕譛ｬ譁ｹ驥昴→縺吶ｋ縲・

---

## 1. 蜈ｨ菴捺ｧ区・縺ｮ讎りｦ・

譛ｬ繧ｷ繧ｹ繝・Β縺ｯ莉･荳九・4螻､讒矩縺ｧ讒区・縺輔ｌ繧九・

1. 繧､繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ螻､
2. 繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｷ繝ｧ繝ｳ螻､
3. 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥ｱ､
4. 繝・・繝ｫ繝ｻ繝・・繧ｿ螻､

蜷・ｱ､縺ｯ雋ｬ蜍吶ｒ譏守｢ｺ縺ｫ蛻・屬縺励∫峩謗･逧・↑萓晏ｭ倥ｒ譛蟆城剞縺ｫ謚代∴繧九・

---

## 2. 繧､繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ螻､・・nterface Layer・・

### 蠖ｹ蜑ｲ
- 莠ｺ髢薙→縺ｮ謗･轤ｹ繧呈球縺・
- 謖・､ｺ縲∫｢ｺ隱阪∫ｵ先棡謠千､ｺ繧定｡後≧

### 諠ｳ螳壹う繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ
- CLI
- Web UI・亥ｰ・擂・・
- 繝√Ε繝・ヨUI・亥ｰ・擂・・

### 迚ｹ蠕ｴ
- 讌ｭ蜍吶Ο繧ｸ繝・け繧呈戟縺溘↑縺・
- 縺吶∋縺ｦ縺ｮ蜃ｦ逅・ｦ∵ｱゅ・繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｷ繝ｧ繝ｳ螻､縺ｸ貂｡縺・
- 莠ｺ髢薙↓繧医ｋ謇ｿ隱阪・蜊ｴ荳九ｒ譏守､ｺ逧・↓蜿励￠莉倥￠繧・

---

## 3. 繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｷ繝ｧ繝ｳ螻､・・rchestration Layer・・

### 荳ｭ譬ｸ繧ｳ繝ｳ繝昴・繝阪Φ繝・
- OrchestratorAgent

### 蠖ｹ蜑ｲ
- 蜃ｦ逅・・菴薙・豬√ｌ繧貞宛蠕｡縺吶ｋ
- 蜷・お繝ｼ繧ｸ繧ｧ繝ｳ繝医∈縺ｮ萓晞ｼ繝ｻ邨先棡蝗槫庶繧定｡後≧
- 莠ｺ髢謎ｻ句・縺悟ｿ・ｦ√↑繝昴う繝ｳ繝医ｒ蛻､譁ｭ縺吶ｋ

### OrchestratorAgent縺ｮ雋ｬ蜍・
- 繧ｿ繧ｹ繧ｯ縺ｮ蜿嶺ｻ・
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝医・驕ｸ螳・
- 螳溯｡碁・ｺ上・蛻ｶ蠕｡
- 萓句､也匱逕滓凾縺ｮ蛻ｶ蠕｡
- 繝ｭ繧ｰ縺ｮ髮・ｴ・

### 陬懆ｶｳ
- OrchestratorAgent閾ｪ霄ｫ縺ｯ蟆る摩蛻､譁ｭ繧定｡後ｏ縺ｪ縺・
- 蛻､譁ｭ縺ｯ蠢・★蟆る摩繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医↓蟋碑ｭｲ縺吶ｋ

---

## 4. 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥ｱ､・・gent Layer・・

### 蝓ｺ譛ｬ譁ｹ驥・
- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医・縲悟愛譁ｭ繧剃ｼｴ縺・ｲｬ蜍吶阪ｒ謖√▽
- 迥ｶ諷具ｼ域枚閼医・螻･豁ｴ・峨ｒ菫晄戟縺吶ｋ
- 蜊倡ｴ比ｽ懈･ｭ縺ｯ陦後ｏ縺ｪ縺・

### 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝井ｸ隕ｧ

#### 4-1. KnowledgeAgent
- 遏･隴倥・逕滓・繝ｻ謨ｴ逅・・讀懃ｴ｢繧呈球蠖・
- 諠・ｱ繧貞・蛻ｩ逕ｨ蜿ｯ閭ｽ縺ｪ蠖｢縺ｫ螟画鋤縺吶ｋ
- 繝翫Ξ繝・ず繝吶・繧ｹ縲∵焔鬆・嶌縲√ヨ繝ｩ繝悶Ν莠倶ｾ九ｒ謇ｱ縺・

#### 4-2. AutomationAgent
- 螳壼梛菴懈･ｭ縺ｮ螳溯｡後ｒ諡・ｽ・
- Excel謫堺ｽ懊∝惠蠎ｫ邂｡逅・∫ｵ檎炊蜃ｦ逅・↑縺ｩ繧呈桶縺・
- 蛻､譁ｭ縺ｯ陦後ｏ縺壹∵・蜉溘・螟ｱ謨励ｒ邨先棡縺ｨ縺励※霑斐☆

#### 4-3. PlanningAgent
- 繧ｿ繧ｹ繧ｯ邂｡逅・・蜆ｪ蜈亥ｺｦ蛻､譁ｭ繧呈球蠖・
- 邱繧∝・繧翫・ｲ謐励∬ｲ闕ｷ繧堤屮隕悶☆繧・
- 繝ｫ繝ｼ繝ｫ繝吶・繧ｹ縺九ｉ髢句ｧ九＠縲∝ｰ・擂逧・↓鬮伜ｺｦ蛹門庄閭ｽ

#### 4-4. BusinessSupportAgent
- 蜑ｯ讌ｭ謾ｯ謠ｴ繧呈球蠖・
- 繝医Ξ繝ｳ繝牙・譫舌∽ｻ募・繧悟呵｣懊∝｣ｲ萓｡謠先｡医ｒ陦後≧
- 繝ｪ繧ｹ繧ｯ繧定ｨ隱槫喧縺励∽ｺｺ髢薙・諢乗晄ｱｺ螳壹ｒ陬懷勧縺吶ｋ

#### 4-5. LearningAgent
- 繧ｷ繧ｹ繝・Β蜈ｨ菴薙・謖ｯ繧願ｿ斐ｊ繧呈球蠖・
- 謌仙粥繝ｻ螟ｱ謨励Ο繧ｰ縺九ｉ謾ｹ蝟・｡医ｒ逕滓・縺吶ｋ
- 閾ｪ蜍募渚譏縺ｯ遖∵ｭ｢縺励∵署譯医・縺ｿ繧定｡後≧

---

## 5. 繝・・繝ｫ繝ｻ繝・・繧ｿ螻､・・ool & Data Layer・・

### 蠖ｹ蜑ｲ
- 螳滄圀縺ｮ菴懈･ｭ繝ｻ繝・・繧ｿ蜃ｦ逅・ｒ陦後≧
- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医°繧臥峩謗･蜻ｼ縺ｳ蜃ｺ縺輔ｌ繧・

### 荳ｻ縺ｪ讒区・隕∫ｴ
- Python繧ｹ繧ｯ繝ｪ繝励ヨ
- 螟夜ΚAPI
- 繝輔ぃ繧､繝ｫ謫堺ｽ懊Δ繧ｸ繝･繝ｼ繝ｫ
- 繝・・繧ｿ繝吶・繧ｹ・亥ｰ・擂・・

### 迚ｹ蠕ｴ
- 迥ｶ諷九ｒ謖√◆縺ｪ縺・
- 蜀榊茜逕ｨ蜿ｯ閭ｽ縺ｪ髢｢謨ｰ鄒､縺ｨ縺励※螳溯｣・
- 繝ｭ繧ｰ蜃ｺ蜉帙ｒ蠢・医→縺吶ｋ

---

## 6. 繝・・繧ｿ縺ｨ繝ｭ繧ｰ縺ｮ豬√ｌ

### 蝓ｺ譛ｬ譁ｹ驥・
- 縺吶∋縺ｦ縺ｮ蜃ｦ逅・・繝ｭ繧ｰ縺ｨ縺励※險倬鹸縺吶ｋ
- 蛻､譁ｭ縺ｮ譬ｹ諡繧貞ｾ後°繧芽ｿｽ霍｡縺ｧ縺阪ｋ繧医≧縺ｫ縺吶ｋ

### 繝ｭ繧ｰ縺ｮ遞ｮ鬘・
- 螳溯｡後Ο繧ｰ
- 蛻､譁ｭ繝ｭ繧ｰ
- 繧ｨ繝ｩ繝ｼ繝ｻ萓句､悶Ο繧ｰ
- 莠ｺ髢捺価隱阪Ο繧ｰ

### 繝ｭ繧ｰ縺ｮ蛻ｩ逕ｨ蜈・
- LearningAgent縺ｫ繧医ｋ蛻・梵
- 繝医Λ繝悶Ν繧ｷ繝･繝ｼ繝・ぅ繝ｳ繧ｰ
- 繝翫Ξ繝・ず繝吶・繧ｹ逕滓・

---

## 7. 莠ｺ髢謎ｻ句・繝昴う繝ｳ繝・

莉･荳九・蝣ｴ蜷医・蠢・★莠ｺ髢薙・遒ｺ隱阪ｒ蠢・ｦ√→縺吶ｋ縲・

- 螟夜Κ縺ｸ縺ｮ蠖ｱ髻ｿ縺後≠繧句・逅・
- 驥鷹姦繧剃ｼｴ縺・愛譁ｭ
- 閾ｪ蟾ｱ蟄ｦ鄙偵↓繧医ｋ繝ｫ繝ｼ繝ｫ螟画峩
- 荳咲｢ｺ螳滓ｧ縺碁ｫ倥＞蛻､譁ｭ

---

## 8. 險ｭ險井ｸ翫・驥崎ｦ∵婿驥・

- 螳悟・閾ｪ蠕九ｒ逶ｮ謖・＆縺ｪ縺・
- 蛻､譁ｭ雋ｬ蜍吶ｒ譏守｢ｺ縺ｫ蛻・屬縺吶ｋ
- 蟆上＆縺丈ｽ懊ｊ縲∝｣翫＠縺ｪ縺後ｉ閧ｲ縺ｦ繧・
- 險ｭ險医ラ繧ｭ繝･繝｡繝ｳ繝医→繧ｳ繝ｼ繝峨ｒ蟶ｸ縺ｫ蜷梧悄縺輔○繧・

---

## 9. 莉雁ｾ後・諡｡蠑ｵ菴吝慍

- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医・邏ｰ蛻・喧
- Web UI縺ｮ霑ｽ蜉
- 螟夜Κ繧ｵ繝ｼ繝薙せ騾｣謳ｺ
- 閾ｪ辟ｶ險隱槭↓繧医ｋ謖・､ｺ縺ｮ鬮伜ｺｦ蛹・
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\docs\04_agents.md
TYPE: *.md
---- CONTENT ----
# 04_agents.md
# 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・

譛ｬ繝峨く繝･繝｡繝ｳ繝医・縲∵悽繧ｷ繧ｹ繝・Β繧呈ｧ区・縺吶ｋ蜷・お繝ｼ繧ｸ繧ｧ繝ｳ繝医↓縺､縺・※縲・
雋ｬ蜍吶・蛻､譁ｭ遽・峇繝ｻ菫晄戟迥ｶ諷九・繝・・繧ｿ繝吶・繧ｹ縺ｨ縺ｮ髢｢菫ゅｒ譏守｢ｺ縺ｫ螳夂ｾｩ縺吶ｋ縲・

繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医・縲悟愛譁ｭ繧剃ｼｴ縺・ｲｬ蜍吶阪ｒ謖√▽蜊倅ｽ阪→縺励・
蜊倡ｴ比ｽ懈･ｭ縺ｯ繝・・繝ｫ縺ｾ縺溘・髢｢謨ｰ縺ｫ蟋碑ｭｲ縺吶ｋ縲・

---

## 1. 蜈ｱ騾夊ｨｭ險域婿驥・

### 1-1. 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医・螳夂ｾｩ
- 蛻､譁ｭ繧定｡後≧
- 譁・ц繧・ｱ･豁ｴ繧堤憾諷九→縺励※菫晄戟縺吶ｋ
- 閾ｪ霄ｫ縺ｧ逶ｴ謗･UI繧ДB繧呈桃菴懊＠縺ｪ縺・ｼ井ｾ句､悶ｒ髯､縺擾ｼ・

### 1-2. 螳溯｡檎腸蠅・燕謠・
- Windows迺ｰ蠅・〒exe縺ｨ縺励※螳溯｡・
- SQLite縺ｯ遉ｾ蜀・・譛峨し繝ｼ繝舌↓驟咲ｽｮ
- 蜷梧凾譖ｸ縺崎ｾｼ縺ｿ繧呈･ｵ蜉幃∩縺代ｋ險ｭ險医→縺吶ｋ

### 1-3. 繝・・繧ｿ繧｢繧ｯ繧ｻ繧ｹ蜴溷援
- DB縺ｸ縺ｮ逶ｴ謗･譖ｸ縺崎ｾｼ縺ｿ縺ｯ髯仙ｮ壹＆繧後◆繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医・縺ｿ縺瑚｡後≧
- 隱ｭ縺ｿ蜿悶ｊ縺ｯ蜈ｨ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥庄閭ｽ
- 譖ｸ縺崎ｾｼ縺ｿ縺ｯ OrchestratorAgent 繧堤ｵ檎罰縺吶ｋ

---

## 2. OrchestratorAgent

### 蠖ｹ蜑ｲ
- 繧ｷ繧ｹ繝・Β蜈ｨ菴薙・蜿ｸ莉､蝪・
- 蜷・お繝ｼ繧ｸ繧ｧ繝ｳ繝医∈縺ｮ萓晞ｼ縺ｨ邨先棡縺ｮ邨ｱ蜷・

### 蛻､譁ｭ遽・峇
- 繧ｿ繧ｹ繧ｯ縺ｮ遞ｮ鬘槫愛螳・
- 荳ｻ諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝医・驕ｸ螳・
- 莠ｺ髢謎ｻ句・縺ｮ隕∝凄蛻､譁ｭ

### 菫晄戟迥ｶ諷・
- 迴ｾ蝨ｨ蜃ｦ逅・ｸｭ縺ｮ繧ｿ繧ｹ繧ｯID
- 螳溯｡御ｸｭ繝輔Ο繝ｼ縺ｮ騾ｲ謐・
- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥他縺ｳ蜃ｺ縺怜ｱ･豁ｴ

### DB縺ｨ縺ｮ髢｢菫・
- 蜴溷援縺ｨ縺励※隱ｭ縺ｿ蜿悶ｊ縺ｮ縺ｿ
- 譖ｸ縺崎ｾｼ縺ｿ縺ｯ蜷・球蠖薙お繝ｼ繧ｸ繧ｧ繝ｳ繝医↓蟋碑ｭｲ

---

## 3. KnowledgeAgent

### 蠖ｹ蜑ｲ
- 遏･隴倥・逕滓・繝ｻ謨ｴ逅・・讀懃ｴ｢
- 繝翫Ξ繝・ず繝吶・繧ｹ縺翫ｈ縺ｳ謇矩・嶌縺ｮ荳ｭ譬ｸ

### 蟇ｾ蠢懊ち繧ｹ繧ｯ
- 繝翫Ξ繝・ず繝吶・繧ｹ逕滓・
- 繝医Λ繝悶Ν蟇ｾ蠢懊リ繝ｬ繝・ず蛹・
- 謇矩・嶌菴懈・

### 蛻､譁ｭ遽・峇
- 諠・ｱ縺ｮ蜿匁昏驕ｸ謚・
- 謚ｽ雎｡蛹悶Ξ繝吶Ν縺ｮ隱ｿ謨ｴ
- 鬘樔ｼｼ繝翫Ξ繝・ず蛻､螳・
- 蜀榊茜逕ｨ萓｡蛟､縺ｮ譛臥┌蛻､譁ｭ

### 菫晄戟迥ｶ諷・
- 蜃ｦ逅・ｯｾ雎｡繝峨く繝･繝｡繝ｳ繝医・繝｡繧ｿ諠・ｱ
- 荳譎ら噪縺ｪ隕∫ｴ・・繧ｿ繧ｰ諠・ｱ
- 鬘樔ｼｼ讀懃ｴ｢縺ｮ邨先棡繧ｭ繝｣繝・す繝･

### DB縺ｨ縺ｮ髢｢菫・
- 隱ｭ縺ｿ蜿悶ｊ: 譌｢蟄倥リ繝ｬ繝・ず讀懃ｴ｢
- 譖ｸ縺崎ｾｼ縺ｿ: 譁ｰ隕上リ繝ｬ繝・ず逋ｻ骭ｲ・域価隱榊ｾ後・縺ｿ・・

### 蛻ｶ邏・
- 閾ｪ蜍募・髢九・遖∵ｭ｢
- 譖ｸ縺崎ｾｼ縺ｿ蜑阪↓莠ｺ髢薙Ξ繝薙Η繝ｼ繧呈検繧險ｭ險医→縺吶ｋ

---

## 4. AutomationAgent

### 蠖ｹ蜑ｲ
- 螳壼梛菴懈･ｭ縺ｮ螳溯｡・
- 讌ｭ蜍吝・逅・・閾ｪ蜍募喧

### 蟇ｾ蠢懊ち繧ｹ繧ｯ
- Excel謫堺ｽ・
- 蝨ｨ蠎ｫ邂｡逅・
- 邨檎炊邂｡逅・

### 蛻､譁ｭ遽・峇
- 蛻､譁ｭ縺ｯ陦後ｏ縺ｪ縺・
- 謌仙粥繝ｻ螟ｱ謨励・蛻､螳壹・縺ｿ

### 菫晄戟迥ｶ諷・
- 螳溯｡御ｸｭ繧ｸ繝ｧ繝匁ュ蝣ｱ
- 繧ｨ繝ｩ繝ｼ蜀・ｮｹ

### DB縺ｨ縺ｮ髢｢菫・
- 蜴溷援縺ｨ縺励※逶ｴ謗･謫堺ｽ懊＠縺ｪ縺・
- 蠢・ｦ√↑繝・・繧ｿ縺ｯ OrchestratorAgent 邨檎罰縺ｧ蜿励￠蜿悶ｋ

### 迚ｹ蠕ｴ
- 蜀ｪ遲画ｧ繧帝㍾隕・
- 蜷後§蜃ｦ逅・ｒ菴募ｺｦ螳溯｡後＠縺ｦ繧ょ撫鬘後′襍ｷ縺阪↑縺・ｨｭ險・

---

## 5. PlanningAgent

### 蠖ｹ蜑ｲ
- 繧ｿ繧ｹ繧ｯ邂｡逅・・騾ｲ謐礼ｮ｡逅・
- 蜆ｪ蜈亥ｺｦ縺ｮ蛻､譁ｭ

### 蟇ｾ蠢懊ち繧ｹ繧ｯ
- 譌･蟶ｸ讌ｭ蜍吶ち繧ｹ繧ｯ邂｡逅・
- 邱繧∝・繧顔ｮ｡逅・
- 驕・ｻｶ讀懃衍

### 蛻､譁ｭ遽・峇
- 蜆ｪ蜈亥ｺｦ豎ｺ螳・
- 繧ｿ繧ｹ繧ｯ蜀埼・鄂ｮ
- 莠ｺ髢薙∈縺ｮ繧｢繝ｩ繝ｼ繝郁ｦ∝凄

### 菫晄戟迥ｶ諷・
- 繧ｿ繧ｹ繧ｯ繝ｪ繧ｹ繝・
- 騾ｲ謐怜ｱ･豁ｴ
- 驕主悉縺ｮ驕・ｻｶ繝代ち繝ｼ繝ｳ

### DB縺ｨ縺ｮ髢｢菫・
- 隱ｭ縺ｿ蜿悶ｊ: 繧ｿ繧ｹ繧ｯ諠・ｱ
- 譖ｸ縺崎ｾｼ縺ｿ: 迥ｶ諷区峩譁ｰ・井ｽ朱ｻ蠎ｦ・・

---

## 6. BusinessSupportAgent

### 蠖ｹ蜑ｲ
- 蜑ｯ讌ｭ謾ｯ謠ｴ蟆ら畑繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝・

### 蟇ｾ蠢懊ち繧ｹ繧ｯ
- 繝医Ξ繝ｳ繝峨し繝ｼ繝・
- 莉募・繧悟呵｣懈歓蜃ｺ
- 螢ｲ萓｡繝ｬ繝ｳ繧ｸ謠先｡・

### 蛻､譁ｭ遽・峇
- 繝医Ξ繝ｳ繝画ｧ縺ｮ譛臥┌
- 蛻ｩ逶雁庄閭ｽ諤ｧ
- 繝ｪ繧ｹ繧ｯ隕∝屏縺ｮ險隱槫喧

### 菫晄戟迥ｶ諷・
- 蟶ょｴ繝・・繧ｿ縺ｮ荳譎ゅく繝｣繝・す繝･
- 驕主悉縺ｮ蛻､譁ｭ邨先棡

### DB縺ｨ縺ｮ髢｢菫・
- 蛟倶ｺｺ鬆伜沺縺ｮ縺ｿ菴ｿ逕ｨ
- 遉ｾ蜀・リ繝ｬ繝・ずDB縺ｨ縺ｯ隲也炊逧・↓蛻・屬

### 蛻ｶ邏・
- 讌ｭ蜍吶Θ繝ｼ繧ｶ縺九ｉ縺ｯ蛻ｩ逕ｨ荳榊庄
- 閾ｪ蜍戊ｳｼ蜈･繝ｻ逋ｺ豕ｨ縺ｯ遖∵ｭ｢

---

## 7. LearningAgent

### 蠖ｹ蜑ｲ
- 繧ｷ繧ｹ繝・Β蜈ｨ菴薙・謾ｹ蝟・署譯・

### 蟇ｾ蠢懊ち繧ｹ繧ｯ
- 螳溯｡後Ο繧ｰ蛻・梵
- 謌仙粥繝ｻ螟ｱ謨励ヱ繧ｿ繝ｼ繝ｳ謚ｽ蜃ｺ
- 謾ｹ蝟・｡育函謌・

### 蛻､譁ｭ遽・峇
- 蛯ｾ蜷大・譫・
- 繝ｫ繝ｼ繝ｫ繝ｻ繝励Ο繝ｳ繝励ヨ謾ｹ蝟・｡井ｽ懈・

### 菫晄戟迥ｶ諷・
- 繝ｭ繧ｰ蛻・梵邨先棡
- 謠先｡亥ｱ･豁ｴ

### DB縺ｨ縺ｮ髢｢菫・
- 隱ｭ縺ｿ蜿悶ｊ蟆ら畑
- 譖ｸ縺崎ｾｼ縺ｿ縺ｯ遖∵ｭ｢

### 蛻ｶ邏・
- 繧ｷ繧ｹ繝・Β縺ｸ縺ｮ閾ｪ蜍募渚譏縺ｯ遖∵ｭ｢
- 蠢・★莠ｺ髢捺価隱阪ｒ蠢・ｦ√→縺吶ｋ

---

## 8. 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝磯俣騾｣謳ｺ繝ｫ繝ｼ繝ｫ

- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥酔螢ｫ縺ｯ逶ｴ謗･騾壻ｿ｡縺励↑縺・
- 縺吶∋縺ｦ OrchestratorAgent 繧剃ｻ九☆繧・
- 繝・・繧ｿ蜿励￠貂｡縺励・JSON蠖｢蠑上ｒ蝓ｺ譛ｬ縺ｨ縺吶ｋ

---

## 9. 莉雁ｾ後・諡｡蠑ｵ謖・・

- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医・邏ｰ蛻・喧縺ｯ雋ｬ蜍吶′閧･螟ｧ蛹悶＠縺滓凾轤ｹ縺ｧ陦後≧
- DB雋闕ｷ縺悟｢励∴縺溷ｴ蜷医・繧ｵ繝ｼ繝仙梛DB縺ｸ遘ｻ陦悟庄閭ｽ縺ｪ讒矩繧堤ｶｭ謖√☆繧・
- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医・蜈･繧梧崛縺医ｒ蜑肴署縺ｨ縺励◆逍守ｵ仙粋險ｭ險医ｒ菫昴▽
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\docs\05_agent_protocol.md
TYPE: *.md
---- CONTENT ----
# 05_agent_protocol.md
# 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝磯俣 JSON 萓晞ｼ繝輔か繝ｼ繝槭ャ繝亥ｮ夂ｾｩ

譛ｬ繝峨く繝･繝｡繝ｳ繝医・縲＾rchestratorAgent 縺ｨ蜷・お繝ｼ繧ｸ繧ｧ繝ｳ繝磯俣縺ｧ菴ｿ逕ｨ縺吶ｋ
JSON蠖｢蠑上・萓晞ｼ繝ｻ蠢懃ｭ斐・繝ｭ繝医さ繝ｫ繧貞ｮ夂ｾｩ縺吶ｋ縲・

譛ｬ繝励Ο繝医さ繝ｫ縺ｮ逶ｮ逧・・莉･荳九・騾壹ｊ縺ｧ縺ゅｋ縲・
- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝磯俣縺ｮ逍守ｵ仙粋繧堤ｶｭ謖√☆繧・
- 繝ｭ繧ｰ繝ｻ繝医Λ繝悶Ν隗｣譫舌ｒ螳ｹ譏薙↓縺吶ｋ
- 蟆・擂縺ｮ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥ｷｮ縺玲崛縺医ｒ蜿ｯ閭ｽ縺ｫ縺吶ｋ

---

## 1. 蝓ｺ譛ｬ譁ｹ驥・

- 縺吶∋縺ｦ縺ｮ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥他縺ｳ蜃ｺ縺励・ OrchestratorAgent 繧剃ｻ九☆繧・
- 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥酔螢ｫ縺ｯ逶ｴ謗･騾壻ｿ｡縺励↑縺・
- 萓晞ｼ繝ｻ蠢懃ｭ斐・ JSON 縺ｮ縺ｿ縺ｧ陦後≧
- 1萓晞ｼ = 1蛻､譁ｭ or 1菴懈･ｭ 繧貞次蜑・→縺吶ｋ

---

## 2. 蜈ｱ騾哽SON讒矩・・equest・・

縺吶∋縺ｦ縺ｮ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝井ｾ晞ｼ縺ｯ莉･荳九・蜈ｱ騾壽ｧ矩繧呈戟縺､縲・

```json
{
  "request_id": "uuid",
  "timestamp": "2025-01-01T10:00:00",
  "from": "OrchestratorAgent",
  "to": "KnowledgeAgent",
  "task_type": "knowledge.generate",
  "priority": "normal",
  "user_context": {
    "user_id": "windows_login_name",
    "role": "knowledge_user"
  },
  "input": {},
  "constraints": {},
  "options": {}
}
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\docs\06_rules.md
TYPE: *.md
---- CONTENT ----
# 06_orchestrator_flow.md
# OrchestratorAgent 蜃ｦ逅・ヵ繝ｭ繝ｼ・育桝莨ｼ繧ｳ繝ｼ繝会ｼ・

譛ｬ繝峨く繝･繝｡繝ｳ繝医・縲＾rchestratorAgent 縺ｮ蜀・Κ蜃ｦ逅・ヵ繝ｭ繝ｼ繧・
逍台ｼｼ繧ｳ繝ｼ繝峨→縺励※螳夂ｾｩ縺励∝ｮ溯｣・凾縺ｮ蛻､譁ｭ繝悶Ξ繧帝亟縺舌％縺ｨ繧堤岼逧・→縺吶ｋ縲・

OrchestratorAgent 縺ｯ縲悟愛譁ｭ縺ｮ蜿ｸ莉､蝪斐阪〒縺ゅｊ縲・
蟆る摩逧・愛譁ｭ繧・ｽ懈･ｭ縺ｯ蜷・お繝ｼ繧ｸ繧ｧ繝ｳ繝医↓蟋碑ｭｲ縺吶ｋ縲・

---

## 1. OrchestratorAgent 縺ｮ雋ｬ蜍吝・遒ｺ隱・

- 螟夜Κ・井ｺｺ髢薙・UI・峨°繧峨・萓晞ｼ蜿嶺ｻ・
- 繧ｿ繧ｹ繧ｯ遞ｮ蛻･縺ｮ蛻､螳・
- 諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝医・驕ｸ螳・
- 螳溯｡碁・ｺ上→萓句､門宛蠕｡
- 莠ｺ髢謎ｻ句・繝昴う繝ｳ繝医・邂｡逅・
- 繝ｭ繧ｰ縺ｮ髮・ｴ・

---

## 2. 蜈ｨ菴灘・逅・ヵ繝ｭ繝ｼ・域ｦりｦｳ・・

```text
[蜈･蜉帛女莉肋
   竊・
[繝ｪ繧ｯ繧ｨ繧ｹ繝域ｭ｣隕丞喧]
   竊・
[繧ｿ繧ｹ繧ｯ遞ｮ蛻･蛻､螳咯
   竊・
[諡・ｽ薙お繝ｼ繧ｸ繧ｧ繝ｳ繝磯∈螳咯
   竊・
[繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥ｮ溯｡珪
   竊・
[邨先棡隧穂ｾ｡]
   竊・
[莠ｺ髢謎ｻ句・蛻､螳咯
   竊・
[邨先棡霑泌唆繝ｻ繝ｭ繧ｰ菫晏ｭ肋
```
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\docs\99_notes.md
TYPE: *.md
---- CONTENT ----
## 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝域ｧ区・
OrchestratorAgent
 笏懌楳 KnowledgeAgent
    笏披楳 SQLite SELECT 蟆る摩
 笏懌楳 AutomationAgent
 笏懌楳 PlanningAgent
 笏懌楳 BusinessSupportAgent
 笏披楳 LearningAgent
## 迺ｰ蠅・燕謠舌Ν繝ｼ繝ｫ
- 螳溯｡檎腸蠅・・Windows
- 驟榊ｸ・ｽ｢蠑上・exe
- DB縺ｯSQLite・亥・譛峨し繝ｼ繝宣・鄂ｮ・・
- 蜷梧凾譖ｸ縺崎ｾｼ縺ｿ繧帝∩縺代ｋ險ｭ險医→縺吶ｋ
- 繝翫Ξ繝・ず讖溯・縺ｯ隍・焚繝ｦ繝ｼ繧ｶ蟇ｾ蠢・
- 蜑ｯ讌ｭ讖溯・縺ｯ蛟倶ｺｺ蛻ｩ逕ｨ髯仙ｮ・
## 繝輔ぃ繧､繝ｫ讒区・
Servi/
笏懌楳 main.py
笏懌楳 orchestrator.py
笏懌楳 writer.py
笏懌楳 db/
笏・ 笏懌楳 __init__.py
笏・ 笏披楳 sqlite.py
笏懌楳 agents/
笏・ 笏懌楳 __init__.py
笏・ 笏懌楳 base.py
笏・ 笏披楳 knowledge.py
笏披楳 data/
   笏披楳 app.db
## 繝・・繝悶Ν讒区・
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT,
    timestamp TEXT,
    agent TEXT,
    status TEXT,
    message TEXT
);
```
```sql
CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT,
    title TEXT,
    summary TEXT,
    markdown_body TEXT,
    created_by TEXT,
    created_at TEXT,
    approved INTEGER DEFAULT 0
);
```
## 驟榊ｸ・ｧ区・
驟榊ｸ・ヵ繧ｩ繝ｫ繝/
笏懌楳 approve.exe
笏懌楳 config.yaml   竊・笘・ｷｨ髮・庄閭ｽ
笏懌楳 data/
笏・ 笏披楳 app.db
## 繝薙Ν繝・
cd D:\work\Mywork\Servi
.\release.ps1
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\approve.spec
TYPE: *.spec
---- CONTENT ----
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cli\\approve.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['yaml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='approve',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
---- FILE END ----

---- FILE START ----
PATH: C:\Users\183025008\Documents\Servi\servi.spec
TYPE: *.spec
---- CONTENT ----
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['servi_main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['yaml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='servi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
---- FILE END ----
