import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QSlider, QGroupBox, QCheckBox,
    QFileDialog, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from config.codecs import VIDEO_FORMATS, AUDIO_FORMATS, PRESET_CODECS
from config.presets import PRESETS, VIDEO_BITRATES, AUDIO_BITRATES, RESOLUTIONS, FPS_OPTIONS
from core.ffprobe import get_metadata, get_thumbnail
from config.settings import DEFAULT_OUTPUT_DIR, FFMPEG_PATH

VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.ts',
              '.m4v', '.wmv', '.mpeg', '.mpg'}
AUDIO_EXTS = {'.mp3', '.aac', '.flac', '.ogg', '.wav', '.m4a', '.opus', '.wma'}
ALL_EXTS   = VIDEO_EXTS | AUDIO_EXTS

THUMB_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'thumbnails')


class ConversionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._input_file: str | None = None
        self._output_ext: str = 'mp4'
        self.setAcceptDrops(True)
        self._setup_ui()

    # ── UI construction ──────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        root.addWidget(self._build_file_section())
        root.addWidget(self._build_settings_section())
        root.addWidget(self._build_output_section())
        root.addLayout(self._build_action_bar())
        root.addStretch()

    # ── 1. Załadowany plik ───────────────────────────────────────────────────

    def _build_file_section(self) -> QGroupBox:
        box = QGroupBox('Załadowany plik')
        h = QHBoxLayout(box)
        h.setSpacing(16)
        h.setContentsMargins(12, 12, 12, 12)

        # Miniaturka
        self._thumb_label = QLabel('Brak\npodglądu')
        self._thumb_label.setObjectName('thumbnailLabel')
        self._thumb_label.setFixedSize(160, 100)
        self._thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(self._thumb_label)

        # Metadane
        meta_col = QVBoxLayout()
        meta_col.setSpacing(4)
        meta_col.setContentsMargins(0, 0, 0, 0)

        self._meta_name = QLabel('—')
        self._meta_name.setObjectName('fileInfoLabel')
        meta_col.addWidget(self._meta_name)

        self._meta_format = QLabel('Format: —')
        self._meta_format.setObjectName('fileMetaLabel')
        meta_col.addWidget(self._meta_format)

        self._meta_res = QLabel('Rozdzielczość: —')
        self._meta_res.setObjectName('fileMetaLabel')
        meta_col.addWidget(self._meta_res)

        self._meta_dur = QLabel('Czas trwania: —')
        self._meta_dur.setObjectName('fileMetaLabel')
        meta_col.addWidget(self._meta_dur)

        self._meta_size = QLabel('Rozmiar: —')
        self._meta_size.setObjectName('fileMetaLabel')
        meta_col.addWidget(self._meta_size)

        meta_col.addStretch()
        h.addLayout(meta_col, stretch=1)

        # Przyciski
        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        btn_col.setAlignment(Qt.AlignmentFlag.AlignTop)

        btn_open = QPushButton('Wybierz plik')
        btn_open.setObjectName('btnOutline')
        btn_open.setFixedWidth(130)
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.clicked.connect(self._open_file_dialog)
        btn_col.addWidget(btn_open)

        hint = QLabel('Przeciągnij i upuść plik tutaj')
        hint.setObjectName('fieldLabel')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_col.addWidget(hint)

        h.addLayout(btn_col)
        return box

    # ── 2. Ustawienia konwersji ──────────────────────────────────────────────

    def _build_settings_section(self) -> QGroupBox:
        box = QGroupBox('Ustawienia konwersji')
        lay = QVBoxLayout(box)
        lay.setSpacing(12)
        lay.setContentsMargins(12, 14, 12, 12)

        # Wiersz 1: typ | format | kodek wideo | kodek audio
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self._combo_type = QComboBox()
        self._combo_type.addItems(['Wideo', 'Audio'])
        self._combo_type.currentTextChanged.connect(self._on_type_changed)
        row1.addLayout(self._ccol('Konwertuj do', self._combo_type))

        self._combo_format = QComboBox()
        for fmt in VIDEO_FORMATS:
            self._combo_format.addItem(fmt)
        self._combo_format.currentTextChanged.connect(self._on_format_changed)
        row1.addLayout(self._ccol('Format wyjściowy', self._combo_format))

        # Kolumna kodeku wideo — wrapper do show/hide
        self._vcodec_col = QWidget()
        self._vcodec_col.setStyleSheet('background: transparent;')
        vcc = QVBoxLayout(self._vcodec_col)
        vcc.setContentsMargins(0, 0, 0, 0)
        vcc.setSpacing(4)
        lbl_vc = QLabel('Kodek wideo')
        lbl_vc.setObjectName('fieldLabel')
        self._combo_vcodec = QComboBox()
        self._combo_vcodec.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        vcc.addWidget(lbl_vc)
        vcc.addWidget(self._combo_vcodec)
        row1.addWidget(self._vcodec_col)

        self._combo_acodec = QComboBox()
        row1.addLayout(self._ccol('Kodek audio', self._combo_acodec))

        lay.addLayout(row1)

        # Wiersz 2: jakość | rozdzielczość | fps | bitrate wideo (ukryty w trybie audio)
        self._row2 = QWidget()
        self._row2.setStyleSheet('background: transparent;')
        row2_h = QHBoxLayout(self._row2)
        row2_h.setContentsMargins(0, 0, 0, 0)
        row2_h.setSpacing(12)

        self._combo_preset = QComboBox()
        for label, _ in PRESETS:
            self._combo_preset.addItem(label)
        self._combo_preset.setCurrentIndex(1)  # Wysoka
        row2_h.addLayout(self._ccol('Jakość', self._combo_preset))

        self._combo_res = QComboBox()
        for label, _ in RESOLUTIONS:
            self._combo_res.addItem(label)
        row2_h.addLayout(self._ccol('Rozdzielczość', self._combo_res))

        self._combo_fps = QComboBox()
        for label, _ in FPS_OPTIONS:
            self._combo_fps.addItem(label)
        row2_h.addLayout(self._ccol('Klatka na sekundę', self._combo_fps))

        self._combo_vbitrate = QComboBox()
        for br in VIDEO_BITRATES:
            self._combo_vbitrate.addItem('auto' if br == 'auto' else f'{br} kbps')
        row2_h.addLayout(self._ccol('Bitrate wideo', self._combo_vbitrate))

        lay.addWidget(self._row2)

        # Wiersz 3: bitrate audio | głośność | checkboxy
        row3 = QHBoxLayout()
        row3.setSpacing(20)

        self._combo_abitrate = QComboBox()
        for br in AUDIO_BITRATES:
            self._combo_abitrate.addItem('auto' if br == 'auto' else f'{br} kbps')
        abitrate_w = QWidget()
        abitrate_w.setStyleSheet('background: transparent;')
        abitrate_w.setFixedWidth(170)
        QVBoxLayout(abitrate_w).setContentsMargins(0, 0, 0, 0)
        abitrate_w.layout().setSpacing(4)
        abitrate_w.layout().addWidget(self._field_label('Bitrate audio'))
        abitrate_w.layout().addWidget(self._combo_abitrate)
        row3.addWidget(abitrate_w)

        # Głośność
        vol_w = QWidget()
        vol_w.setStyleSheet('background: transparent;')
        vol_lay = QVBoxLayout(vol_w)
        vol_lay.setContentsMargins(0, 0, 0, 0)
        vol_lay.setSpacing(4)
        self._lbl_vol = QLabel('Głośność audio: 100%')
        self._lbl_vol.setObjectName('fieldLabel')
        self._slider_vol = QSlider(Qt.Orientation.Horizontal)
        self._slider_vol.setRange(0, 200)
        self._slider_vol.setValue(100)
        self._slider_vol.valueChanged.connect(
            lambda v: self._lbl_vol.setText(f'Głośność audio: {v}%'))
        vol_lay.addWidget(self._lbl_vol)
        vol_lay.addWidget(self._slider_vol)
        row3.addWidget(vol_w, stretch=1)

        # Checkboxy + Edytuj
        chk_w = QWidget()
        chk_w.setStyleSheet('background: transparent;')
        chk_lay = QVBoxLayout(chk_w)
        chk_lay.setContentsMargins(0, 0, 0, 0)
        chk_lay.setSpacing(8)

        self._chk_keep_audio = QCheckBox('Zachowaj oryginalną ścieżkę audio')
        self._chk_keep_audio.setChecked(True)
        chk_lay.addWidget(self._chk_keep_audio)

        trim_row = QHBoxLayout()
        trim_row.setSpacing(8)
        self._chk_trim = QCheckBox('Przytnij do zaznaczonego fragmentu')
        self._btn_edit = QPushButton('✂  Edytuj')
        self._btn_edit.setObjectName('btnOutline')
        self._btn_edit.setFixedWidth(90)
        self._btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_edit.setEnabled(False)
        self._chk_trim.toggled.connect(self._btn_edit.setEnabled)
        trim_row.addWidget(self._chk_trim)
        trim_row.addWidget(self._btn_edit)
        chk_lay.addLayout(trim_row)

        row3.addWidget(chk_w)
        lay.addLayout(row3)

        # Wypełnij kodeki dla domyślnego formatu
        self._on_format_changed(self._combo_format.currentText())

        return box

    # ── 3. Zapisz plik w ────────────────────────────────────────────────────

    def _build_output_section(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lbl = QLabel('Zapisz plik w')
        lbl.setObjectName('fieldLabel')
        lay.addWidget(lbl)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self._edit_outpath = QLineEdit(DEFAULT_OUTPUT_DIR)
        self._edit_outpath.setReadOnly(True)
        btn_browse = QPushButton('Przeglądaj')
        btn_browse.setFixedWidth(100)
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse_output_dir)
        path_row.addWidget(self._edit_outpath, stretch=1)
        path_row.addWidget(btn_browse)
        lay.addLayout(path_row)

        return w

    # ── 4. Pasek akcji ───────────────────────────────────────────────────────

    def _build_action_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setContentsMargins(0, 4, 0, 0)

        self._lbl_status = QLabel('Brak załadowanego pliku')
        self._lbl_status.setObjectName('fieldLabel')
        bar.addWidget(self._lbl_status)

        bar.addStretch()

        self._btn_convert = QPushButton('Rozpocznij konwersję')
        self._btn_convert.setObjectName('btnPrimary')
        self._btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_convert.setEnabled(False)
        bar.addWidget(self._btn_convert)

        return bar

    # ── Helpers UI ───────────────────────────────────────────────────────────

    @staticmethod
    def _ccol(label_text: str, widget: QWidget) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(4)
        lbl = QLabel(label_text)
        lbl.setObjectName('fieldLabel')
        col.addWidget(lbl)
        col.addWidget(widget)
        return col

    @staticmethod
    def _field_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName('fieldLabel')
        return lbl

    # ── Logic ────────────────────────────────────────────────────────────────

    def _on_type_changed(self, text: str):
        is_video = (text == 'Wideo')
        self._row2.setVisible(is_video)
        self._vcodec_col.setVisible(is_video)

        self._combo_format.blockSignals(True)
        self._combo_format.clear()
        for fmt in (VIDEO_FORMATS if is_video else AUDIO_FORMATS):
            self._combo_format.addItem(fmt)
        self._combo_format.blockSignals(False)
        self._on_format_changed(self._combo_format.currentText())

    def _on_format_changed(self, fmt: str):
        is_video = (self._combo_type.currentText() == 'Wideo')

        self._combo_vcodec.blockSignals(True)
        self._combo_vcodec.clear()
        self._combo_acodec.clear()

        if is_video and fmt in VIDEO_FORMATS:
            for label, _ in VIDEO_FORMATS[fmt]['video']:
                self._combo_vcodec.addItem(label)
            for label, _ in VIDEO_FORMATS[fmt]['audio']:
                self._combo_acodec.addItem(label)

        self._combo_vcodec.blockSignals(False)
        self._refresh_output_ext()

    def _open_file_dialog(self):
        exts = ' '.join(f'*{e}' for e in sorted(ALL_EXTS))
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Wybierz plik multimedialny',
            os.path.expanduser('~'),
            f'Pliki multimedialne ({exts});;Wszystkie pliki (*)',
        )
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        self._input_file = path

        meta = get_metadata(path)
        if meta:
            self._update_file_info(meta)
        else:
            self._meta_name.setText(os.path.basename(path))

        os.makedirs(THUMB_DIR, exist_ok=True)
        thumb_path = os.path.join(THUMB_DIR, 'preview.jpg')
        if get_thumbnail(path, thumb_path, FFMPEG_PATH):
            pm = QPixmap(thumb_path).scaled(
                160, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._thumb_label.setPixmap(pm)
            self._thumb_label.setText('')
        else:
            self._thumb_label.clear()
            self._thumb_label.setText('Brak\npodglądu')

        self._set_status('Gotowy do konwersji', 'statusLabel')
        self._btn_convert.setEnabled(True)
        self._refresh_output_ext()

    def _update_file_info(self, meta: dict):
        self._meta_name.setText(meta.get('filename', '—'))
        self._meta_format.setText(f'Format: {meta.get("format", "—")}')

        w_px, h_px = meta.get('width'), meta.get('height')
        self._meta_res.setText(
            f'Rozdzielczość: {w_px}×{h_px}' if w_px and h_px else 'Rozdzielczość: —')

        dur = meta.get('duration', 0)
        if dur:
            total = int(float(dur))
            hh, rem = divmod(total, 3600)
            mm, ss  = divmod(rem, 60)
            self._meta_dur.setText(f'Czas trwania: {hh:02d}:{mm:02d}:{ss:02d}')

        size = meta.get('size', 0)
        if size:
            self._meta_size.setText(f'Rozmiar: {int(size) / (1024 * 1024):.2f} MB')

    def _browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, 'Wybierz katalog wyjściowy',
            self._edit_outpath.text() or os.path.expanduser('~'),
        )
        if folder:
            self._edit_outpath.setText(folder)

    def _refresh_output_ext(self):
        fmt = self._combo_format.currentText()
        is_video = (self._combo_type.currentText() == 'Wideo')
        if is_video and fmt in VIDEO_FORMATS:
            self._output_ext = VIDEO_FORMATS[fmt]['extension']
        elif not is_video and fmt in AUDIO_FORMATS:
            self._output_ext = AUDIO_FORMATS[fmt]['extension']

    def _set_status(self, text: str, obj_name: str = 'fieldLabel'):
        self._lbl_status.setText(text)
        self._lbl_status.setObjectName(obj_name)
        self._lbl_status.style().unpolish(self._lbl_status)
        self._lbl_status.style().polish(self._lbl_status)

    # ── Drag & drop ──────────────────────────────────────────────────────────

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            if os.path.splitext(path)[1].lower() in ALL_EXTS:
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.splitext(path)[1].lower() in ALL_EXTS:
                self._load_file(path)
                event.acceptProposedAction()

    # ── Public API (Etap 4) ──────────────────────────────────────────────────

    def get_input_file(self) -> str | None:
        return self._input_file

    def get_output_file(self) -> str | None:
        if not self._input_file:
            return None
        stem = os.path.splitext(os.path.basename(self._input_file))[0]
        return os.path.join(
            self._edit_outpath.text(), f'{stem}_converted.{self._output_ext}')

    def get_settings(self) -> dict:
        is_video = (self._combo_type.currentText() == 'Wideo')
        fmt = self._combo_format.currentText()

        vcodec, acodec = None, None
        if is_video and fmt in VIDEO_FORMATS:
            vi = self._combo_vcodec.currentIndex()
            ai = self._combo_acodec.currentIndex()
            vclist = VIDEO_FORMATS[fmt]['video']
            aclist = VIDEO_FORMATS[fmt]['audio']
            vcodec = vclist[vi][1] if 0 <= vi < len(vclist) else None
            acodec = aclist[ai][1] if 0 <= ai < len(aclist) else None
        elif not is_video and fmt in AUDIO_FORMATS:
            acodec = AUDIO_FORMATS[fmt]['codec']

        preset = None
        if vcodec in PRESET_CODECS:
            pi = self._combo_preset.currentIndex()
            if 0 <= pi < len(PRESETS):
                preset = PRESETS[pi][1]

        return {
            'video_codec':   vcodec,
            'audio_codec':   acodec,
            'preset':        preset,
            'resolution':    RESOLUTIONS[self._combo_res.currentIndex()][1] if is_video else None,
            'fps':           FPS_OPTIONS[self._combo_fps.currentIndex()][1] if is_video else None,
            'video_bitrate': VIDEO_BITRATES[self._combo_vbitrate.currentIndex()] if is_video else None,
            'audio_bitrate': AUDIO_BITRATES[self._combo_abitrate.currentIndex()],
            'volume':        self._slider_vol.value(),
            'keep_audio':    self._chk_keep_audio.isChecked(),
        }

    @property
    def btn_convert(self) -> QPushButton:
        return self._btn_convert

    @property
    def lbl_status(self) -> QLabel:
        return self._lbl_status
