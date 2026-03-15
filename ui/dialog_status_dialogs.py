from __future__ import annotations

from typing import Sequence, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from ui.button_layout_utils import make_dialog_button_row
from ui.dialog_base import _BaseThemedDialog
from ui.layout_metrics import DialogLayout
from ui.messages import Buttons, Symbols
from ui.theme import status_row_margins
from ui.widget_factory_buttons import make_dialog_button


class ValidationStatusDialog(_BaseThemedDialog):
    def __init__(self, title: str, items: Sequence[Tuple[str, bool]], parent=None):
        super().__init__(title=title, parent=parent)

        for label, ok in items:
            self.body.addWidget(self._make_status_row(label, ok))

        close_button = make_dialog_button(Buttons.OK, self.card, role="close")
        close_button.clicked.connect(self.accept)
        self.body.addLayout(make_dialog_button_row([close_button]))

    def _make_status_row(self, label: str, ok: bool) -> QWidget:
        row = QFrame(self.card)
        row.setObjectName("statusRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(*status_row_margins())
        layout.setSpacing(DialogLayout.STATUS_ROW_SPACING)

        icon = QLabel(Symbols.STATUS_OK if ok else Symbols.STATUS_FAIL, row)
        icon.setFixedWidth(DialogLayout.STATUS_ICON_WIDTH)
        icon.setAlignment(Qt.AlignCenter)
        icon.setObjectName("statusIconOk" if ok else "statusIconFail")

        text = QLabel(label, row)
        text.setObjectName("statusTextOk" if ok else "statusTextFail")
        text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        layout.addWidget(icon)
        layout.addWidget(text, 1)
        return row


__all__ = ["ValidationStatusDialog"]
