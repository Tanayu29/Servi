## エージェント構成
OrchestratorAgent
 ├─ KnowledgeAgent
 ├─ AutomationAgent
 ├─ PlanningAgent
 ├─ BusinessSupportAgent
 └─ LearningAgent
## 環境前提ルール
- 実行環境はWindows
- 配布形式はexe
- DBはSQLite（共有サーバ配置）
- 同時書き込みを避ける設計とする
- ナレッジ機能は複数ユーザ対応
- 副業機能は個人利用限定
## ファイル構成
Servi/
├─ main.py
├─ orchestrator.py
├─ db/
│  ├─ __init__.py
│  └─ sqlite.py
├─ agents/
│  ├─ __init__.py
│  ├─ base.py
│  └─ knowledge.py
└─ data/
   └─ app.db
## テーブル構成
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