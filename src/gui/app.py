import sys

from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.gui.appState import AppState

class App:
    """Main application class that initializes the GUI and runs the event loop."""

    def __init__(self):
        """Initialize the application state."""

        self.state = AppState()

    def run(self):
        """Initialize the application, load styles, and start the main window."""
        
        try:
            self.state.run()
            app = QApplication(sys.argv)
            
            with open("src/gui/resources/style.qss", "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            
            window = MainWindow(self.state)
            window.show()
            
            exit_code = app.exec()
            sys.exit(exit_code)

        except KeyboardInterrupt:
            print(f"[Log] - Application interrupted by user.")
            sys.exit(0)

        except Exception as e:
            print(f"[Error] - Running application: {e}")
            sys.exit(1)

        finally:
            self.state.end()
            print("[Log] - Application closed and resources cleaned up.")