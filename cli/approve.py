import sys
import os

# =====================================
# ★ import より先にパスを通す（最重要）
# =====================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PyInstaller exe 実行時
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
    print("\n=== 未承認ナレッジ一覧 ===")

    if not items:
        print("未承認ナレッジはありません")
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
            "\n承認するIDを入力（qで終了 / rで再表示）: "
        ).strip()

        if user_input.lower() == "q":
            break
        if user_input.lower() == "r":
            continue
        if not user_input.isdigit():
            print("数値IDを入力してください")
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
            print(f">>> ナレッジ {knowledge_id} を承認しました")
        else:
            print("承認に失敗しました:", response.get("errors"))

    print("\nCLI 承認UIを終了します")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("=== 致命的エラー ===")
        traceback.print_exc()
        input("\nEnterキーで終了")
