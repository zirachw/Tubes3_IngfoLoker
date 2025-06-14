# src/GUI/components/pagination.py
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QApplication
from PyQt6.QtCore   import pyqtSignal, Qt
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

    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addStretch()

        # Calculate responsive sizes
        screen = QApplication.primaryScreen()
        screen_width = screen.availableGeometry().width()
        
        # Responsive button and font sizes
        if screen_width >= 1920:
            button_size = 40
            font_size = 12
            spacing = 12
        elif screen_width >= 1600:
            button_size = 36
            font_size = 11
            spacing = 10
        elif screen_width >= 1200:
            button_size = 32
            font_size = 10
            spacing = 8
        else:
            button_size = 28
            font_size = 9
            spacing = 6

        lay.setSpacing(spacing)

        self.prev_btn = QPushButton("◀")  # Using Unicode arrow for better appearance
        self.prev_btn.setObjectName("paginationPrevButton")
        self.prev_btn.setMinimumSize(button_size, button_size)
        self.prev_btn.setMaximumSize(button_size, button_size)
        self.prev_btn.setFont(QFont("Segoe UI", font_size))
        
        self.next_btn = QPushButton("▶")  # Using Unicode arrow for better appearance
        self.next_btn.setObjectName("paginationNextButton")
        self.next_btn.setMinimumSize(button_size, button_size)
        self.next_btn.setMaximumSize(button_size, button_size)
        self.next_btn.setFont(QFont("Segoe UI", font_size))
        
        self.label = QLabel()
        self.label.setObjectName("paginationLabel")
        self.label.setFont(QFont("Segoe UI", font_size, QFont.Weight.Medium.value))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set minimum width for label to prevent layout jumping
        self.label.setMinimumWidth(max(100, int(screen_width / 20)))

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

    def resizeEvent(self, event):
        """Handle resize to maintain responsive design"""
        super().resizeEvent(event)
        
        # Get current screen dimensions
        if self.parent():
            # Try to get parent window width
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, 'width'):
                parent_widget = parent_widget.parent()
            current_width = parent_widget.width() if parent_widget else QApplication.primaryScreen().availableGeometry().width()
        else:
            current_width = QApplication.primaryScreen().availableGeometry().width()
        
        # Update sizes based on current width
        if current_width >= 1920:
            button_size = 40
            font_size = 12
            spacing = 12
        elif current_width >= 1600:
            button_size = 36
            font_size = 11
            spacing = 10
        elif current_width >= 1200:
            button_size = 32
            font_size = 10
            spacing = 8
        else:
            button_size = 28
            font_size = 9
            spacing = 6

        # Update button sizes
        self.prev_btn.setMinimumSize(button_size, button_size)
        self.prev_btn.setMaximumSize(button_size, button_size)
        self.prev_btn.setFont(QFont("Segoe UI", font_size))
        
        self.next_btn.setMinimumSize(button_size, button_size)
        self.next_btn.setMaximumSize(button_size, button_size)
        self.next_btn.setFont(QFont("Segoe UI", font_size))
        
        # Update label font and width
        self.label.setFont(QFont("Segoe UI", font_size, QFont.Weight.Medium.value))
        self.label.setMinimumWidth(max(100, int(current_width / 20)))
        
        # Update layout spacing
        if self.layout():
            self.layout().setSpacing(spacing)