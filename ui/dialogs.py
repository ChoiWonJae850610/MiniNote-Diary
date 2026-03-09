from __future__ import annotations

from typing import Sequence, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.theme import THEME, hex_to_rgba
from ui.widget_factory import make_dialog_button


def _dialog_stylesheet() -> str:
    t = THEME
    success = "#1d8f4e"
    danger = "#c23b3b"
    return f"""
        QDialog {{
            background: {t.color_window};
            color: {t.color_text};
        }}
        QFrame#dialogCard {{
            background: {t.color_surface};
            border: 1px solid {t.color_border};
            border-radius: 18px;
        }}
        QLabel#dialogTitle {{
            color: {t.color_text};
            font-size: {t.menu_title_font_px - 2}px;
            font-weight: 700;
            background: transparent;
        }}
        QLabel#dialogMessage {{
            color: {t.color_text_soft};
            font-size: {t.base_font_px + 1}px;
            background: transparent;
        }}
        QLabel#statusIconOk {{
            color: {success};
            font-size: {t.base_font_px + 3}px;
            font-weight: 800;
            background: transparent;
        }}
        QLabel#statusIconFail {{
            color: {danger};
            font-size: {t.base_font_px + 3}px;
            font-weight: 800;
            background: transparent;
        }}
        QLabel#statusTextOk {{
            color: {success};
            font-size: {t.base_font_px + 1}px;
            font-weight: 700;
            background: transparent;
        }}
        QLabel#statusTextFail {{
            color: {danger};
            font-size: {t.base_font_px + 1}px;
            font-weight: 700;
            background: transparent;
        }}
        QFrame#statusRow {{
            background: {hex_to_rgba(t.color_window, 0.92)};
            border: 1px solid {t.color_border_soft};
            border-radius: 12px;
        }}
        QPushButton#dialogConfirm {{
            min-width: 88px;
            min-height: {t.dialog_button_height}px;
            padding: 0 16px;
            border-radius: 12px;
            background: {t.color_primary};
            border: 1px solid {t.color_primary};
            color: {t.color_text_on_primary};
            font-weight: 700;
        }}
        QPushButton#dialogConfirm:hover {{
            background: {t.color_primary_hover};
            border-color: {t.color_primary_hover};
        }}
        QPushButton#dialogCancel, QPushButton#dialogClose {{
            min-width: 88px;
            min-height: {t.dialog_button_height}px;
            padding: 0 16px;
            border-radius: 12px;
            background: {t.color_surface_alt};
            border: 1px solid {t.color_border};
            color: {t.color_text_soft};
            font-weight: 700;
        }}
        QPushButton#dialogCancel:hover, QPushButton#dialogClose:hover {{
            background: {t.color_surface_muted};
            border-color: {t.color_border_hover};
        }}
    """


class _BaseThemedDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(title)
        self.setMinimumWidth(360)
        self.setStyleSheet(_dialog_stylesheet())

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)

        self.card = QFrame(self)
        self.card.setObjectName("dialogCard")
        root.addWidget(self.card)

        self.body = QVBoxLayout(self.card)
        self.body.setContentsMargins(20, 18, 20, 18)
        self.body.setSpacing(14)

        self.title_label = QLabel(title, self.card)
        self.title_label.setObjectName("dialogTitle")
        self.title_label.hide()


class ConfirmActionDialog(_BaseThemedDialog):
    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "확인",
        cancel_text: str = "취소",
        parent=None,
    ):
        super().__init__(title=title, parent=parent)
        self.setMinimumWidth(330)

        message_label = QLabel(message, self.card)
        message_label.setObjectName("dialogMessage")
        message_label.setWordWrap(True)
        self.body.addWidget(message_label)

        button_row = QHBoxLayout()
        button_row.addStretch(1)

        self.cancel_button = make_dialog_button(cancel_text, self.card)
        self.cancel_button.setObjectName("dialogCancel")
        self.cancel_button.clicked.connect(self.reject)

        self.confirm_button = make_dialog_button(confirm_text, self.card)
        self.confirm_button.setObjectName("dialogConfirm")
        self.confirm_button.clicked.connect(self.accept)
        self.confirm_button.setDefault(True)

        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.confirm_button)
        self.body.addLayout(button_row)


class ValidationStatusDialog(_BaseThemedDialog):
    def __init__(self, title: str, items: Sequence[Tuple[str, bool]], parent=None):
        super().__init__(title=title, parent=parent)
        self.setMinimumWidth(340)

        for label, ok in items:
            self.body.addWidget(self._make_status_row(label, ok))

        button_row = QHBoxLayout()
        button_row.addStretch(1)

        close_button = make_dialog_button("확인", self.card)
        close_button.setObjectName("dialogClose")
        close_button.clicked.connect(self.accept)

        button_row.addWidget(close_button)
        self.body.addLayout(button_row)

    def _make_status_row(self, label: str, ok: bool) -> QWidget:
        row = QFrame(self.card)
        row.setObjectName("statusRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        icon = QLabel("V" if ok else "X", row)
        icon.setFixedWidth(18)
        icon.setAlignment(Qt.AlignCenter)
        icon.setObjectName("statusIconOk" if ok else "statusIconFail")

        text = QLabel(label, row)
        text.setObjectName("statusTextOk" if ok else "statusTextFail")
        text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        layout.addWidget(icon)
        layout.addWidget(text, 1)
        return row
