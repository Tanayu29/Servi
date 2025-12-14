import threading
import queue
from db import sqlite

class WriterAgent:
    def __init__(self):
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def enqueue(self, action: str, payload: dict):
        self.queue.put((action, payload))

    def _run(self):
        while True:
            action, payload = self.queue.get()
            try:
                if action == "log":
                    sqlite.insert_log(**payload)
                elif action == "knowledge":
                    sqlite.insert_knowledge(**payload)
            finally:
                self.queue.task_done()
