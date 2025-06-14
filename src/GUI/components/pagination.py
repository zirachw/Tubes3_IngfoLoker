# src/GUI/components/pagination.py
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore   import pyqtSignal, Qt

class Pagination(QWidget):
    """
    A reusable pagination widget: shows "<  Page X of Y  >"
    and emits pageChanged(new_page) when user clicks prev/next.
    """
    pageChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagination")
        self._current = 1
        self._total   = 1
        self._build_ui()

    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addStretch()

        self.prev_btn = QPushButton("<")
        self.prev_btn.setObjectName("paginationPrevButton")
        self.next_btn = QPushButton(">")
        self.next_btn.setObjectName("paginationNextButton")
        self.label    = QLabel()
        self.label.setObjectName("paginationLabel")

        self.prev_btn.clicked.connect(self._on_prev)
        self.next_btn.clicked.connect(self._on_next)

        lay.addWidget(self.prev_btn)
        lay.addWidget(self.label)
        lay.addWidget(self.next_btn)

        self.setVisible(False)

    def setPage(self, current: int, total: int):
        """Update display and enable/disable buttons."""
        self._current = current
        self._total   = total
        self.label.setText(f"Page {current} of {total}")
        self.prev_btn.setEnabled(current > 1)
        self.next_btn.setEnabled(current < total)
        self.setVisible(total > 1)

    def _on_prev(self):
        if self._current > 1:
            self._current -= 1
            self.setPage(self._current, self._total)
            self.pageChanged.emit(self._current)

    def _on_next(self):
        if self._current < self._total:
            self._current += 1
            self.setPage(self._current, self._total)
            self.pageChanged.emit(self._current)