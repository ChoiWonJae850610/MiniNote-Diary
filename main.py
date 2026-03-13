# main.py
import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme import build_app_stylesheet


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    try:
        app.setStyleSheet(build_app_stylesheet())
    except Exception:
        pass


def main():
    app = QApplication(sys.argv)
    apply_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()