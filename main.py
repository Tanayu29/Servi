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
