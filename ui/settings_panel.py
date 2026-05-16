from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSpinBox, QGroupBox,
    QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt

import config.user_config as cfg


class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        title = QLabel('Ustawienia')
        title.setObjectName('sectionTitle')
        root.addWidget(title)

        subtitle = QLabel('Konfiguracja ścieżek i parametrów konwersji')
        subtitle.setObjectName('sectionSubtitle')
        root.addWidget(subtitle)

        root.addWidget(self._build_ffmpeg_group())
        root.addWidget(self._build_output_group())
        root.addWidget(self._build_threads_group())
        root.addStretch()
        root.addLayout(self._build_button_bar())

    # ------------------------------------------------------------------ groups

    def _build_ffmpeg_group(self) -> QGroupBox:
        box = QGroupBox('Pliki wykonywalne FFmpeg')
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        layout.addWidget(QLabel('Ścieżka do ffmpeg.exe'))
        self._edit_ffmpeg = self._path_row(layout, 'ffmpeg_path', self._browse_ffmpeg)

        layout.addWidget(QLabel('Ścieżka do ffprobe.exe'))
        self._edit_ffprobe = self._path_row(layout, 'ffprobe_path', self._browse_ffprobe)

        return box

    def _build_output_group(self) -> QGroupBox:
        box = QGroupBox('Folder wyjściowy')
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        layout.addWidget(QLabel('Domyślny folder zapisu plików'))
        self._edit_output = self._path_row(layout, 'output_dir', self._browse_output)

        return box

    def _build_threads_group(self) -> QGroupBox:
        box = QGroupBox('Wydajność')
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        row = QHBoxLayout()
        row.addWidget(QLabel('Liczba wątków FFmpeg'))
        row.addStretch()
        self._spin_threads = QSpinBox()
        self._spin_threads.setRange(1, 32)
        self._spin_threads.setFixedWidth(80)
        self._spin_threads.setValue(int(cfg.get('threads') or 4))
        row.addWidget(self._spin_threads)
        layout.addLayout(row)

        hint = QLabel('Wartość 0 = automatyczna (zalecane: liczba rdzeni CPU)')
        hint.setObjectName('sectionSubtitle')
        self._spin_threads.setRange(0, 32)
        self._spin_threads.setSpecialValueText('auto')
        layout.addWidget(hint)

        return box

    def _build_button_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(10)

        btn_reset = QPushButton('Przywróć domyślne')
        btn_reset.setObjectName('btnCancel')
        btn_reset.setFixedWidth(180)
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(self._reset_defaults)

        btn_save = QPushButton('Zapisz ustawienia')
        btn_save.setObjectName('btnPrimary')
        btn_save.setFixedWidth(180)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save_settings)

        bar.addStretch()
        bar.addWidget(btn_reset)
        bar.addWidget(btn_save)
        return bar

    # ------------------------------------------------------------------ helpers

    def _path_row(self, parent_layout, cfg_key: str, browse_fn) -> QLineEdit:
        row = QHBoxLayout()
        edit = QLineEdit()
        edit.setText(str(cfg.get(cfg_key) or ''))
        edit.setPlaceholderText('Wprowadź ścieżkę...')
        row.addWidget(edit, stretch=1)

        btn = QPushButton('Przeglądaj')
        btn.setObjectName('btnSecondary')
        btn.setFixedWidth(100)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(browse_fn)
        row.addWidget(btn)

        parent_layout.addLayout(row)
        return edit

    def _reload_fields(self):
        self._edit_ffmpeg.setText(str(cfg.get('ffmpeg_path') or ''))
        self._edit_ffprobe.setText(str(cfg.get('ffprobe_path') or ''))
        self._edit_output.setText(str(cfg.get('output_dir') or ''))
        self._spin_threads.setValue(int(cfg.get('threads') or 0))

    # ------------------------------------------------------------------ browse

    def _browse_ffmpeg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Wybierz ffmpeg.exe', '', 'Pliki wykonywalne (*.exe);;Wszystkie pliki (*)'
        )
        if path:
            self._edit_ffmpeg.setText(path)

    def _browse_ffprobe(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Wybierz ffprobe.exe', '', 'Pliki wykonywalne (*.exe);;Wszystkie pliki (*)'
        )
        if path:
            self._edit_ffprobe.setText(path)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, 'Wybierz folder wyjściowy')
        if path:
            self._edit_output.setText(path)

    # ------------------------------------------------------------------ actions

    def _save_settings(self):
        cfg.set_value('ffmpeg_path', self._edit_ffmpeg.text().strip())
        cfg.set_value('ffprobe_path', self._edit_ffprobe.text().strip())
        cfg.set_value('output_dir', self._edit_output.text().strip())
        cfg.set_value('threads', self._spin_threads.value())
        cfg.save()
        QMessageBox.information(self, 'Ustawienia', 'Ustawienia zostały zapisane.')

    def _reset_defaults(self):
        reply = QMessageBox.question(
            self, 'Przywróć domyślne',
            'Czy na pewno chcesz przywrócić domyślne ustawienia?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            cfg.reset_defaults()
            self._reload_fields()
