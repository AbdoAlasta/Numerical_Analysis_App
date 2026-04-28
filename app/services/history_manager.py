import json
import uuid
from datetime import datetime
from pathlib import Path


class HistoryManager:
    def __init__(self, filepath: str | Path, max_entries: int = 100) -> None:
        self._filepath = Path(filepath)
        self.max_entries = max_entries

    def save_record(self, record: dict) -> str:
        records = self._read()
        record_id = uuid.uuid4().hex[:12]
        record["id"] = record_id
        record["datetime"] = datetime.now().isoformat(timespec="seconds")
        records.append(record)
        if len(records) > self.max_entries:
            records = records[-self.max_entries:]
        self._write(records)
        return record_id

    def load_records(self) -> list[dict]:
        records = self._read()
        return list(reversed(records))

    def get_record(self, record_id: str) -> dict | None:
        for r in self._read():
            if r.get("id") == record_id:
                return r
        return None

    def delete_record(self, record_id: str) -> bool:
        records = self._read()
        new_records = [r for r in records if r.get("id") != record_id]
        if len(new_records) < len(records):
            self._write(new_records)
            return True
        return False

    def clear_all(self) -> None:
        self._write([])

    def _read(self) -> list[dict]:
        try:
            if not self._filepath.exists():
                return []
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (IOError, json.JSONDecodeError):
            return []

    def _write(self, records: list[dict]) -> None:
        try:
            self._filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, default=str)
        except IOError:
            pass
