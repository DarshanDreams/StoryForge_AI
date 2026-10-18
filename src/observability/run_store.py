from __future__ import annotations

import json
from pathlib import Path
from threading import Lock


class RunStore:
    """Append-only JSONL storage for traceable creative experiments."""

    def __init__(self, path: str | Path = "evaluation/experiment_runs.jsonl"):
        self.path = Path(path)
        self._append_lock = Lock()

    def append(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(record, ensure_ascii=True) + "\n"
        with self._append_lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(serialized)

    def recent(self, limit: int = 20) -> list[dict]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines if line.strip()]
        return list(reversed(records[-limit:]))

    def all(self) -> list[dict]:
        return list(reversed(self.recent(limit=100000)))

    def compare(self, action: str | None = None) -> list[dict]:
        records = self.all()
        if action:
            records = [record for record in records if record.get("action") == action]
        return records