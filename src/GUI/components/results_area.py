import os

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QApplication, QSizePolicy
)
from PyQt6.QtCore   import Qt, pyqtSignal
from .result_card   import ResultCard
from .pagination    import Pagination
from pathlib import Path

from src.gui.appState import AppState

class ResultsArea(QWidget):
    summaryRequested = pyqtSignal(int)
    viewCvRequested  = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultsArea")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Calculate responsive grid columns based on screen width
        screen = QApplication.primaryScreen()
        screen_width = screen.availableGeometry().width()
        
        # Dynamic columns based on screen width
        if screen_width >= 1920:
            self.max_columns = 5
        elif screen_width >= 1600:
            self.max_columns = 4
        elif screen_width >= 1200:
            self.max_columns = 3
        elif screen_width >= 800:
            self.max_columns = 2
        else:
            self.max_columns = 1
            
        # Dynamic page size based on columns
        self.page_size = self.max_columns * 2  # 2 rows per page
        self.current_page = 1
        self.results = []
        self.exact_ms = 0
        self.fuzzy_ms = 0

        self._build_ui()

        data_path = Path(os.getenv("DATA_FOLDER"))
        if not data_path.exists():
            self.count = 0
        else:
            self.count = len(list(data_path.glob("*.pdf")))

    def _build_ui(self):
        vlay = QVBoxLayout(self)
        vlay.setSpacing(12)
        vlay.setContentsMargins(0, 0, 0, 0)

        # — Title "Results:" —
        self.title_label = QLabel("Results:")
        self.title_label.setObjectName("resultsTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vlay.addWidget(self.title_label)

        # — Info label: "Exact Matches: X CVs scanned in Y ms" —
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 0, 0, 0)

        self.infoExact = QLabel()
        self.infoExact.setObjectName("infoExact")
        self.infoExact.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        info_row.addWidget(self.infoExact, alignment=Qt.AlignmentFlag.AlignLeft)

        info_row.addStretch()

        self.infoFuzzy = QLabel()
        self.infoFuzzy.setObjectName("infoFuzzy")
        self.infoFuzzy.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        info_row.addWidget(self.infoFuzzy, alignment=Qt.AlignmentFlag.AlignRight)

        vlay.addLayout(info_row)
        
        # Create responsive grid container
        self.grid_container = QWidget()
        self.grid_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.grid = QGridLayout(self.grid_container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        # Responsive spacing based on screen size
        screen = QApplication.primaryScreen()
        screen_width = screen.availableGeometry().width()
        spacing = max(12, int(screen_width / 120))  # Adaptive spacing
        
        self.grid.setHorizontalSpacing(spacing)
        self.grid.setVerticalSpacing(spacing)
        
        # Center the grid
        hgrid = QHBoxLayout()
        hgrid.setContentsMargins(0, 0, 0, 0)
        hgrid.addStretch()
        hgrid.addWidget(self.grid_container)
        hgrid.addStretch()
        vlay.addLayout(hgrid)

        vlay.addStretch()

        # Bottom section with pagination
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)

        self.showing_label = QLabel()
        self.showing_label.setObjectName("showingLabel")
        self.showing_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bottom.addWidget(self.showing_label, alignment=Qt.AlignmentFlag.AlignLeft)

        bottom.addStretch()

        self.pagination = Pagination()
        self.pagination.pageChanged.connect(self._on_page_changed)
        bottom.addWidget(self.pagination, alignment=Qt.AlignmentFlag.AlignRight)

        vlay.addLayout(bottom)

        self.clear()

    def clear(self):
        """Clear all widgets from the grid"""
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        self.title_label.hide()
        self.infoExact.hide()
        self.infoFuzzy.hide()
        self.showing_label.hide()
        self.pagination.hide()

    def show_results(self, results: list, exact_ms: int, fuzzy_ms: int):
        """
        Display either Exact or Fuzzy results:
        - `results`: list of Applicant to show in cards
        - `exact_ms`: execution time for exact (0 if not used)
        - `fuzzy_ms`: execution time for fuzzy (0 if not used)
        """
        self.clear()
        self._results = results
        self._exact_ms = exact_ms
        self._fuzzy_ms = fuzzy_ms
        self.current_page = 1

        self.title_label.show()
        total = self.count
        self.infoExact.setText(f"Exact Matches: {total} CVs scanned in {exact_ms} ms")
        self.infoExact.show()

        if fuzzy_ms:
            self.infoFuzzy.setText(f"Fuzzy Matches: {total} CVs scanned in {fuzzy_ms} ms")
            self.infoFuzzy.show()
        else:
            self.infoFuzzy.hide()

        self._refresh()

    def _refresh(self):
        """Refresh the current page display"""
        # Clear existing widgets
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        data = self._results
        total = len(data)
        pages = (total + self.page_size - 1) // self.page_size if total > 0 else 1
        start = (self.current_page - 1) * self.page_size
        sub = data[start: start + self.page_size]

        # Add cards to grid with responsive layout
        for idx, detail in enumerate(sub):
            row = idx // self.max_columns
            col = idx % self.max_columns
            
            card = ResultCard(detail)
            card.summaryRequested.connect(self.summaryRequested)
            card.viewCvRequested.connect(self.viewCvRequested)
            
            # Add card to grid
            self.grid.addWidget(card, row, col)

        # Update pagination and showing label
        if total:
            first = start + 1
            last = start + len(sub)
            self.showing_label.setText(f"Showing {first}–{last} of {total}")
        else:
            self.showing_label.setText("No results")
        self.showing_label.show()

        self.pagination.setPage(self.current_page, pages)
        self.pagination.show()

    def _on_page_changed(self, page: int):
        """Handle page change event"""
        self.current_page = page
        self._refresh()

    def resizeEvent(self, event):
        """Handle window resize to update responsive layout"""
        super().resizeEvent(event)
        
        # Recalculate columns based on new size
        if self.parent():
            parent_width = self.parent().width()
        else:
            screen = QApplication.primaryScreen()
            parent_width = screen.availableGeometry().width()
        
        # Update max columns based on current width
        old_columns = self.max_columns
        
        if parent_width >= 1920:
            self.max_columns = 5
        elif parent_width >= 1600:
            self.max_columns = 4
        elif parent_width >= 1200:
            self.max_columns = 3
        elif parent_width >= 800:
            self.max_columns = 2
        else:
            self.max_columns = 1
        
        # Update page size and refresh if columns changed
        if old_columns != self.max_columns:
            self.page_size = self.max_columns * 2
            # Adjust current page to maintain roughly the same position
            if hasattr(self, '_results') and self._results:
                current_item = (self.current_page - 1) * (old_columns * 2)
                self.current_page = max(1, (current_item // self.page_size) + 1)
                self._refresh()
        
        # Update grid spacing
        spacing = max(12, int(parent_width / 120))
        self.grid.setHorizontalSpacing(spacing)
        self.grid.setVerticalSpacing(spacing)