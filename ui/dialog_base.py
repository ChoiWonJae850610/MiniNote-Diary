from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFrame, QLabel, QVBoxLayout
from ui.theme import THEME, hex_to_rgba
from ui.ui_metrics import CommonSymbolsLayout




def build_dialog_shell(dialog: QDialog, title: str) -> tuple[QFrame, QVBoxLayout, QLabel]:
    dialog.setModal(True)
    dialog.setWindowTitle(title)
    dialog.setMinimumWidth(CommonSymbolsLayout.DIALOG_MIN_WIDTH_LG)

    root = QVBoxLayout(dialog)
    root.setContentsMargins(*dialog_layout_margins())

    card = QFrame(dialog)
    card.setObjectName("dialogCard")
    root.addWidget(card)

    body = QVBoxLayout(card)
    body.setContentsMargins(*dialog_inner_margins())
    body.setSpacing(THEME.section_gap)

    title_label = QLabel(title, card)
    title_label.setObjectName("dialogTitle")
    title_label.hide()
    return card, body, title_label

def dialog_stylesheet() -> str:
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
    def __init__(self, title: str, parent=None, *, minimum_width: int = CommonSymbolsLayout.DIALOG_MIN_WIDTH_LG):
        super().__init__(parent)
        self.setStyleSheet(dialog_stylesheet())
        self.card, self.body, self.title_label = build_dialog_shell(self, title)
        self.setMinimumWidth(minimum_width)


__all__ = ["_BaseThemedDialog", "build_dialog_shell", "dialog_stylesheet"]
