import os
import shutil
from db.sqlite import insert_knowledge, insert_log


class DropWatcherAgent:
    def __init__(self, input_dir, processed_dir, error_dir):
        self.input_dir = input_dir
        self.processed_dir = processed_dir
        self.error_dir = error_dir

        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.error_dir, exist_ok=True)

    def run_once(self):
        for fname in os.listdir(self.input_dir):
            path = os.path.join(self.input_dir, fname)
            if not os.path.isfile(path):
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                insert_knowledge(
                    title=fname,
                    content=content,
                    source="drop_folder",
                    approved=0,
                )

                shutil.move(path, os.path.join(self.processed_dir, fname))
                insert_log("INFO", f"processed file: {fname}")

            except Exception as e:
                shutil.move(path, os.path.join(self.error_dir, fname))
                insert_log("ERROR", f"{fname}: {e}")
