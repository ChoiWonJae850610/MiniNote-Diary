# main.py
import os
import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    base_dir = os.path.abspath(os.path.dirname(__file__))
    qss_path = os.path.join(base_dir, "ui", "theme.qss")
    if os.path.isfile(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
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