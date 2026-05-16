import json
import os
from datetime import datetime

_DEFAULT_FILE = os.path.join(os.path.dirname(__file__), '..', 'history.json')
_MAX_ENTRIES  = 200


class HistoryManager:
    def __init__(self, history_file: str = _DEFAULT_FILE):
        self.history_file = os.path.abspath(history_file)

    def _load(self) -> list[dict]:
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, entries: list[dict]) -> None:
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

    def add(self, input_file: str, output_file: str, success: bool) -> None:
        entries = self._load()
        entries.insert(0, {
            'date':   datetime.now().isoformat(timespec='seconds'),
            'input':  input_file,
            'output': output_file,
            'status': 'OK' if success else 'BLAD',
        })
        self._save(entries[:_MAX_ENTRIES])

    def get_all(self) -> list[dict]:
        return self._load()

    def clear(self) -> None:
        self._save([])
