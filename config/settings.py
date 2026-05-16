import os
import sys

APP_NAME = 'MediaConverterPro'
APP_VERSION = '1.0.0'

DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'Videos', 'Converted')
DEFAULT_FORMAT = 'MP4'
DEFAULT_THREADS = 0  # 0 = auto (FFmpeg decyduje)


def _base_path() -> str:
    """Returns the directory containing bundled files when frozen, or project root otherwise."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _exe(name: str) -> str:
    bundled = os.path.join(_base_path(), name)
    return bundled if os.path.isfile(bundled) else name


FFMPEG_PATH  = _exe('ffmpeg.exe')
FFPROBE_PATH = _exe('ffprobe.exe')
