from collections import Counter
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect,
    QFrame, QSizePolicy, QScrollArea
)
from PyQt6.QtCore   import pyqtSignal, Qt
from PyQt6.QtGui    import QFont

class ResultCard(QWidget):
    summaryRequested = pyqtSignal(int)
    viewCvRequested  = pyqtSignal(int)

    def __init__(self, applicant, parent=None):
        super().__init__(parent)
        self.setObjectName("resultCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.applicant = applicant
        raw = getattr(applicant, "matches", {})
        if isinstance(raw, dict):
            self.matches = raw
        else:
            self.matches = dict(Counter(raw))

        self.setFixedSize(320, 280)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 3)
        shadow.setColor(Qt.GlobalColor.gray)
        self.setGraphicsEffect(shadow)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # — Header Section —
        self._create_header(main_layout)
        
        # — Separator line —
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setObjectName("separator")
        separator.setMaximumHeight(1)
        main_layout.addWidget(separator)
        
        # — Content Section —
        self._create_content(main_layout)
        
        # — Action Buttons —
        self._create_buttons(main_layout)

    def _create_header(self, layout):
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        name_label = QLabel(self.applicant.name)
        name_label.setObjectName("nameLabel")
        name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold.value))
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(40)
        header_layout.addWidget(name_label)
        
        total_matches = sum(self.matches.values())
        count_text = f"{total_matches} match{'es' if total_matches != 1 else ''}"
        count_label = QLabel(count_text)
        count_label.setObjectName("countLabel")
        count_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium.value))
        count_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(count_label)
        
        layout.addLayout(header_layout)

    def _create_content(self, layout):
        matched_label = QLabel("Matched Keywords:")
        matched_label.setObjectName("matchedLabel")
        matched_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold.value))
        layout.addWidget(matched_label)
        
        if self.matches:
            scroll_area = QScrollArea()
            scroll_area.setObjectName("keywordsScrollArea")
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            
            scroll_area.setFixedHeight(75)
            
            keywords_widget = QWidget()
            keywords_layout = QVBoxLayout(keywords_widget)
            keywords_layout.setSpacing(2)
            keywords_layout.setContentsMargins(8, 4, 8, 4)
            
            self._create_keyword_items(keywords_layout)
            
            scroll_area.setWidget(keywords_widget)
            layout.addWidget(scroll_area)
        else:
            no_matches = QLabel("No matches found")
            no_matches.setFont(QFont("Segoe UI", 10))
            no_matches.setStyleSheet("color: #6c757d; font-style: italic;")
            no_matches.setFixedHeight(75)
            no_matches.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_matches)

    def _create_keyword_items(self, layout):
        """Create individual keyword items for the scroll area"""
        if not self.matches:
            return
        
        sorted_matches = sorted(
            self.matches.items(), 
            key=lambda x: (-x[1], x[0].lower())
        )
        
        for keyword, count in sorted_matches:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(4, 2, 4, 2)
            item_layout.setSpacing(8)
            
            keyword_label = QLabel(keyword)
            keyword_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold.value))
            keyword_label.setStyleSheet("color: #495057;")
            keyword_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            if count > 1:
                count_label = QLabel(f"{count}x")
                count_label.setFont(QFont("Segoe UI", 9))
                count_label.setStyleSheet("""
                    color: #ffffff;
                    background-color: #6c757d;
                    border-radius: 8px;
                    padding: 2px 6px;
                """)
                count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                count_label.setFixedSize(30, 16)
                item_layout.addWidget(count_label)
            
            item_layout.addWidget(keyword_label)
            
            bullet = QLabel("•")
            bullet.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold.value))
            bullet.setStyleSheet("color: #3498db;")
            bullet.setFixedWidth(10)
            
            final_layout = QHBoxLayout()
            final_layout.setContentsMargins(0, 0, 0, 0)
            final_layout.setSpacing(6)
            final_layout.addWidget(bullet)
            final_layout.addWidget(item_widget)
            
            container = QWidget()
            container.setLayout(final_layout)
            container.setFixedHeight(20)
            
            layout.addWidget(container)
        
        layout.addStretch()

    def _create_buttons(self, layout):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        summary_btn = QPushButton("Summary")
        summary_btn.setObjectName("summaryButton")
        summary_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium.value))
        summary_btn.setFixedHeight(36)
        summary_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        view_btn = QPushButton("View CV")
        view_btn.setObjectName("viewCVButton")
        view_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium.value))
        view_btn.setFixedHeight(36)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        summary_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        view_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        button_layout.addWidget(summary_btn)
        button_layout.addWidget(view_btn)
        
        layout.addLayout(button_layout)
        
        summary_btn.clicked.connect(lambda: self.summaryRequested.emit(self.applicant.id))
        view_btn.clicked.connect(lambda: self.viewCvRequested.emit(self.applicant.id))

    def update_content(self, applicant):
        self.applicant = applicant
        raw = getattr(applicant, "matches", {})
        if isinstance(raw, dict):
            self.matches = raw
        else:
            self.matches = dict(Counter(raw))
        
        self._clear_layout()
        self._build_ui()
    
    def _clear_layout(self):
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()