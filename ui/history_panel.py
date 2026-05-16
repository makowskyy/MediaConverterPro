from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from core.history_manager import HistoryManager

_HEADERS = ['Data', 'Plik wejściowy', 'Plik wyjściowy', 'Status']
_COLOR_OK  = QColor('#22c55e')
_COLOR_ERR = QColor('#ef4444')

_manager = HistoryManager()


class HistoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Nagłówek
        header = QHBoxLayout()
        title = QLabel('Historia konwersji')
        title.setObjectName('sectionTitle')
        header.addWidget(title)
        header.addStretch()

        btn_clear = QPushButton('Wyczyść historię')
        btn_clear.setObjectName('btnCancel')
        btn_clear.setFixedWidth(140)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self._clear_history)
        header.addWidget(btn_clear)
        root.addLayout(header)

        subtitle = QLabel('Lista ostatnich konwersji (maks. 200 wpisów)')
        subtitle.setObjectName('sectionSubtitle')
        root.addWidget(subtitle)

        # Tabela
        self._table = QTableWidget()
        self._table.setColumnCount(len(_HEADERS))
        self._table.setHorizontalHeaderLabels(_HEADERS)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(self._table, stretch=1)

        self._lbl_empty = QLabel('Brak wpisów w historii')
        self._lbl_empty.setObjectName('placeholderLabel')
        self._lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_empty.setVisible(False)
        root.addWidget(self._lbl_empty)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

    def _refresh(self):
        entries = _manager.get_all()
        self._table.setRowCount(0)

        if not entries:
            self._table.setVisible(False)
            self._lbl_empty.setVisible(True)
            return

        self._lbl_empty.setVisible(False)
        self._table.setVisible(True)
        self._table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            date_str = entry.get('date', '—').replace('T', '  ')
            input_f  = entry.get('input', '—')
            output_f = entry.get('output', '—')
            status   = entry.get('status', '—')

            items = [
                QTableWidgetItem(date_str),
                QTableWidgetItem(input_f),
                QTableWidgetItem(output_f),
                QTableWidgetItem('✓  OK' if status == 'OK' else '✗  Błąd'),
            ]

            color = _COLOR_OK if status == 'OK' else _COLOR_ERR
            items[3].setForeground(color)

            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self._table.setItem(row, col, item)

        self._table.resizeRowsToContents()

    def _clear_history(self):
        if not _manager.get_all():
            return
        reply = QMessageBox.question(
            self, 'Wyczyść historię',
            'Czy na pewno chcesz usunąć całą historię konwersji?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            _manager.clear()
            self._refresh()
