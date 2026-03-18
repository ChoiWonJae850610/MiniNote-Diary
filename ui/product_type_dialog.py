
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from ui.messages import Buttons, DialogTitles
from ui.widget_factory import make_dialog_button
from ui.window_policy import lock_window_size
from ui.theme import THEME


class ProductTypeDialog(QDialog):
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.setWindowTitle(DialogTitles.PRODUCT_TYPE_MANAGE)
        self.resize(THEME.product_type_dialog_width, THEME.product_type_dialog_height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        label = QLabel('제품 타입 관리 팝업은 다음 단계에서 화면 구성을 진행합니다.', self)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)

        btn_close = make_dialog_button(Buttons.CLOSE, self, role='close')
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close, 0, Qt.AlignCenter)
        lock_window_size(self, width=THEME.product_type_dialog_width, height=THEME.product_type_dialog_height)
