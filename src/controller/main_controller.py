from collections import namedtuple
import os
from src.utils.data import DataManager
from src.algo.kmp import KMP
from src.gui.components.pdf_viewer import PdfViewer

class MainController:
    def __init__(self, results_area, parent):
        self.results_area = results_area
        self.parent = parent

    def search(self, keywords, algorithm, top_n):
        print(keywords)
        
        Detail = namedtuple("Detail", ["id", "name", "matches"])

        # extracted_texts = DataManager.get_extracted_texts()
        extracted_texts = [{1: "teks A A"}, {2: "teks B"}] # masih dummy
        dummy_exact = []

        for entry in extracted_texts:
            for detail_id, text in entry.items():
                matches = {}
                for keyword in keywords:
                    print("Ini keyword",keyword)
                    kmp = KMP(text, keyword)
                    res, _ = kmp.search()
                    if res:
                        matches[keyword] = res
                        print(res)
                if matches:
                    dummy_exact.append(Detail(
                        id=detail_id,
                        name=f"Detail {detail_id}",
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

    def open_cv(self, applicant_id: int):
        print(f"Open CV for ID {applicant_id}")
        pdf_map = {
            1: "data/Tucil3_13523045.pdf",
            2: "data/Tucil3_13523045.pdf",
        }
        path = pdf_map.get(applicant_id)
        print(f"This is path: {path}")
        if not path:
            print(f"[Error] Tidak ada mapping PDF untuk ID {applicant_id}")
            return

        abs_path = os.path.abspath(path)
        if not os.path.isfile(abs_path):
            print(f"[Error] File PDF tidak ditemukan: {abs_path}")
            return

        dlg = PdfViewer(abs_path, self.parent)
        dlg.exec()
