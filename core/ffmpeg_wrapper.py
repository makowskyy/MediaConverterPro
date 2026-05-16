import subprocess
import os

from config.settings import FFMPEG_PATH, FFPROBE_PATH
from config.codecs import PRESET_CODECS


class FFmpegWrapper:
    def __init__(self, ffmpeg_path: str = FFMPEG_PATH, ffprobe_path: str = FFPROBE_PATH):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

    def build_command(self, input_file: str, output_file: str, settings: dict) -> list[str]:
        cmd = [self.ffmpeg_path, '-y', '-i', input_file]

        if settings.get('trim_only'):
            # Szybkie przycinanie — kopiuj strumienie bez re-encodowania
            if settings.get('trim_start'):
                cmd += ['-ss', settings['trim_start']]
            if settings.get('trim_end'):
                cmd += ['-to', settings['trim_end']]
            cmd += ['-c', 'copy']
        else:
            vc = settings.get('video_codec')
            if vc:
                cmd += ['-c:v', vc]
                if settings.get('preset') and vc in PRESET_CODECS:
                    cmd += ['-preset', settings['preset']]

            if settings.get('resolution') and settings['resolution'] != 'original':
                cmd += ['-vf', f"scale={settings['resolution']}"]

            if settings.get('fps') and settings['fps'] != 'original':
                cmd += ['-r', str(settings['fps'])]

            if settings.get('video_bitrate') and settings['video_bitrate'] != 'auto':
                cmd += ['-b:v', f"{settings['video_bitrate']}k"]

            if settings.get('keep_audio'):
                cmd += ['-c:a', 'copy']
                # -b:a i -filter:a są niezgodne z -c:a copy — pomijamy
            else:
                if settings.get('audio_codec'):
                    cmd += ['-c:a', settings['audio_codec']]
                if settings.get('audio_bitrate') and settings['audio_bitrate'] != 'auto':
                    cmd += ['-b:a', f"{settings['audio_bitrate']}k"]
                if settings.get('volume', 100) != 100:
                    vol = settings['volume'] / 100.0
                    cmd += ['-filter:a', f'volume={vol}']

            if settings.get('trim_start'):
                cmd += ['-ss', settings['trim_start']]
            if settings.get('trim_end'):
                cmd += ['-to', settings['trim_end']]

        if settings.get('threads'):
            cmd += ['-threads', str(settings['threads'])]

        cmd.append(output_file)
        return cmd

    def check_available(self) -> bool:
        try:
            subprocess.run(
                [self.ffmpeg_path, '-version'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def output_path_for(input_file: str, output_dir: str, extension: str) -> str:
        stem = os.path.splitext(os.path.basename(input_file))[0]
        return os.path.join(output_dir, f'{stem}_converted.{extension}')
