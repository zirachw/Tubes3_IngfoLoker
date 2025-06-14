import os

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
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

        self.page_size     = 10
        self.current_page  = 1
        self.results = []
        self.exact_ms      = 0
        self.fuzzy_ms      = 0

        self._build_ui()

        data_path = Path(os.getenv("DATA_FOLDER"))
        if not data_path.exists():
            self.count = 0

        else:
            self.count = len(list(data_path.glob("*.pdf")))

    def _build_ui(self):
        vlay = QVBoxLayout(self)
        vlay.setSpacing(12)
        vlay.setContentsMargins(0,0,0,0)

        # — Title “Results:” —
        self.title_label = QLabel("Results:")
        self.title_label.setObjectName("resultsTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vlay.addWidget(self.title_label)

        # — Info label: “Exact Matches: X CVs scanned in Y ms” —
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0,0,0,0)

        self.infoExact = QLabel()
        self.infoExact.setObjectName("infoExact")
        info_row.addWidget(self.infoExact, alignment=Qt.AlignmentFlag.AlignLeft)

        info_row.addStretch()

        self.infoFuzzy = QLabel()
        self.infoFuzzy.setObjectName("infoFuzzy")
        info_row.addWidget(self.infoFuzzy, alignment=Qt.AlignmentFlag.AlignRight)

        vlay.addLayout(info_row)
        
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.setHorizontalSpacing(16)
        self.grid.setVerticalSpacing(16)

        hgrid = QHBoxLayout()
        hgrid.setContentsMargins(0,0,0,0)
        hgrid.addStretch()             
        hgrid.addLayout(self.grid)      
        hgrid.addStretch()
        vlay.addLayout(hgrid)

        vlay.addStretch()

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0,0,0,0)

        self.showing_label = QLabel()
        self.showing_label.setObjectName("showingLabel")
        bottom.addWidget(self.showing_label, alignment=Qt.AlignmentFlag.AlignLeft)

        bottom.addStretch()

        self.pagination = Pagination()
        self.pagination.pageChanged.connect(self._on_page_changed)
        bottom.addWidget(self.pagination, alignment=Qt.AlignmentFlag.AlignRight)

        vlay.addLayout(bottom)

        self.clear()

    def clear(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)
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
            self._results  = results
            self._exact_ms = exact_ms
            self._fuzzy_ms = fuzzy_ms
            self.current_page = 1

            self.title_label.show()
            total = len(results)
            self.infoExact.setText(f"Exact Matches: {total} CVs scanned in {exact_ms} ms")
            self.infoExact.show()

            if fuzzy_ms:
                self.infoFuzzy.setText(f"Fuzzy Matches: {total} CVs scanned in {fuzzy_ms} ms")
                self.infoFuzzy.show()
            else:
                self.infoFuzzy.hide()

            self._refresh()

    def _refresh(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        data  = self._results
        total = self.count
        pages = (total + self.page_size - 1) // self.page_size
        start = (self.current_page - 1) * self.page_size
        sub   = data[start : start + self.page_size]

        for idx, detail in enumerate(sub):
            r, c = divmod(idx, 5)
            card = ResultCard(detail)
            card.summaryRequested.connect(self.summaryRequested)
            card.viewCvRequested.connect(self.viewCvRequested)
            self.grid.addWidget(card, r, c)

        if total:
            first = start + 1
            last  = start + len(sub)
            self.showing_label.setText(f"Showing {first}–{last} of {total}")
        else:
            self.showing_label.setText("No results")
        self.showing_label.show()

        self.pagination.setPage(self.current_page, pages)
        self.pagination.show()

    def _on_page_changed(self, page: int):
        self.current_page = page
        self._refresh()