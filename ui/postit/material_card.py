from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QMenu, QSizePolicy, QToolButton, QVBoxLayout

from services.formatters import digits_only, format_commas_from_digits
from services.unit_repository import load_units, unit_label_for_value
from ui.postit.base import _PostItCardBase
from ui.icon_factory import make_partner_link_icon
from ui.postit.common import FIELD_H, make_down_icon
from ui.postit.layout import POSTIT_INNER_TOP_PADDING, POSTIT_INNER_BOTTOM_PADDING, POSTIT_INNER_SIDE_PADDING, POSTIT_SECTION_SPACING, POSTIT_GRID_H_SPACING, POSTIT_GRID_V_SPACING, POSTIT_ROW_ACTION_GAP
from ui.partner_ui_utils import PARTNER_PICKER_TYPE_FABRIC, PARTNER_PICKER_TYPE_OTHER, show_partner_picker
from ui.postit.editors import _ClickToEditLineEdit, _MoneyLineEdit, _QtyClickToEditLineEdit
from ui.theme import THEME, delete_button_style, field_label_style, input_line_edit_style, menu_style, unit_button_style, tool_button_style


class PostItCard(_PostItCardBase):
    delete_clicked = Signal(int)
    selected = Signal(int)
    data_changed = Signal(int, dict)

    def __init__(self, kind: str, index: int, data: Dict[str, str], parent=None):
        super().__init__(kind, parent=parent)
        self.index = index
        self.data = dict(data or {})
        self._block_total = False
        self._syncing_data = False
        self._units = load_units()
        self._unit_value = (self.data.get("단위") or "").strip()
        self._unit_label = unit_label_for_value(self._unit_value, self._units)
        self._suppress_unit_menu_once = False

        root = QVBoxLayout(self)
        root.setContentsMargins(POSTIT_INNER_SIDE_PADDING, POSTIT_INNER_TOP_PADDING, POSTIT_INNER_SIDE_PADDING, POSTIT_INNER_BOTTOM_PADDING)
        root.setSpacing(POSTIT_SECTION_SPACING)

        self.btn_delete = QToolButton(self)
        self.btn_delete.setText("×")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setFixedSize(THEME.delete_button_size, THEME.delete_button_size)
        self.btn_delete.setStyleSheet(delete_button_style())
        self.btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.index))

        vi = QGridLayout()
        vi.setContentsMargins(0, 0, 0, 0)
        vi.setHorizontalSpacing(POSTIT_GRID_H_SPACING)
        vi.setVerticalSpacing(POSTIT_GRID_V_SPACING)

        def mk_label(text: str) -> QLabel:
            label = QLabel(text, self)
            label.setFixedWidth(THEME.field_label_width)
            label.setFixedHeight(FIELD_H)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setStyleSheet(field_label_style())
            return label

        self.vendor = _ClickToEditLineEdit(self)
        self.item = _ClickToEditLineEdit(self)
        self.btn_vendor_partner = QToolButton(self)
        self.btn_vendor_partner.setIcon(make_partner_link_icon(14))
        self.btn_vendor_partner.setIconSize(QSize(14, 14))
        self.btn_vendor_partner.setFixedSize(FIELD_H, FIELD_H)
        self.btn_vendor_partner.setCursor(Qt.PointingHandCursor)
        self.btn_vendor_partner.setToolTip('거래처 관리')
        self.btn_vendor_partner.setStyleSheet(tool_button_style())
        self.btn_vendor_partner.clicked.connect(self._open_vendor_picker)
        self.vendor.set_text_silent(self.data.get("거래처", ""))
        self.data["거래처_id"] = self.data.get("거래처_id", "")
        self.item.set_text_silent(self.data.get("품목", ""))
        vi.addWidget(mk_label("원단처" if self.kind == "fabric" else "거래처"), 0, 0)
        vendor_row = QHBoxLayout()
        vendor_row.setContentsMargins(0, 0, 0, 0)
        vendor_row.setSpacing(POSTIT_ROW_ACTION_GAP)
        vendor_row.addWidget(self.vendor, 1)
        vendor_row.addWidget(self.btn_vendor_partner, 0)
        vi.addLayout(vendor_row, 0, 1)
        vi.addWidget(mk_label("품  목"), 1, 0)
        vi.addWidget(self.item, 1, 1)
        root.addLayout(vi)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(POSTIT_GRID_H_SPACING)
        grid.setVerticalSpacing(POSTIT_GRID_V_SPACING)

        self.qty = _QtyClickToEditLineEdit(self)
        self.qty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.qty.set_text_silent(self.data.get("수량", ""))

        self.unit_btn = QToolButton(self)
        self.unit_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.unit_btn.setIcon(make_down_icon(12))
        self.unit_btn.setIconSize(QSize(12, 12))
        self.unit_btn.setCursor(Qt.PointingHandCursor)
        self.unit_btn.setFixedHeight(FIELD_H)
        self.unit_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.unit_btn.setStyleSheet(unit_button_style())
        self._apply_unit_button_text()
        self._unit_menu = QMenu(self.unit_btn)
        self._unit_menu.setStyleSheet(menu_style())
        self._unit_actions: Dict[str, object] = {}
        self._act_clear_unit = self._unit_menu.addAction("(비움)")
        self._act_clear_unit.setCheckable(True)
        self._act_clear_unit.triggered.connect(lambda: self._set_unit("", ""))
        if self._units:
            self._unit_menu.addSeparator()
        else:
            hint = self._unit_menu.addAction("(단위 목록 없음)")
            hint.setEnabled(False)
        for unit, label in self._units:
            action = self._unit_menu.addAction(label)
            action.setCheckable(True)
            action.triggered.connect(lambda _=False, u=unit, lb=label: self._set_unit(u, lb))
            self._unit_actions[unit] = action
        self._unit_menu.aboutToShow.connect(self._sync_unit_menu_checks)
        self.unit_btn.setMenu(self._unit_menu)
        self.unit_btn.setPopupMode(QToolButton.InstantPopup)
        self.unit_btn.installEventFilter(self)

        self.price = _MoneyLineEdit(self)
        self.total = _MoneyLineEdit(self)
        for widget in (self.price, self.total):
            widget.setStyleSheet(input_line_edit_style())
        self.price.setText(self.data.get("단가", ""))
        self.total.setText(self.data.get("총액", ""))

        def mk_label2(text: str) -> QLabel:
            label = QLabel(text, self)
            label.setFixedWidth(THEME.field_label_width)
            label.setFixedHeight(FIELD_H)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setStyleSheet(field_label_style())
            return label

        grid.addWidget(mk_label2("수  량"), 0, 0)
        grid.addWidget(self.qty, 0, 1)
        grid.addWidget(mk_label2("단위"), 0, 2)
        grid.addWidget(self.unit_btn, 0, 3)
        grid.addWidget(mk_label2("단  가"), 1, 0)
        grid.addWidget(self.price, 1, 1, 1, 3)
        grid.addWidget(mk_label2("총  액"), 2, 0)
        grid.addWidget(self.total, 2, 1, 1, 3)
        root.addLayout(grid)

        self.vendor.committed.connect(self._on_vendor_committed)
        self.item.committed.connect(lambda value: self._commit("품목", value))
        self.qty.committed.connect(self._on_qty_committed)
        self.qty.textChanged.connect(lambda _t: self._recalc_total())
        self.price.textChanged.connect(lambda _t: self._on_price_changed())
        self.total.textChanged.connect(lambda _t: None if self._block_total else self._commit("총액", self.total.text()))

        self.setTabOrder(self.vendor, self.item)
        self.setTabOrder(self.item, self.qty)
        self.setTabOrder(self.qty, self.unit_btn)
        self.setTabOrder(self.unit_btn, self.price)
        self.setTabOrder(self.price, self.total)
        self.price._pending_prev_widget = self.unit_btn
        self.price._pending_next_widget = self.total
        self.total._pending_prev_widget = self.price

        self.setMinimumSize(QSize(320, THEME.postit_card_height))
        self.setMaximumHeight(THEME.postit_card_height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


    def _partner_type_for_picker(self) -> str:
        return PARTNER_PICKER_TYPE_FABRIC if self.kind == "fabric" else PARTNER_PICKER_TYPE_OTHER

    def _open_vendor_picker(self):
        def _apply(partner):
            self.vendor.set_text_silent(partner.name)
            self.data["거래처_id"] = partner.id
            self._commit("거래처", partner.name)

        show_partner_picker(self.btn_vendor_partner, partner_type=self._partner_type_for_picker(), on_selected=_apply)


    def _on_vendor_committed(self, value: str):
        self.data["거래처_id"] = ""
        self._commit("거래처", value)

    def _apply_unit_button_text(self):
        self.unit_btn.setText((self._unit_value or "").strip())

    def _sync_unit_menu_checks(self):
        current = (self._unit_value or "").strip()
        self._act_clear_unit.setChecked(not bool(current))
        for unit, action in self._unit_actions.items():
            action.setChecked(bool(current) and unit == current)

    def _set_unit(self, unit: str, label: str):
        self._unit_value = unit or ""
        self._unit_label = label or ""
        self._apply_unit_button_text()
        self._commit("단위", self._unit_value)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.unit_btn.hasFocus():
            self._set_unit("", "")
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.index)
        super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        if obj is self.unit_btn and self._suppress_unit_menu_once:
            if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick):
                self._suppress_unit_menu_once = False
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def suppress_unit_menu_once(self):
        self._suppress_unit_menu_once = True

    def resizeEvent(self, event):
        self.btn_delete.move(self.width() - (THEME.delete_button_size + 4), 6)
        super().resizeEvent(event)

    def update_data(self, data: Dict[str, str]):
        self._syncing_data = True
        try:
            self.data = dict(data or {})
            self._unit_value = (self.data.get("단위") or "").strip()
            self._unit_label = unit_label_for_value(self._unit_value, self._units)
            widgets = (self.vendor, self.item, self.qty, self.price, self.total)
            blocked = [(widget, widget.blockSignals(True)) for widget in widgets]
            try:
                self.vendor.set_text_silent(self.data.get("거래처", ""))
                self.data["거래처_id"] = self.data.get("거래처_id", "")
                self.item.set_text_silent(self.data.get("품목", ""))
                self.qty.set_text_silent(digits_only(self.data.get("수량", "")))
                self.price.setText(self.data.get("단가", ""))
                self.total.setText(self.data.get("총액", ""))
                self._apply_unit_button_text()
            finally:
                for widget, old in blocked:
                    widget.blockSignals(old)
            self._recalc_total(commit=False)
        finally:
            self._syncing_data = False

    def _commit(self, key: str, value: str):
        value = (value or "").strip()
        self.data[key] = value
        if self._syncing_data:
            return
        payload = {key: value}
        if key == "거래처":
            payload["거래처_id"] = str(self.data.get("거래처_id", "") or "")
        self.data_changed.emit(self.index, payload)

    def _on_qty_committed(self, value: str):
        self._commit("수량", value)
        self._recalc_total()

    def _on_price_changed(self):
        self._commit("단가", self.price.text())
        self._recalc_total()

    def _recalc_total(self, *, commit: bool = True):
        if self._block_total:
            return
        qty_digits = digits_only(self.qty.text())
        price_digits = digits_only(self.price.text())
        if not qty_digits or not price_digits:
            self._block_total = True
            try:
                self.total.setText("")
            finally:
                self._block_total = False
            if commit:
                self._commit("총액", "")
            return
        try:
            total = int(qty_digits) * int(price_digits)
        except (TypeError, ValueError):
            total = 0
        self._block_total = True
        try:
            self.total.setText(format_commas_from_digits(str(total)))
        finally:
            self._block_total = False
        if commit:
            self._commit("총액", self.total.text())
