import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from config.settings import APP_NAME, _base_path


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName(APP_NAME)

    logo_path = os.path.join(_base_path(), 'assets', 'logo.png')
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
