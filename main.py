from orchestrator import OrchestratorAgent
from db.sqlite import init_db

if __name__ == "__main__":

    init_db()

    orchestrator = OrchestratorAgent()

    request = {
        "task_type": "knowledge.generate",
        "user_context": {
            "user_id": "yuya",
            "role": "knowledge_user"
        },
        "input": {
            "sources": [
                {"type": "email", "content": "障害対応しました"}
            ]
        }
    }

    response = orchestrator.handle_request(request)

    print(response)
