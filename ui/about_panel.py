import subprocess

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
)
from PySide6.QtCore import Qt

from config.settings import APP_NAME, APP_VERSION, FFMPEG_PATH


def _ffmpeg_version() -> str:
    try:
        out = subprocess.check_output(
            [FFMPEG_PATH, '-version'],
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode('utf-8', errors='ignore')
        first = out.splitlines()[0]          # "ffmpeg version 8.1.1 ..."
        return first.split('version ')[-1].split(' ')[0]
    except Exception:
        return 'niedostępny'


def _info_row(label: str, value: str) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(12)
    lbl = QLabel(label + ':')
    lbl.setObjectName('fileMetaLabel')
    lbl.setFixedWidth(160)
    val = QLabel(value)
    val.setObjectName('fileInfoValue')
    val.setWordWrap(True)
    row.addWidget(lbl)
    row.addWidget(val, stretch=1)
    return row


class AboutPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Nagłówek
        header = QHBoxLayout()
        header.setSpacing(20)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        name_lbl = QLabel(APP_NAME)
        name_lbl.setObjectName('sectionTitle')
        ver_lbl = QLabel(f'Wersja {APP_VERSION}')
        ver_lbl.setObjectName('sectionSubtitle')
        title_col.addWidget(name_lbl)
        title_col.addWidget(ver_lbl)
        header.addLayout(title_col)
        header.addStretch()
        root.addLayout(header)

        desc = QLabel(
            'Desktopowa aplikacja do konwersji plików wideo i audio.\n'
            'Graficzna nakładka na FFmpeg — wywołuje go jako podproces\n'
            'i odczytuje postęp w czasie rzeczywistym.'
        )
        desc.setObjectName('sectionSubtitle')
        desc.setWordWrap(True)
        root.addWidget(desc)

        # Informacje techniczne
        box_tech = QGroupBox('Informacje techniczne')
        lay_tech = QVBoxLayout(box_tech)
        lay_tech.setSpacing(6)

        import sys
        from PySide6 import __version__ as pyside_ver

        for row in (
            _info_row('Wersja aplikacji',  APP_VERSION),
            _info_row('Python',            sys.version.split()[0]),
            _info_row('PySide6 (Qt)',       pyside_ver),
            _info_row('FFmpeg',            _ffmpeg_version()),
            _info_row('Backend mediów',    'FFmpeg + FFprobe (subprocess)'),
            _info_row('GUI Framework',     'PySide6 / Qt 6'),
            _info_row('Pakowanie',         'PyInstaller'),
        ):
            lay_tech.addLayout(row)

        root.addWidget(box_tech)

        root.addStretch()
