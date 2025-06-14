from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore   import Qt, pyqtSignal
from .result_card   import ResultCard
from .pagination    import Pagination

class ResultsArea(QWidget):
    summaryRequested = pyqtSignal(int)
    viewCvRequested  = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultsArea")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.page_size     = 8
        self.current_page  = 1
        self.exact_results = []
        self.fuzzy_results = []

        self._build_ui()

    def _build_ui(self):
        vlay = QVBoxLayout(self)
        vlay.setSpacing(12)
        vlay.setContentsMargins(0,0,0,0)

        # Header
        hdr = QHBoxLayout()
        self.lbl_exact = QLabel("Exact Match")
        self.lbl_exact.setObjectName("exactLabel")
        self.lbl_fuzzy = QLabel("Fuzzy Match")
        self.lbl_fuzzy.setObjectName("fuzzyLabel")
        hdr.addWidget(self.lbl_exact)
        hdr.addStretch()
        hdr.addWidget(self.lbl_fuzzy)
        vlay.addLayout(hdr)

        # Grid (4 cols × 2 rows)
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.setSpacing(16)
        vlay.addLayout(self.grid)
        hgrid = QHBoxLayout()
        hgrid.setContentsMargins(0,0,0,0)
        hgrid.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hgrid.addLayout(self.grid)
        vlay.addLayout(hgrid)

        vlay.addStretch()

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0,0,0,0)
        bottom.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_label = QLabel("")
        self.info_label.setObjectName("infoLabel")
        bottom.addWidget(self.info_label)
        bottom.addStretch()

        self.pagination = Pagination()
        self.pagination.pageChanged.connect(self._on_page_changed)
        bottom.addWidget(self.pagination)

        vlay.addLayout(bottom)

        self.clear()

    def clear(self):
        # remove old cards
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.lbl_fuzzy.hide()
        self.info_label.hide()
        self.pagination.hide()

    def show_results(self, exact: list, fuzzy: list):
        self.exact_results = exact
        self.fuzzy_results = fuzzy
        self.current_page  = 1

        if exact:
            self.lbl_exact.show()
            self.lbl_fuzzy.hide()
        else:
            self.lbl_exact.hide()
            if fuzzy:
                self.lbl_fuzzy.show()

        self._refresh()

    def _refresh(self):
        self.clear()
        data  = self.exact_results or self.fuzzy_results
        total = len(data)
        pages = (total + self.page_size - 1) // self.page_size
        start = (self.current_page - 1) * self.page_size
        sub   = data[start : start + self.page_size]

        # add cards
        for idx, appl in enumerate(sub):
            r, c = divmod(idx, 4)
            card = ResultCard(appl)
            card.summaryRequested.connect(self.summaryRequested)
            card.viewCvRequested.connect(self.viewCvRequested)
            self.grid.addWidget(card, r, c)

        if total:
            first = start + 1
            last  = start + len(sub)
            self.info_label.setText(f"Showing {first}–{last} of {total}")
        else:
            self.info_label.setText("No results")
        self.info_label.show()

        # update and show pagination
        self.pagination.setPage(self.current_page, pages)
        self.pagination.show()

    def _on_page_changed(self, new_page: int):
        self.current_page = new_page
        self._refresh()