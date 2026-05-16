import subprocess
import json
import os

from config.settings import FFPROBE_PATH, FFMPEG_PATH


def get_duration(input_file: str, ffprobe_path: str = FFPROBE_PATH) -> float | None:
    cmd = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', input_file]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8')
        return float(json.loads(output)['format']['duration'])
    except (subprocess.CalledProcessError, KeyError, ValueError, FileNotFoundError):
        return None


def get_metadata(input_file: str, ffprobe_path: str = FFPROBE_PATH) -> dict | None:
    cmd = [
        ffprobe_path, '-v', 'quiet',
        '-print_format', 'json',
        '-show_format', '-show_streams',
        input_file,
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8')
        data = json.loads(output)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None

    fmt = data.get('format', {})
    streams = data.get('streams', [])
    video = next((s for s in streams if s.get('codec_type') == 'video'), None)
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)

    ext = os.path.splitext(input_file)[1].lstrip('.').upper()
    result = {
        'filename': os.path.basename(input_file),
        'format':   ext if ext else fmt.get('format_long_name', fmt.get('format_name', 'Unknown')),
        'duration': float(fmt.get('duration', 0)),
        'size':     int(fmt.get('size', 0)),
        'bitrate':  int(fmt.get('bit_rate', 0)),
    }

    if video:
        result.update({
            'width':       video.get('width', 0),
            'height':      video.get('height', 0),
            'video_codec': video.get('codec_name', 'Unknown'),
            'fps':         _parse_fps(video.get('r_frame_rate', '0/1')),
        })

    if audio:
        result.update({
            'audio_codec': audio.get('codec_name', 'Unknown'),
            'sample_rate': audio.get('sample_rate', 'Unknown'),
            'channels':    audio.get('channels', 0),
        })

    return result


def get_thumbnail(input_file: str, output_path: str, ffmpeg_path: str = FFMPEG_PATH) -> bool:
    cmd = [
        ffmpeg_path, '-y',
        '-ss', '00:00:01',
        '-i', input_file,
        '-vframes', '1',
        '-q:v', '2',
        output_path,
    ]
    try:
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=True,
        )
        return os.path.exists(output_path)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _parse_fps(fps_str: str) -> float:
    try:
        num, den = fps_str.split('/')
        return round(float(num) / float(den), 3) if float(den) != 0 else 0.0
    except (ValueError, ZeroDivisionError):
        return 0.0
