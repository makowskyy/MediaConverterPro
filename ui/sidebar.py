import os

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame)
from PySide6.QtCore import Signal, Qt, QByteArray, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

ICONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons')
ICON_SIZE  = QSize(18, 18)

NAV_ITEMS = [
    ('Konwersja',          'conversion', 'conversion'),
    ('Dane pliku',         'video',      'video'),
    ('Ustawienia',         'settings',   'settings'),
    ('Historia konwersji', 'history',    'history'),
    ('O aplikacji',        'about',      'about'),
]


def _render_svg(name: str, color: str, size: QSize = ICON_SIZE) -> QPixmap:
    path = os.path.join(ICONS_DIR, f'{name}.svg')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            template = f.read()
    except OSError:
        return QPixmap()
    data = template.replace('ICONCOLOR', color).encode('utf-8')
    renderer = QSvgRenderer(QByteArray(data))
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def _make_nav_icon(name: str) -> QIcon | None:
    off_pm = _render_svg(name, '#9ca3af')
    on_pm  = _render_svg(name, '#ffffff')
    if off_pm.isNull():
        return None
    icon = QIcon()
    icon.addPixmap(off_pm, QIcon.Mode.Normal, QIcon.State.Off)
    icon.addPixmap(on_pm,  QIcon.Mode.Normal, QIcon.State.On)
    return icon


class Sidebar(QWidget):
    page_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('sidebar')
        self.setFixedWidth(215)

        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 16)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        logo_pm = _render_svg('app_icon', '#7c3aed', QSize(32, 32))
        if not logo_pm.isNull():
            logo_lbl = QLabel()
            logo_lbl.setPixmap(logo_pm)
            logo_lbl.setFixedSize(QSize(32, 32))
            header.addWidget(logo_lbl)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(0)

        title = QLabel('MediaConverter')
        title.setObjectName('sidebarTitle')
        text_col.addWidget(title)

        subtitle = QLabel('PRO')
        subtitle.setObjectName('sidebarSubtitle')
        text_col.addWidget(subtitle)

        header.addLayout(text_col)
        header.addStretch()
        layout.addLayout(header)

        layout.addSpacing(20)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)
        layout.addSpacing(8)

        for label, key, icon_name in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName('navButton')
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            icon = _make_nav_icon(icon_name)
            if icon:
                btn.setIcon(icon)
                btn.setIconSize(ICON_SIZE)
            btn.clicked.connect(lambda _checked, k=key: self._on_nav_click(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch()

        self._activate('conversion')

    def _on_nav_click(self, key: str):
        self._activate(key)
        self.page_changed.emit(key)

    def _activate(self, key: str):
        for k, btn in self._buttons.items():
            btn.setChecked(k == key)

    def set_active(self, key: str):
        self._activate(key)
