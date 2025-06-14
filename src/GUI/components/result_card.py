from collections import Counter
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect,
    QFrame, QSizePolicy, QScrollArea, QApplication
)
from PyQt6.QtCore   import pyqtSignal, Qt
from PyQt6.QtGui    import QFont

class ResultCard(QWidget):
    summaryRequested = pyqtSignal(int)
    viewCvRequested  = pyqtSignal(int)

    def __init__(self, detail, parent=None):
        super().__init__(parent)
        self.setObjectName("resultCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.detail = detail
        raw = getattr(detail, "matches", {})
        if isinstance(raw, dict):
            self.matches = raw
        else:
            self.matches = dict(Counter(raw))

        # Calculate responsive size based on screen dimensions
        screen = QApplication.primaryScreen()
        screen_width = screen.availableGeometry().width()
        
        # Base card size responsive to screen width
        # For screens < 1920px, scale down proportionally
        scale_factor = min(1.0, screen_width / 1920)
        base_width = int(320 * scale_factor)
        base_height = int(280 * scale_factor)
        
        # Set minimum and maximum sizes for better UX
        self.card_width = max(250, min(350, base_width))
        self.card_height = max(220, min(320, base_height))
        
        self.setMinimumSize(self.card_width, self.card_height)
        self.setMaximumSize(self.card_width, self.card_height)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 3)
        shadow.setColor(Qt.GlobalColor.gray)
        self.setGraphicsEffect(shadow)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Responsive margins based on card size
        margin = max(12, int(self.card_width * 0.04))
        main_layout.setContentsMargins(margin, margin-4, margin, margin-4)
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
        
        # Responsive font sizes
        name_font_size = max(12, int(self.card_width / 25))
        count_font_size = max(10, int(self.card_width / 30))
        
        name_label = QLabel(self.detail.name)
        name_label.setObjectName("nameLabel")
        name_label.setFont(QFont("Segoe UI", name_font_size, QFont.Weight.Bold.value))
        name_label.setWordWrap(True)
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_layout.addWidget(name_label)
        
        total_matches = sum(self.matches.values())
        count_text = f"{total_matches} match{'es' if total_matches != 1 else ''}"
        count_label = QLabel(count_text)
        count_label.setObjectName("countLabel")
        count_label.setFont(QFont("Segoe UI", count_font_size, QFont.Weight.Medium.value))
        count_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(count_label)
        
        layout.addLayout(header_layout)

    def _create_content(self, layout):
        content_font_size = max(10, int(self.card_width / 32))
        
        matched_label = QLabel("Matched Keywords:")
        matched_label.setObjectName("matchedLabel")
        matched_label.setFont(QFont("Segoe UI", content_font_size, QFont.Weight.DemiBold.value))
        layout.addWidget(matched_label)
        
        if self.matches:
            scroll_area = QScrollArea()
            scroll_area.setObjectName("keywordsScrollArea")
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            
            # Responsive scroll area height
            scroll_height = max(60, int(self.card_height * 0.25))
            scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            scroll_area.setMinimumHeight(scroll_height)
            scroll_area.setMaximumHeight(scroll_height)
            
            keywords_widget = QWidget()
            keywords_layout = QVBoxLayout(keywords_widget)
            keywords_layout.setSpacing(2)
            keywords_layout.setContentsMargins(8, 4, 8, 4)
            
            self._create_keyword_items(keywords_layout, content_font_size)
            
            scroll_area.setWidget(keywords_widget)
            layout.addWidget(scroll_area)
        else:
            no_matches = QLabel("No matches found")
            no_matches.setFont(QFont("Segoe UI", content_font_size-1))
            no_matches.setStyleSheet("color: #6c757d; font-style: italic;")
            scroll_height = max(60, int(self.card_height * 0.25))
            no_matches.setMinimumHeight(scroll_height)
            no_matches.setMaximumHeight(scroll_height)
            no_matches.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_matches)

    def _create_keyword_items(self, layout, base_font_size):
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
            keyword_label.setFont(QFont("Segoe UI", base_font_size-1, QFont.Weight.Bold.value))
            keyword_label.setStyleSheet("color: #495057;")
            keyword_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            if count > 1:
                count_label = QLabel(f"{count}x")
                count_label.setFont(QFont("Segoe UI", base_font_size-2))
                count_label.setStyleSheet("""
                    color: #ffffff;
                    background-color: #6c757d;
                    border-radius: 8px;
                    padding: 2px 6px;
                """)
                count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                count_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                item_layout.addWidget(count_label)
            
            item_layout.addWidget(keyword_label)
            
            bullet = QLabel("•")
            bullet.setFont(QFont("Segoe UI", base_font_size, QFont.Weight.Bold.value))
            bullet.setStyleSheet("color: #3498db;")
            bullet.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            
            final_layout = QHBoxLayout()
            final_layout.setContentsMargins(0, 0, 0, 0)
            final_layout.setSpacing(6)
            final_layout.addWidget(bullet)
            final_layout.addWidget(item_widget)
            
            container = QWidget()
            container.setLayout(final_layout)
            container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            layout.addWidget(container)
        
        layout.addStretch()

    def _create_buttons(self, layout):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Responsive button font size and height
        button_font_size = max(9, int(self.card_width / 35))
        button_height = max(32, int(self.card_height / 8))
        
        summary_btn = QPushButton("Summary")
        summary_btn.setObjectName("summaryButton")
        summary_btn.setFont(QFont("Segoe UI", button_font_size, QFont.Weight.Medium.value))
        summary_btn.setMinimumHeight(button_height)
        summary_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        view_btn = QPushButton("View CV")
        view_btn.setObjectName("viewCVButton")
        view_btn.setFont(QFont("Segoe UI", button_font_size, QFont.Weight.Medium.value))
        view_btn.setMinimumHeight(button_height)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        summary_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        view_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        button_layout.addWidget(summary_btn)
        button_layout.addWidget(view_btn)
        
        layout.addLayout(button_layout)
        
        summary_btn.clicked.connect(lambda: self.summaryRequested.emit(self.detail.id))
        view_btn.clicked.connect(lambda: self.viewCvRequested.emit(self.detail.id))

    def update_content(self, detail):
        self.detail = detail
        raw = getattr(detail, "matches", {})
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

    def resizeEvent(self, event):
        """Handle resize events to maintain responsiveness"""
        super().resizeEvent(event)
        # Could add dynamic updates here if needed