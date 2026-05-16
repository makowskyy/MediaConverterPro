from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QLineEdit, QPushButton, QCheckBox, QFrame,
)
from PySide6.QtCore import Qt


def _sec_to_tc(seconds: float) -> str:
    """Sekundy → HH:MM:SS.mmm"""
    total_ms = int(seconds * 1000)
    ms       = total_ms % 1000
    total_s  = total_ms // 1000
    s        = total_s  % 60
    total_m  = total_s  // 60
    m        = total_m  % 60
    h        = total_m  // 60
    return f'{h:02d}:{m:02d}:{s:02d}.{ms:03d}'


def _tc_to_sec(tc: str) -> float | None:
    """HH:MM:SS[.mmm] → sekundy, None gdy niepoprawny format"""
    try:
        parts = tc.strip().split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    except (ValueError, IndexError):
        pass
    return None


class TrimDialog(QDialog):
    def __init__(self, duration: float,
                 start: str = '',
                 end: str   = '',
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edytor trimowania')
        self.setMinimumWidth(560)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._duration = max(duration, 0.1)
        self._max_ms   = int(self._duration * 1000)
        self._guard    = False  # blokada pętli sygnałów

        self._setup_ui()

        self._set_in_sec(_tc_to_sec(start) or 0.0)
        self._set_out_sec(_tc_to_sec(end)   or self._duration)

    # ── UI ───────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        dur_lbl = QLabel(f'Czas trwania pliku: {_sec_to_tc(self._duration)}')
        dur_lbl.setObjectName('fileMetaLabel')
        lay.addWidget(dur_lbl)

        lay.addWidget(self._hsep())

        lay.addLayout(self._slider_group(
            'Punkt początkowy (IN)', 'in'))
        lay.addLayout(self._slider_group(
            'Punkt końcowy (OUT)',   'out'))

        self._lbl_fragment = QLabel()
        self._lbl_fragment.setObjectName('fileMetaLabel')
        lay.addWidget(self._lbl_fragment)

        lay.addWidget(self._hsep())

        self._chk_copy = QCheckBox(
            'Szybkie przycinanie — kopiuj strumienie bez re-encodowania')
        self._chk_copy.setChecked(True)
        lay.addWidget(self._chk_copy)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton('Anuluj')
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_apply = QPushButton('Zastosuj')
        btn_apply.setObjectName('btnPrimary')
        btn_apply.setFixedWidth(110)
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_apply.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_apply)
        lay.addLayout(btn_row)

    def _slider_group(self, label_text: str, tag: str) -> QVBoxLayout:
        group = QVBoxLayout()
        group.setSpacing(6)

        lbl = QLabel(label_text)
        lbl.setObjectName('fieldLabel')
        group.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(10)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, self._max_ms)

        edit = QLineEdit()
        edit.setFixedWidth(110)

        if tag == 'in':
            self._slider_in, self._edit_in = slider, edit
            slider.setValue(0)
            slider.valueChanged.connect(self._on_in_slider)
            edit.editingFinished.connect(self._on_in_edit)
        else:
            self._slider_out, self._edit_out = slider, edit
            slider.setValue(self._max_ms)
            slider.valueChanged.connect(self._on_out_slider)
            edit.editingFinished.connect(self._on_out_edit)

        row.addWidget(slider, stretch=1)
        row.addWidget(edit)
        group.addLayout(row)
        return group

    @staticmethod
    def _hsep() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        return sep

    # ── Sync suwak ↔ pole tekstowe ───────────────────────────────────────────

    def _on_in_slider(self, ms: int):
        if self._guard:
            return
        out_ms = self._slider_out.value()
        if ms >= out_ms:
            ms = max(0, out_ms - 100)
            self._guard = True
            self._slider_in.setValue(ms)
            self._guard = False
        self._edit_in.setText(_sec_to_tc(ms / 1000))
        self._refresh_fragment()

    def _on_out_slider(self, ms: int):
        if self._guard:
            return
        in_ms = self._slider_in.value()
        if ms <= in_ms:
            ms = min(self._max_ms, in_ms + 100)
            self._guard = True
            self._slider_out.setValue(ms)
            self._guard = False
        self._edit_out.setText(_sec_to_tc(ms / 1000))
        self._refresh_fragment()

    def _on_in_edit(self):
        sec = _tc_to_sec(self._edit_in.text())
        if sec is not None:
            self._set_in_sec(sec)
        else:
            self._edit_in.setText(_sec_to_tc(self._slider_in.value() / 1000))

    def _on_out_edit(self):
        sec = _tc_to_sec(self._edit_out.text())
        if sec is not None:
            self._set_out_sec(sec)
        else:
            self._edit_out.setText(_sec_to_tc(self._slider_out.value() / 1000))

    def _set_in_sec(self, sec: float):
        sec = max(0.0, min(sec, self._duration - 0.1))
        self._guard = True
        self._slider_in.setValue(int(sec * 1000))
        self._edit_in.setText(_sec_to_tc(sec))
        self._guard = False
        self._refresh_fragment()

    def _set_out_sec(self, sec: float):
        sec = max(0.1, min(sec, self._duration))
        self._guard = True
        self._slider_out.setValue(int(sec * 1000))
        self._edit_out.setText(_sec_to_tc(sec))
        self._guard = False
        self._refresh_fragment()

    def _refresh_fragment(self):
        in_s  = self._slider_in.value()  / 1000
        out_s = self._slider_out.value() / 1000
        self._lbl_fragment.setText(
            f'Fragment: {_sec_to_tc(in_s)} – {_sec_to_tc(out_s)}'
            f'   (długość: {_sec_to_tc(out_s - in_s)})')

    # ── Public API ───────────────────────────────────────────────────────────

    def get_trim_start(self) -> str:
        return self._edit_in.text()

    def get_trim_end(self) -> str:
        return self._edit_out.text()

    def get_copy_streams(self) -> bool:
        return self._chk_copy.isChecked()
