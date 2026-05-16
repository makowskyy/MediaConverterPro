import os

APP_NAME = 'MediaConverterPro'
APP_VERSION = '1.0.0'

DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'Videos', 'Converted')
DEFAULT_FORMAT = 'MP4'
DEFAULT_THREADS = 0  # 0 = auto (FFmpeg decyduje)

FFMPEG_PATH = 'ffmpeg'
FFPROBE_PATH = 'ffprobe'
