import os
import time
from pathlib import Path
from collections import namedtuple

from src.db.manager import DataManager
from src.algo.kmp import KMP
from src.algo.bm import BoyerMoore
from src.algo.levenshtein import Levenshtein
from src.algo.ahocorasick import AhoCorasick
from src.db.models import ApplicantProfile, ApplicationDetail
from src.gui.appState import AppState
from src.gui.components.summary_dialog import SummaryDialog

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
        exact_res = []

        algorithm = algorithm.lower()

        start_exact = time.time()

        if algorithm == "aho-corasick":
            matcher = AhoCorasick(keywords)
            for detail_id, text in extracted_texts.items():
                matches = matcher.search(text)
                if matches:
                    applicant = ApplicationDetail.get_applicant(self.app_state.db, detail_id)
                    if not applicant:
                        print(f"[Error] Applicant with {detail_id} detail_id not found.")
                        continue
                    applicant_name = f"{applicant['first_name']} {applicant['last_name']}"
                    exact_res.append(Detail(id=detail_id, name=applicant_name, matches=matches))

        else:
            if algorithm == "kmp":
                matcher = KMP("", "")
            elif algorithm == "boyer-moore":
                matcher = BoyerMoore("", "")
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            for detail_id, text in extracted_texts.items():
                matches = {}
                matcher.text = text

                for keyword in keywords:
                    matcher.pattern = keyword.lower()
                    res, _ = matcher.search()
                    if res:
                        matches[keyword] = res

                if matches:
                    applicant = ApplicationDetail.get_applicant(self.app_state.db, detail_id)
                    if not applicant:
                        print(f"[Error] Applicant with {detail_id} detail_id not found.")
                        continue

                    applicant_name = f"{applicant['first_name']} {applicant['last_name']}"
                    exact_res.append(Detail(id=detail_id, name=applicant_name, matches=matches))

        end_exact = time.time()
        exec_time_exact = int((end_exact - start_exact) * 1000)

        exact_res.sort(key=lambda detail: sum(detail.matches.values()), reverse=True)
        exact_top = exact_res[:top_n]
        
        if exact_top:
            self.results_area.show_results(exact_top, exact_ms=exec_time_exact, fuzzy_ms=0)
        else:
            start_fuzzy = time.time()
            fuzzy_res = []
            
            for detail_id, text in extracted_texts.items():
                fuzzy_matches = {}
                
                for keyword in keywords:
                    levenshtein = Levenshtein(text, keyword)
                    
                    found, total_count, matched_strings_dict = levenshtein.search_fuzzy_matches(threshold=80.0)
                    
                    if found:
                        for matched_string, count in matched_strings_dict.items():
                            fuzzy_matches[matched_string] = count
                
                if fuzzy_matches:
                    applicant = ApplicationDetail.get_applicant(self.app_state.db, detail_id)
                    if not applicant:
                        print(f"[Error] Applicant with {detail_id} detail_id not found.")
                        continue
                    applicant_name = f"{applicant['first_name']} {applicant['last_name']}"
                    fuzzy_res.append(Detail(id=detail_id, name=applicant_name, matches=fuzzy_matches))
            
            end_fuzzy = time.time()
            exec_time_fuzzy = int((end_fuzzy - start_fuzzy) * 1000)
            fuzzy_res.sort(key=lambda detail: sum(detail.matches.values()), reverse=True)
            fuzzy_top = fuzzy_res[:top_n]
            self.results_area.show_results(fuzzy_top, exact_ms=exec_time_exact, fuzzy_ms=exec_time_fuzzy)

    def show_summary(self, detail_id: int):
        detail = ApplicationDetail.get_applicant(self.app_state.db, detail_id)

        print(f"Show summary for ID {detail['applicant_id']}")

        summary = self.app_state.data_manager.get_extracted_texts("raw")
        det = summary.get(detail_id, {})

        dialog = SummaryDialog(detail, det)
        dialog.exec()

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