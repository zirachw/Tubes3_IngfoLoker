# src/GUI/components/result_card.py
from collections import Counter
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
)
from PyQt6.QtCore   import pyqtSignal, Qt
from PyQt6.QtGui    import QFont

class ResultCard(QWidget):
    """
    Card widget: white rounded background with drop shadow,
    showing name at top, matched keywords list immediately below,
    then action buttons at the bottom.
    """
    summaryRequested = pyqtSignal(int)
    viewCvRequested  = pyqtSignal(int)

    def __init__(self, applicant, parent=None):
        super().__init__(parent)
        self.setObjectName("resultCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.applicant = applicant
        # Normalize matches: accept dict or list
        raw = getattr(applicant, "matches", {})
        if isinstance(raw, dict):
            self.matches = raw
        else:
            # raw is list[str]
            self.matches = dict(Counter(raw))

        self.setFixedSize(300, 300)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)

        # — Header: name + total count —
        header = QHBoxLayout()
        name_lbl = QLabel(self.applicant.name)
        name_lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold.value))
        total = sum(self.matches.values())
        count_lbl = QLabel(f"{total} match{'es' if total != 1 else ''}")
        count_lbl.setFont(QFont("Arial", 12))
        count_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(name_lbl)
        header.addStretch()
        header.addWidget(count_lbl)
        layout.addLayout(header)

        # — Matched keywords heading —
        mk_lbl = QLabel("Matched keywords:")
        mk_lbl.setFont(QFont("Arial", 12, QFont.Weight.DemiBold.value))
        layout.addWidget(mk_lbl)

        # — Occurrence list —
        html = "<ol style='margin:0; padding-left:16px;'>"
        for kw, cnt in self.matches.items():
            label = "occurrence" if cnt == 1 else "occurrences"
            html += f"<li>{kw}: {cnt} {label}</li>"
        html += "</ol>"
        list_lbl = QLabel(html)
        list_lbl.setTextFormat(Qt.TextFormat.RichText)
        list_lbl.setWordWrap(True)
        list_lbl.setFont(QFont("Arial", 12))
        layout.addWidget(list_lbl)

        # — Buttons row —
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_sum  = QPushButton("Summary")
        btn_sum.setObjectName("summaryButton")
        btn_view = QPushButton("View CV")
        btn_view.setObjectName("viewCVButton")
        btn_row.addWidget(btn_sum)
        btn_row.addWidget(btn_view)
        layout.addLayout(btn_row)

        btn_sum.clicked.connect(lambda: self.summaryRequested.emit(self.applicant.id))
        btn_view.clicked.connect(lambda: self.viewCvRequested.emit(self.applicant.id))
