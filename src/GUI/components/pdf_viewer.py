from PyQt6.QtWidgets          import QDialog, QVBoxLayout, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore    import QWebEngineSettings
from PyQt6.QtCore             import QUrl
import os

class PdfViewer(QDialog):
    def __init__(self, pdf_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Viewer")
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.setGeometry(0, 0, size.width(), size.height())

        layout = QVBoxLayout(self)

        # 1) Buat widget QWebEngineView
        self.viewer = QWebEngineView(self)

        # 2) Aktifkan PDF plugin di settings
        settings = self.viewer.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

        # 3) Muat PDF sebagai URL file absolut
        abs_path = os.path.abspath(pdf_path)
        url = QUrl.fromLocalFile(abs_path)
        self.viewer.setUrl(url)

        layout.addWidget(self.viewer)
