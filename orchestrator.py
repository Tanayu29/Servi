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
