from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFrame, QLabel, QVBoxLayout

from ui.ui_metrics import CommonSymbolsLayout
from ui.theme import THEME, dialog_inner_margins, dialog_layout_margins


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
