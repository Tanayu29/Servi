# 05_agent_protocol.md
# エージェント間 JSON 依頼フォーマット定義

本ドキュメントは、OrchestratorAgent と各エージェント間で使用する
JSON形式の依頼・応答プロトコルを定義する。

本プロトコルの目的は以下の通りである。
- エージェント間の疎結合を維持する
- ログ・トラブル解析を容易にする
- 将来のエージェント差し替えを可能にする

---

## 1. 基本方針

- すべてのエージェント呼び出しは OrchestratorAgent を介する
- エージェント同士は直接通信しない
- 依頼・応答は JSON のみで行う
- 1依頼 = 1判断 or 1作業 を原則とする

---

## 2. 共通JSON構造（Request）

すべてのエージェント依頼は以下の共通構造を持つ。

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
