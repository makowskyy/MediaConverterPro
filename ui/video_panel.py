from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
)
from PySide6.QtCore import Qt


def _row(label: str, value: str = '—') -> tuple[QLabel, QLabel]:
    lbl = QLabel(label + ':')
    lbl.setObjectName('fileMetaLabel')
    val = QLabel(value)
    val.setObjectName('fileInfoValue')
    val.setWordWrap(True)
    return lbl, val


class VideoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        title = QLabel('Dane pliku')
        title.setObjectName('sectionTitle')
        root.addWidget(title)

        self._subtitle = QLabel('Załaduj plik w panelu Konwersja, aby zobaczyć szczegóły')
        self._subtitle.setObjectName('sectionSubtitle')
        root.addWidget(self._subtitle)

        root.addWidget(self._build_general_group())
        root.addWidget(self._build_video_group())
        root.addWidget(self._build_audio_group())
        root.addStretch()

    def _build_general_group(self) -> QGroupBox:
        box = QGroupBox('Ogólne')
        lay = QVBoxLayout(box)
        lay.setSpacing(6)

        self._lbl_filename,  self._val_filename  = _row('Nazwa pliku')
        self._lbl_format,    self._val_format     = _row('Format / kontener')
        self._lbl_duration,  self._val_duration   = _row('Czas trwania')
        self._lbl_size,      self._val_size       = _row('Rozmiar')
        self._lbl_bitrate,   self._val_bitrate    = _row('Bitrate ogólny')

        for lbl, val in (
            (self._lbl_filename, self._val_filename),
            (self._lbl_format,   self._val_format),
            (self._lbl_duration, self._val_duration),
            (self._lbl_size,     self._val_size),
            (self._lbl_bitrate,  self._val_bitrate),
        ):
            row = QHBoxLayout()
            row.setSpacing(12)
            lbl.setFixedWidth(160)
            row.addWidget(lbl)
            row.addWidget(val, stretch=1)
            lay.addLayout(row)

        return box

    def _build_video_group(self) -> QGroupBox:
        self._box_video = QGroupBox('Strumień wideo')
        lay = QVBoxLayout(self._box_video)
        lay.setSpacing(6)

        self._lbl_res,     self._val_res     = _row('Rozdzielczość')
        self._lbl_vcodec,  self._val_vcodec  = _row('Kodek wideo')
        self._lbl_fps,     self._val_fps     = _row('Klatki na sekundę')

        for lbl, val in (
            (self._lbl_res,    self._val_res),
            (self._lbl_vcodec, self._val_vcodec),
            (self._lbl_fps,    self._val_fps),
        ):
            row = QHBoxLayout()
            row.setSpacing(12)
            lbl.setFixedWidth(160)
            row.addWidget(lbl)
            row.addWidget(val, stretch=1)
            lay.addLayout(row)

        return self._box_video

    def _build_audio_group(self) -> QGroupBox:
        self._box_audio = QGroupBox('Strumień audio')
        lay = QVBoxLayout(self._box_audio)
        lay.setSpacing(6)

        self._lbl_acodec,  self._val_acodec  = _row('Kodek audio')
        self._lbl_srate,   self._val_srate   = _row('Częstotliwość próbk.')
        self._lbl_channels,self._val_channels = _row('Kanały')

        for lbl, val in (
            (self._lbl_acodec,   self._val_acodec),
            (self._lbl_srate,    self._val_srate),
            (self._lbl_channels, self._val_channels),
        ):
            row = QHBoxLayout()
            row.setSpacing(12)
            lbl.setFixedWidth(160)
            row.addWidget(lbl)
            row.addWidget(val, stretch=1)
            lay.addLayout(row)

        return self._box_audio

    def update_metadata(self, meta: dict):
        self._subtitle.setText(meta.get('filename', ''))

        self._val_filename.setText(meta.get('filename', '—'))
        self._val_format.setText(meta.get('format', '—'))

        dur = meta.get('duration', 0)
        if dur:
            total = int(float(dur))
            hh, rem = divmod(total, 3600)
            mm, ss = divmod(rem, 60)
            self._val_duration.setText(f'{hh:02d}:{mm:02d}:{ss:02d}')
        else:
            self._val_duration.setText('—')

        size = meta.get('size', 0)
        if size:
            mb = int(size) / (1024 * 1024)
            self._val_size.setText(f'{mb:.2f} MB  ({int(size):,} B)')
        else:
            self._val_size.setText('—')

        br = meta.get('bitrate', 0)
        self._val_bitrate.setText(f'{int(br) // 1000} kbps' if br else '—')

        w, h = meta.get('width'), meta.get('height')
        self._val_res.setText(f'{w} × {h} px' if w and h else '—')
        self._val_vcodec.setText(meta.get('video_codec', '—'))
        fps = meta.get('fps')
        self._val_fps.setText(f'{fps} fps' if fps else '—')

        self._val_acodec.setText(meta.get('audio_codec', '—'))
        sr = meta.get('sample_rate')
        self._val_srate.setText(f'{int(sr):,} Hz'.replace(',', ' ') if sr else '—')
        ch = meta.get('channels', 0)
        ch_map = {1: 'Mono (1)', 2: 'Stereo (2)', 6: '5.1 (6)', 8: '7.1 (8)'}
        self._val_channels.setText(ch_map.get(ch, f'{ch}') if ch else '—')

        self._box_video.setVisible(bool(w and h))
        self._box_audio.setVisible(bool(meta.get('audio_codec')))
