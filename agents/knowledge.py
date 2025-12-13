from agents.base import BaseAgent
from db.sqlite import insert_knowledge

class KnowledgeAgent(BaseAgent):
    name = "KnowledgeAgent"

    def execute(self, request: dict) -> dict:
        sources = request.get("input", {}).get("sources", [])
        user = request.get("user_context", {}).get("user_id", "unknown")

        summary = f"{len(sources)} 件の情報からナレッジを生成しました"

        result = {
            "title": "仮ナレッジ",
            "summary": summary,
            "markdown_body": "## 概要\nここに本文が入ります"
        }

        insert_knowledge(
            request_id=request["request_id"],
            title=result["title"],
            summary=result["summary"],
            body=result["markdown_body"],
            user=user
        )

        return {
            "request_id": request["request_id"],
            "status": "success",
            "agent": self.name,
            "result": result,
            "human_review_required": True,
            "warnings": [],
            "errors": [],
            "logs": ["knowledge saved"]
        }
