import os
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget

from ui.sidebar import Sidebar
from ui.conversion_panel import ConversionPanel
from ui.video_panel import VideoPanel
from ui.audio_panel import AudioPanel
from ui.settings_panel import SettingsPanel
from ui.history_panel import HistoryPanel
from ui.about_panel import AboutPanel
from config.settings import APP_NAME, APP_VERSION

DARK_QSS = os.path.join(os.path.dirname(__file__), '..', 'assets', 'styles', 'dark.qss')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'{APP_NAME} {APP_VERSION}')
        self.setMinimumSize(1000, 680)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._sidebar = Sidebar()
        root_layout.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName('contentArea')
        root_layout.addWidget(self._stack, stretch=1)

        self._pages: dict[str, QWidget] = {
            'conversion': ConversionPanel(),
            'video':      VideoPanel(),
            'audio':      AudioPanel(),
            'settings':   SettingsPanel(),
            'history':    HistoryPanel(),
            'about':      AboutPanel(),
        }
        for page in self._pages.values():
            self._stack.addWidget(page)

        self._sidebar.page_changed.connect(self._switch_page)
        self._switch_page('conversion')

        self._load_stylesheet()

    def _load_stylesheet(self):
        try:
            with open(DARK_QSS, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except OSError:
            pass

    def _switch_page(self, key: str):
        page = self._pages.get(key)
        if page:
            self._stack.setCurrentWidget(page)
            self._sidebar.set_active(key)
