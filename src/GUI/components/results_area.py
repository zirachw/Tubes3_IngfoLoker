import os

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QApplication, QSizePolicy
)
from PyQt6.QtCore   import Qt, pyqtSignal, QTimer
from .result_card   import ResultCard
from .pagination    import Pagination
from pathlib import Path

from src.gui.appState import AppState
from src.db.encryption import EncryptionManager

class ResultsArea(QWidget):
    summaryRequested = pyqtSignal(int)
    viewCvRequested  = pyqtSignal(int)

    def __init__(self, parent=None, app_state: AppState = None):
        super().__init__(parent)
        self.setObjectName("resultsArea")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.app_state = app_state

        self.max_columns = 3
        self.max_rows = 2
        self.page_size = 6
        self.current_page = 1
        self.results = []
        self.exact_ms = 0
        self.fuzzy_ms = 0
        
        self.card_min_width = 280
        self.card_min_height = 200
        self.card_margin = 16

        self.title_height = 40
        self.info_height = 30
        self.pagination_height = 50
        self.bottom_margin = 20

        self._build_ui()
        self._calculate_layout()

        self.count = len(self.app_state.data_manager.pdf_files)

        QTimer.singleShot(100, self._calculate_layout)

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
        
        # — Grid container for results cards —
        self.grid_container = QWidget()
        self.grid_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.grid = QGridLayout(self.grid_container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        hgrid = QHBoxLayout()
        hgrid.setContentsMargins(0, 0, 0, 0)
        hgrid.addStretch()
        hgrid.addWidget(self.grid_container)
        hgrid.addStretch()
        vlay.addLayout(hgrid)

        vlay.addStretch()

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)

        # — Label showing "Showing X–Y of Z" —
        self.showing_label = QLabel()
        self.showing_label.setObjectName("showingLabel")
        self.showing_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bottom.addWidget(self.showing_label, alignment=Qt.AlignmentFlag.AlignLeft)

        bottom.addStretch()

        # — Pagination control: "<  Page X of Y  >" —
        self.pagination = Pagination()
        self.pagination.pageChanged.connect(self._on_page_changed)
        bottom.addWidget(self.pagination, alignment=Qt.AlignmentFlag.AlignRight)

        vlay.addLayout(bottom)

        self.clear()

    def _calculate_layout(self):
        if not self.isVisible():
            return
            
        available_width = self.width()
        available_height = self.height()
        
        if available_width <= 0 or available_height <= 0:
            return
            
        available_grid_height = (available_height - 
                               self.title_height - 
                               self.info_height - 
                               self.pagination_height - 
                               self.bottom_margin - 
                               60)
        
        effective_width = available_width - 40
        max_cols = max(1, (effective_width + self.card_margin) // (self.card_min_width + self.card_margin))
        
        max_rows = max(1, (available_grid_height + self.card_margin) // (self.card_min_height + self.card_margin))
        
        max_cols = min(max_cols, 6)
        max_rows = min(max_rows, 4)
        
        old_page_size = self.page_size
        self.max_columns = max_cols
        self.max_rows = max_rows
        self.page_size = max_cols * max_rows
        
        horizontal_spacing = max(12, min(24, (effective_width - (max_cols * self.card_min_width)) // max(1, max_cols - 1)))
        vertical_spacing = max(12, min(24, (available_grid_height - (max_rows * self.card_min_height)) // max(1, max_rows - 1)))
        
        self.grid.setHorizontalSpacing(horizontal_spacing)
        self.grid.setVerticalSpacing(vertical_spacing)
        
        if (old_page_size != self.page_size and 
            hasattr(self, '_results') and 
            self._results and 
            old_page_size > 0):
            
            current_item_index = (self.current_page - 1) * old_page_size
            self.current_page = max(1, (current_item_index // self.page_size) + 1)
            self._refresh()

    def clear(self):
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

        self._calculate_layout()
        self._refresh()

    def _refresh(self):
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        data = self._results
        total = len(data)
        pages = (total + self.page_size - 1) // self.page_size if total > 0 else 1
        start = (self.current_page - 1) * self.page_size
        sub = data[start: start + self.page_size]

        for idx, detail in enumerate(sub):
            row = idx // self.max_columns
            col = idx % self.max_columns
            
            card = ResultCard(detail)
            card.summaryRequested.connect(self.summaryRequested)
            card.viewCvRequested.connect(self.viewCvRequested)
            
            self.grid.addWidget(card, row, col)

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
        self.current_page = page
        self._refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        if hasattr(self, '_resize_timer'):
            self._resize_timer.stop()
        else:
            self._resize_timer = QTimer()
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self._calculate_layout)
        
        self._resize_timer.start(100)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self._calculate_layout)