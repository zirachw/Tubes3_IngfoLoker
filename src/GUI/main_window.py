from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from src.gui.components.search_bar import SearchBar
from src.gui.components.results_area import ResultsArea
from src.controller.main_controller import MainController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("IngfoLoker - Job Applicant Search")

        screen = QApplication.primaryScreen()
        geom = screen.availableGeometry()
        self.setGeometry(geom)

        central = QWidget()
        central.setObjectName("centralWidget")
        vlay = QVBoxLayout(central)
        vlay.setContentsMargins(100, 16, 100, 16)
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
        vlay.addWidget(self.results_area)

        self.controller = MainController(self.results_area, self)

        self.search_bar.searchRequested.connect(self.controller.search)
        self.results_area.summaryRequested.connect(self.controller.show_summary)
        self.results_area.viewCvRequested.connect(self.controller.open_cv)
