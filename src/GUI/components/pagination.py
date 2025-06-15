from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QApplication
from PyQt6.QtCore   import pyqtSignal, Qt, QTimer
from PyQt6.QtGui    import QFont

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
        
        self.setMinimumHeight(40)

    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8) 
        lay.addStretch()

        self._update_sizes()

        self.prev_btn = QPushButton("◀")
        self.prev_btn.setObjectName("paginationPrevButton")
        self.prev_btn.setFont(QFont("Segoe UI", self.font_size))
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setObjectName("paginationNextButton")
        self.next_btn.setFont(QFont("Segoe UI", self.font_size))
        
        self.label = QLabel()
        self.label.setObjectName("paginationLabel")
        self.label.setFont(QFont("Segoe UI", self.font_size, QFont.Weight.Medium.value))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._apply_sizes()

        self.prev_btn.clicked.connect(self._on_prev)
        self.next_btn.clicked.connect(self._on_next)

        lay.addWidget(self.prev_btn)
        lay.addWidget(self.label)
        lay.addWidget(self.next_btn)

        self.setVisible(False)

    def _update_sizes(self):
        if self.parent() and hasattr(self.parent(), 'width'):
            current_width = self.parent().width()
        else:
            screen = QApplication.primaryScreen()
            current_width = screen.availableGeometry().width()
        
        if current_width >= 1920:
            self.button_size = 36
            self.font_size = 11
            self.spacing = 10
            self.label_min_width = 120
        elif current_width >= 1600:
            self.button_size = 32
            self.font_size = 10
            self.spacing = 8
            self.label_min_width = 110
        elif current_width >= 1200:
            self.button_size = 30
            self.font_size = 9
            self.spacing = 8
            self.label_min_width = 100
        elif current_width >= 800:
            self.button_size = 28
            self.font_size = 9
            self.spacing = 6
            self.label_min_width = 90
        else:
            self.button_size = 26
            self.font_size = 8
            self.spacing = 6
            self.label_min_width = 80

    def _apply_sizes(self):
        button_size = max(24, min(40, self.button_size))
        
        self.prev_btn.setMinimumSize(button_size, button_size)
        self.prev_btn.setMaximumSize(button_size + 10, button_size + 10)
        self.prev_btn.setFont(QFont("Segoe UI", max(8, self.font_size)))
        
        self.next_btn.setMinimumSize(button_size, button_size)
        self.next_btn.setMaximumSize(button_size + 10, button_size + 10)
        self.next_btn.setFont(QFont("Segoe UI", max(8, self.font_size)))
        
        self.label.setFont(QFont("Segoe UI", max(8, self.font_size), QFont.Weight.Medium.value))
        self.label.setMinimumWidth(max(80, self.label_min_width))
        
        if self.layout():
            self.layout().setSpacing(max(6, self.spacing))

    def setPage(self, current: int, total: int):
        self._current = current
        self._total   = total
        self.label.setText(f"Page {current} of {total}")
        self.prev_btn.setEnabled(current > 1)
        self.next_btn.setEnabled(current < total)
        
        should_show = total > 1
        self.setVisible(should_show)
        
        if should_show:
            self.setMinimumSize(
                max(200, self.label_min_width + (self.button_size * 2) + (self.spacing * 4)),
                max(32, self.button_size + 8)
            )

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        if hasattr(self, '_resize_timer'):
            self._resize_timer.stop()
        else:
            self._resize_timer = QTimer()
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self._delayed_resize)
        
        self._resize_timer.start(50)

    def _delayed_resize(self):
        self._update_sizes()
        self._apply_sizes()

    def sizeHint(self):
        self._update_sizes()
        width = self.label_min_width + (self.button_size * 2) + (self.spacing * 4) + 16
        height = max(32, self.button_size + 16)
        return self.size().__class__(width, height)

    def minimumSizeHint(self):
        return self.size().__class__(200, 32)