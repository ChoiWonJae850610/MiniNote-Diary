from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QFormLayout, QLabel, QPlainTextEdit, QSpinBox

from ui.button_layout_utils import make_dialog_button_row
from ui.dialogs.base import _BaseThemedDialog
from ui.messages import Buttons, Labels
from ui.widget_factory_buttons import make_dialog_button


@dataclass(frozen=True)
class InboundInspectionResult:
    defect_qty: int
    good_qty: int
    inspection_memo: str
    inspection_exempt: bool


class InboundInspectionDialog(_BaseThemedDialog):
    def __init__(self, *, inbound_qty: int, parent=None):
        super().__init__(title='검수 입력', parent=parent)
        self.inbound_qty = max(0, int(inbound_qty or 0))

        desc = QLabel(f'이번 입고 수량 {self.inbound_qty}개 기준으로 검수 내용을 입력하세요.', self.card)
        desc.setObjectName('dialogMessage')
        desc.setWordWrap(True)
        self.body.addWidget(desc)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.lbl_inbound_qty = QLabel(str(self.inbound_qty), self.card)
        form.addRow(Labels.INBOUND_QTY, self.lbl_inbound_qty)

        self.exempt_check = QCheckBox('검수 예외처리 (나중에 상품관리에서 검수)', self.card)
        self.exempt_check.toggled.connect(self._apply_exempt_state)
        form.addRow('', self.exempt_check)

        self.defect_spin = QSpinBox(self.card)
        self.defect_spin.setRange(0, self.inbound_qty)
        self.defect_spin.valueChanged.connect(self._refresh_good_qty)
        form.addRow('불량 수량', self.defect_spin)

        self.lbl_good_qty = QLabel(str(self.inbound_qty), self.card)
        form.addRow('정상 반영 수량', self.lbl_good_qty)

        self.memo_edit = QPlainTextEdit(self.card)
        self.memo_edit.setPlaceholderText('검수 메모를 입력하세요')
        self.memo_edit.setFixedHeight(110)
        form.addRow(Labels.MEMO, self.memo_edit)

        self.body.addLayout(form)

        self.cancel_button = make_dialog_button(Buttons.CANCEL, self.card, role='cancel')
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button = make_dialog_button(Buttons.OK, self.card, role='confirm')
        self.confirm_button.clicked.connect(self.accept)
        self.confirm_button.setDefault(True)
        self.body.addLayout(make_dialog_button_row([self.cancel_button, self.confirm_button]))

    def _apply_exempt_state(self, checked: bool) -> None:
        self.defect_spin.setEnabled(not checked)
        self.memo_edit.setPlaceholderText('검수 예외 사유를 입력하세요' if checked else '검수 메모를 입력하세요')
        if checked:
            self.defect_spin.setValue(0)
            self.lbl_good_qty.setText('미반영')
        else:
            self._refresh_good_qty()

    def _refresh_good_qty(self) -> None:
        self.lbl_good_qty.setText(str(max(0, self.inbound_qty - self.defect_spin.value())))

    def result_data(self) -> InboundInspectionResult:
        inspection_exempt = self.exempt_check.isChecked()
        defect_qty = 0 if inspection_exempt else max(0, min(self.inbound_qty, self.defect_spin.value()))
        good_qty = 0 if inspection_exempt else max(0, self.inbound_qty - defect_qty)
        return InboundInspectionResult(
            defect_qty=defect_qty,
            good_qty=good_qty,
            inspection_memo=self.memo_edit.toPlainText().strip(),
            inspection_exempt=inspection_exempt,
        )
