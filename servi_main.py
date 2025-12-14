import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from orchestrator import OrchestratorAgent
from agents.drop_watcher import DropWatcherAgent
from config.loader import load_config
from db.sqlite import init_db


def main():
    print("=== Servi 起動中 ===")

    config = load_config()
    init_db()

    watcher = DropWatcherAgent(
        input_dir=os.path.join(BASE_DIR, "input"),
        processed_dir=os.path.join(BASE_DIR, "processed"),
        error_dir=os.path.join(BASE_DIR, "error"),
    )

    print("Dropフォルダ監視を開始")

    while True:
        watcher.run_once()
        time.sleep(5)


if __name__ == "__main__":
    main()
