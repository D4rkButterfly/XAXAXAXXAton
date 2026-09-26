import json, uuid, os

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")


STORE_PATH = os.path.join(DATA_DIR, "templates.json")


class TemplateManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(STORE_PATH):
            with open(STORE_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)

    def add_template(self, docx_path: str, description: str) -> str:
        templates = self.list_templates()
        tid = str(uuid.uuid4())
        templates.append({"id": tid, "path": docx_path, "description": description})
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return tid

    def list_templates(self):
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_template(self, tid: str):
        return next((t for t in self.list_templates() if t["id"] == tid), None)