import subprocess
import json
import re

from PySide6.QtCore import QThread, Signal

from config.settings import FFPROBE_PATH


class FFmpegWorker(QThread):
    progress_updated = Signal(int)   # 0-100
    status_changed   = Signal(str)   # komunikat tekstowy
    finished         = Signal(bool)  # True = sukces

    def __init__(self, input_file: str, output_file: str, command: list[str],
                 ffprobe_path: str = FFPROBE_PATH):
        super().__init__()
        self.input_file   = input_file
        self.output_file  = output_file
        self.command      = command
        self.ffprobe_path = ffprobe_path
        self._process     = None

    # --- metody wewnętrzne ---

    def _get_duration(self) -> float | None:
        cmd = [self.ffprobe_path, '-v', 'quiet',
               '-print_format', 'json', '-show_format', self.input_file]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8')
            return float(json.loads(output)['format']['duration'])
        except Exception:
            return None

    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        h, m, s = time_str.split(':')
        return float(h) * 3600 + float(m) * 60 + float(s)

    # --- główna metoda wątku ---

    def run(self):
        total_duration = self._get_duration()
        if not total_duration:
            self.finished.emit(False)
            return

        self.status_changed.emit('Konwertowanie...')
        time_regex = re.compile(r'time=(\d{2}:\d{2}:\d{2}\.\d+)')

        self._process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # FFmpeg pisze postęp na stderr
            text=True,
        )

        for line in self._process.stdout:
            match = time_regex.search(line)
            if match:
                current = self._time_to_seconds(match.group(1))
                pct = int((current / total_duration) * 100)
                self.progress_updated.emit(min(pct, 100))

        self._process.wait()
        success = self._process.returncode == 0
        self.status_changed.emit('Zakończono pomyślnie' if success else 'Błąd konwersji')
        self.finished.emit(success)

    def cancel(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()
