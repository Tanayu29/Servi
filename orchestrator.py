import uuid
import datetime
from agents.knowledge import KnowledgeAgent
from db.sqlite import insert_log

class OrchestratorAgent:

    def handle_request(self, raw_request: dict) -> dict:
        request = self._normalize_request(raw_request)

        try:
            category = self._classify_task(request)
            agent = self._select_agent(category)
            response = agent.execute(request)

            insert_log(
                request["request_id"],
                agent.name,
                response["status"],
                "execution finished"
            )

        except Exception as e:
            insert_log(
                request["request_id"],
                "OrchestratorAgent",
                "failed",
                str(e)
            )
            raise

        if response.get("human_review_required"):
            print(">>> 人間の確認が必要です")

        return response

    def _normalize_request(self, raw):
        raw["request_id"] = str(uuid.uuid4())
        raw["timestamp"] = datetime.datetime.now().isoformat()
        raw["from"] = "Interface"
        return raw

    def _classify_task(self, request):
        if request.get("task_type", "").startswith("knowledge."):
            return "knowledge"
        raise ValueError("Unsupported task")

    def _select_agent(self, category):
        if category == "knowledge":
            return KnowledgeAgent()
        raise ValueError("Agent not found")
