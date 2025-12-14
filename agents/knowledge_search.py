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
