from agents.base import BaseAgent

class KnowledgeAgent(BaseAgent):
    name = "KnowledgeAgent"

    def execute(self, request):
        sources = request.get("input", {}).get("sources", [])
        summary = f"{len(sources)} 件の情報から生成"

        return {
            "status": "success",
            "agent": self.name,
            "result": {
                "title": "仮ナレッジ",
                "summary": summary,
                "markdown_body": "## 本文"
            },
            "human_review_required": True
        }
