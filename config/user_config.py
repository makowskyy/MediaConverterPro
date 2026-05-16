import json
import os

from config.settings import DEFAULT_OUTPUT_DIR, FFMPEG_PATH, FFPROBE_PATH, DEFAULT_THREADS

_FILE = os.path.join(os.path.dirname(__file__), '..', 'user_config.json')

_DEFAULTS: dict = {
    'output_dir':   DEFAULT_OUTPUT_DIR,
    'ffmpeg_path':  FFMPEG_PATH,
    'ffprobe_path': FFPROBE_PATH,
    'threads':      DEFAULT_THREADS,
}

_data: dict = {}


def _ensure_loaded() -> None:
    if not _data:
        load()


def load() -> None:
    global _data
    _data = dict(_DEFAULTS)
    if os.path.exists(_FILE):
        try:
            with open(_FILE, 'r', encoding='utf-8') as f:
                _data.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass


def save() -> None:
    _ensure_loaded()
    try:
        with open(_FILE, 'w', encoding='utf-8') as f:
            json.dump(_data, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def get(key: str):
    _ensure_loaded()
    return _data.get(key, _DEFAULTS.get(key))


def set_value(key: str, value) -> None:
    _ensure_loaded()
    _data[key] = value


def reset_defaults() -> None:
    global _data
    _data = dict(_DEFAULTS)
    save()
