import os

from pathlib import Path
from collections import namedtuple

from src.db.manager import DataManager
from src.algo.kmp import KMP
from src.db.models import ApplicantProfile, ApplicationDetail
from src.gui.appState import AppState

from PyQt6.QtGui     import QDesktopServices
from PyQt6.QtCore    import QUrl

class MainController:
    def __init__(self, parent, results_area, app_state: AppState):
        self.results_area = results_area
        self.parent = parent
        self.app_state = app_state

    def search(self, keywords, algorithm, top_n):
        
        Detail = namedtuple("Detail", ["id", "name", "matches"])

        extracted_texts = self.app_state.data_manager.get_extracted_texts("clean")
        # extracted_texts = {1: "teks A A", 2: "teks B"} # masih dummy
        dummy_exact = []

        for detail_id, text in extracted_texts.items():
            matches = {}
            for keyword in keywords:
                kmp = KMP(text, keyword)
                res, _ = kmp.search()
                if res:
                    matches[keyword] = res
            if matches:
                applicant = ApplicationDetail.get_applicant(self.app_state.db, detail_id)

                if not applicant:
                    print(f"[Error] Applicant with {detail_id} detail_id not found.")
                    continue

                applicant_name = f"{applicant['first_name']} {applicant['last_name']}"

                dummy_exact.append(Detail(
                    id=detail_id,
                    name=applicant_name,
                    matches=matches
                ))

        dummy_fuzzy = [
            Detail(4, "Charlie", {"Java": 1, "Javscript": 1})
        ]

        exact = dummy_exact[:top_n]
        exec_time_exact = 120
        if exact:
            self.results_area.show_results(exact, exact_ms=exec_time_exact, fuzzy_ms=0)
        else:
            fuzzy = dummy_fuzzy[:top_n]
            exec_time_fuzzy = 200
            self.results_area.show_results(fuzzy, exact_ms=exec_time_exact, fuzzy_ms=exec_time_fuzzy)

    def show_summary(self, applicant_id: int):
        print(f"Show summary for ID {applicant_id}")

    def open_cv(self, detail_id: int):
        print(f"Open CV for ID {detail_id}")
        
        pdf_name = self.app_state.data_manager.get_cv_path(detail_id)

        if not pdf_name:
            print(f"[Error] CV for detail_id {detail_id} not found.")
            return
        
        path = Path(self.app_state.data_folder) / pdf_name
        abs_path = os.path.abspath(path)
        
        url = QUrl.fromLocalFile(abs_path)
        QDesktopServices.openUrl(url)