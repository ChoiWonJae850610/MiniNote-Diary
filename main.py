# main.py
import os
import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def _apply_theme(app: QApplication) -> None:
    """
    - Fusion 스타일로 위젯 기본 룩을 통일
    - ui/theme.qss가 있으면 로드해서 전체 테마 적용
    """
    app.setStyle("Fusion")

    base_dir = os.path.abspath(os.path.dirname(__file__))
    qss_path = os.path.join(base_dir, "ui", "theme.qss")

    if os.path.isfile(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception:
            # 테마 파일 파싱/읽기 실패 시 앱은 그대로 실행
            pass


def main():
    app = QApplication(sys.argv)
    _apply_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()