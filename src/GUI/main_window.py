from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from src.gui.appState import AppState
from src.gui.components.search_bar import SearchBar
from src.gui.components.results_area import ResultsArea
from src.controller.main_controller import MainController

class MainWindow(QMainWindow):
    def __init__(self, app_state: AppState):
        super().__init__()

        self.app_state = app_state
        self.setObjectName("MainWindow")
        self.setWindowTitle("IngfoLoker - Job Applicant Search")

        screen = QApplication.primaryScreen()
        geom = screen.availableGeometry()
        
        width = int(geom.width() * 0.9)
        height = int(geom.height() * 0.9) 
        x = (geom.width() - width) // 2
        y = (geom.height() - height) // 2
        
        self.setGeometry(x, y, width, height)
        self.setMinimumSize(800, 600)

        central = QWidget()
        central.setObjectName("centralWidget")
        vlay = QVBoxLayout(central)
        
        margin = max(20, int(width * 0.05))
        vlay.setContentsMargins(margin, 16, margin, 16)
        vlay.setSpacing(16)
        self.setCentralWidget(central)

        self.title = QLabel("CV Analyzer App")
        self.title.setObjectName("titleLabel")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vlay.addWidget(self.title)

        self.search_bar = SearchBar()
        vlay.addWidget(self.search_bar)

        self.results_area = ResultsArea()
        self.results_area.setObjectName("resultsArea")
        vlay.addWidget(self.results_area, 1)

        self.controller = MainController(self, self.results_area, self.app_state)

        self.search_bar.searchRequested.connect(self.controller.search)
        self.results_area.summaryRequested.connect(self.controller.show_summary)
        self.results_area.viewCvRequested.connect(self.controller.open_cv)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        width = self.width()
        margin = max(20, int(width * 0.05))
        
        central_widget = self.centralWidget()
        if central_widget and central_widget.layout():
            central_widget.layout().setContentsMargins(margin, 16, margin, 16)