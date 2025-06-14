from PyQt6.QtWidgets import (
    QMainWindow, QApplication,
    QWidget, QVBoxLayout, QScrollArea
)
from PyQt6.QtCore   import Qt
from src.GUI.components.search_bar   import SearchBar
from src.GUI.components.results_area import ResultsArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("IngfoLoker – Search Demo")

        # full-screen
        screen = QApplication.primaryScreen()
        geom   = screen.availableGeometry()
        self.setGeometry(geom)

        # central + layout
        central = QWidget()
        central.setObjectName("centralWidget")
        vlay = QVBoxLayout(central)
        vlay.setContentsMargins(16,16,16,16)
        vlay.setSpacing(16)
        self.setCentralWidget(central)

        # SearchBar
        self.search_bar = SearchBar()
        vlay.addWidget(self.search_bar)

        # ResultsArea inside scroll
        self.results_area = ResultsArea()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.results_area)
        vlay.addWidget(scroll)

        # wire signals
        self.search_bar.searchRequested.connect(self.on_search)
        self.results_area.summaryRequested.connect(self.show_summary)
        self.results_area.viewCvRequested.connect(self.open_cv)

    def on_search(self, keywords, algorithm, top_n):
        # dummy data until controller is ready
        from collections import namedtuple
        Applicant = namedtuple("Applicant", ["id", "name", "matches"])
        dummy_exact = [
            Applicant(
                id=1,
                name="Farhan",
                matches={"React": 1, "Express": 2, "HTML": 1}
            ),
            Applicant(
                id=2,
                name="Aland",
                matches={"React": 1}
            ),
            Applicant(
                id=3,
                name="Ariel",
                matches={"Express": 1}
            ),
            Applicant(
                id=5,
                name="Budi",
                matches={"HTML": 1, "CSS": 1}
            ),
            Applicant(
                id=6,
                name="Dewi",
                matches={"Java": 1, "JavaScript": 1}
            ),
            Applicant(
                id=7,
                name="Eka",
                matches={"Python": 1, "Django": 1}
            ),
            Applicant(
                id=8,
                name="Fajar",
                matches={"C++": 1, "Qt": 1}
            ),
            Applicant(
                id=9,
                name="Gita",
                matches={"Ruby": 1, "Rails": 1}
            ),
            Applicant(
                id=10,
                name="Hani",
                matches={"Go": 1, "Gin": 1}
            ),
            Applicant(
                id=11,
                name="Iwan",
                matches={"PHP": 1, "Laravel": 1}
            ),
            Applicant(
                id=12,
                name="Joko",
                matches={"Swift": 1, "iOS": 1}
            ),
            Applicant(
                id=13,
                name="Kiki",
                matches={"Kotlin": 1, "Android": 1}
            ),
            Applicant(
                id=14,
                name="Lina",
                matches={"TypeScript": 1, "Angular": 1}
            ),
            Applicant(
                id=15,
                name="Maya",
                matches={"Vue.js": 1, "Nuxt.js": 1}
            ),
            Applicant(
                id=16,
                name="Nina",
                matches={"Rust": 1, "Actix": 1}
            ),
            Applicant(
                id=17,
                name="Omar",
                matches={"Scala": 1, "Akka": 1}
            ),
            Applicant(
                id=18,
                name="Putu",
                matches={"Elixir": 1, "Phoenix": 1}
            ),
            Applicant(
                id=19,
                name="Qori",
                matches={"C#": 1, "ASP.NET": 1}
            ),
            Applicant(
                id=20,
                name="Rina",
                matches={"Perl": 1, "Dancer": 1}
            )
        ]

        # For fuzzy you might use slightly different data:
        dummy_fuzzy = [
            Applicant(
                id=4,
                name="Charlie",
                matches={"Java": 1, "Javscript": 1}  # typo variant
            )
        ]
        
        
        # Then pick top_n from exact, or if none, from fuzzy:
        exact_results = dummy_exact[:top_n]
        fuzzy_results = [] if exact_results else dummy_fuzzy[:top_n]

        self.results_area.show_results(exact_results, fuzzy_results)

    def show_summary(self, applicant_id: int):
        print(f"Show summary for ID {applicant_id}")
        # TODO: open SummaryDialog

    def open_cv(self, applicant_id: int):
        print(f"Open CV for ID {applicant_id}")
        # TODO: open PDF viewer