from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QSpinBox,
    QHBoxLayout, QVBoxLayout, QButtonGroup
)
from PyQt6.QtCore   import Qt, pyqtSignal

class SearchBar(QWidget):
    searchRequested = pyqtSignal(str, str, int)

    def __init__(self):
        super().__init__()
        self.setObjectName("searchBar")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(8)
        lay.setContentsMargins(0,0,0,0)

        # Keywords
        lay.addWidget(QLabel("Keywords:"))
        self.input = QLineEdit()
        self.input.setPlaceholderText("e.g. React, Express, HTML")
        lay.addWidget(self.input)

        # Controls row
        row = QHBoxLayout()
        row.setSpacing(12)
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row.addWidget(QLabel("Search Algorithm:"))
        self.btn_kmp = QPushButton("KMP")
        self.btn_bm  = QPushButton("Boyer-Moore")
        self.btn_ah  = QPushButton("Aho-Corasick")
        for btn in (self.btn_kmp, self.btn_bm, self.btn_ah):
            btn.setCheckable(True)
            row.addWidget(btn)
        grp = QButtonGroup(self)
        grp.setExclusive(True)
        for b in (self.btn_kmp, self.btn_bm, self.btn_ah):
            grp.addButton(b)
        self.btn_kmp.setChecked(True)

        row.addSpacing(32)
        row.addWidget(QLabel("Top Matches:"))
        self.top_n = QSpinBox()
        self.top_n.setRange(1, 100)
        self.top_n.setValue(5)
        row.addWidget(self.top_n)

        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self._on_search)
        row.addWidget(self.btn_search)

        lay.addLayout(row)

    def _on_search(self):
        kws = self.input.text().strip()
        if self.btn_kmp.isChecked():
            alg = "KMP"
        elif self.btn_bm.isChecked():
            alg = "Boyer-Moore"
        else:
            alg = "Aho-Corasick"
        self.searchRequested.emit(kws, alg, self.top_n.value())
