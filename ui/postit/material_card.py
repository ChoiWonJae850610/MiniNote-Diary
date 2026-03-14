from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtWidgets import QMenu, QSizePolicy, QToolButton

from services.field_keys import MaterialKeys
from services.formatters import digits_only, format_commas_from_digits
from services.unit_repository import load_units, unit_label_for_value
from ui.icon_factory import make_partner_link_icon
from ui.postit.metrics import PostItLayout
from ui.messages import Labels, PostItTexts, Tooltips
from ui.partner_ui_utils import PARTNER_PICKER_TYPE_FABRIC, PARTNER_PICKER_TYPE_OTHER, show_partner_picker
from ui.postit.base import _PostItCardBase
from ui.postit.common import FIELD_H, make_down_icon
from ui.postit.editors import _ClickToEditLineEdit, _MoneyLineEdit, _QtyClickToEditLineEdit
from ui.postit.forms import PostItBodyLayout, make_field_label, make_form_row
from ui.postit.layout import POSTIT_CARD_HEIGHT, POSTIT_ROW_ACTION_GAP
from ui.theme import THEME, delete_button_style, input_line_edit_style, menu_style, unit_button_style, tool_button_style
from ui.widget_factory import set_widget_tooltip


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
        self._unit_value = (self.data.get(MaterialKeys.UNIT) or "").strip()
        self._unit_label = unit_label_for_value(self._unit_value, self._units)
        self._suppress_unit_menu_once = False

        root = PostItBodyLayout(self)

        self.btn_delete = QToolButton(self)
        self.btn_delete.setText("×")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setFixedSize(THEME.delete_button_size, THEME.delete_button_size)
        self.btn_delete.setStyleSheet(delete_button_style())
        self.btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.index))

        self.vendor = _ClickToEditLineEdit(self)
        self.item = _ClickToEditLineEdit(self)
        self.btn_vendor_partner = QToolButton(self)
        self.btn_vendor_partner.setIcon(make_partner_link_icon(PostItLayout.PARTNER_LINK_ICON_SIZE))
        self.btn_vendor_partner.setIconSize(QSize(PostItLayout.PARTNER_LINK_ICON_SIZE, PostItLayout.PARTNER_LINK_ICON_SIZE))
        self.btn_vendor_partner.setFixedSize(FIELD_H, FIELD_H)
        self.btn_vendor_partner.setCursor(Qt.PointingHandCursor)
        set_widget_tooltip(self.btn_vendor_partner, Tooltips.PARTNER_MANAGE)
        self.btn_vendor_partner.setStyleSheet(tool_button_style())
        self.btn_vendor_partner.clicked.connect(self._open_vendor_picker)
        self.vendor.set_edit_enabled(False)
        self.vendor.setFocusPolicy(Qt.NoFocus)
        self.vendor.set_text_silent(self.data.get(MaterialKeys.VENDOR, ""))
        self.data[MaterialKeys.VENDOR_ID] = self.data.get(MaterialKeys.VENDOR_ID, "")
        self.item.set_text_silent(self.data.get(MaterialKeys.ITEM, ""))

        vendor_row = make_form_row(make_field_label(Labels.FABRIC_VENDOR if self.kind == "fabric" else Labels.VENDOR, self), (self.vendor, 1), self.btn_vendor_partner)
        vendor_row.setSpacing(POSTIT_ROW_ACTION_GAP)
        root.addLayout(vendor_row)
        root.addLayout(make_form_row(make_field_label(Labels.ITEM, self), (self.item, 1)))

        self.qty = _QtyClickToEditLineEdit(self)
        self.qty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.qty.set_text_silent(self.data.get(MaterialKeys.QTY, ""))

        self.unit_btn = QToolButton(self)
        self.unit_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.unit_btn.setIcon(make_down_icon(PostItLayout.UNIT_ICON_SIZE))
        self.unit_btn.setIconSize(QSize(PostItLayout.UNIT_ICON_SIZE, PostItLayout.UNIT_ICON_SIZE))
        self.unit_btn.setCursor(Qt.PointingHandCursor)
        self.unit_btn.setFixedHeight(FIELD_H)
        self.unit_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.unit_btn.setStyleSheet(unit_button_style())
        self._apply_unit_button_text()
        self._unit_menu = QMenu(self.unit_btn)
        self._unit_menu.setStyleSheet(menu_style())
        self._unit_actions: Dict[str, object] = {}
        self._act_clear_unit = self._unit_menu.addAction(PostItTexts.CLEAR_UNIT)
        self._act_clear_unit.setCheckable(True)
        self._act_clear_unit.triggered.connect(lambda: self._set_unit("", ""))
        if self._units:
            self._unit_menu.addSeparator()
        else:
            hint = self._unit_menu.addAction(PostItTexts.EMPTY_UNIT_LIST)
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
        self.price.setText(self.data.get(MaterialKeys.UNIT_PRICE, ""))
        self.total.set_edit_enabled(False)
        self.total.setFocusPolicy(Qt.NoFocus)
        self.total.setText(self.data.get(MaterialKeys.TOTAL, ""))

        root.addLayout(
            make_form_row(
                make_field_label(Labels.QTY, self),
                (self.qty, 1),
                make_field_label(Labels.UNIT, self),
                (self.unit_btn, 1),
            )
        )
        root.addLayout(make_form_row(make_field_label(Labels.UNIT_PRICE, self), (self.price, 1)))
        root.addLayout(make_form_row(make_field_label(Labels.TOTAL, self), (self.total, 1)))

        self.item.committed.connect(lambda value: self._commit(MaterialKeys.ITEM, value))
        self.qty.committed.connect(self._on_qty_committed)
        self.qty.textChanged.connect(lambda _t: self._recalc_total())
        self.price.textChanged.connect(lambda _t: self._on_price_changed())
        self.total.textChanged.connect(lambda _t: None if self._block_total else self._commit(MaterialKeys.TOTAL, self.total.text()))

        self.setTabOrder(self.btn_vendor_partner, self.item)
        self.setTabOrder(self.item, self.qty)
        self.setTabOrder(self.qty, self.unit_btn)
        self.setTabOrder(self.unit_btn, self.price)
        self.price._pending_prev_widget = self.unit_btn

        self.setMinimumSize(QSize(320, POSTIT_CARD_HEIGHT))
        self.setMaximumHeight(POSTIT_CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _partner_type_for_picker(self) -> str:
        return PARTNER_PICKER_TYPE_FABRIC if self.kind == "fabric" else PARTNER_PICKER_TYPE_OTHER

    def _open_vendor_picker(self):
        def _apply(partner):
            self.vendor.set_text_silent(partner.name)
            self.data[MaterialKeys.VENDOR_ID] = partner.id
            self._commit(MaterialKeys.VENDOR, partner.name)

        show_partner_picker(self.btn_vendor_partner, partner_type=self._partner_type_for_picker(), on_selected=_apply)

    def _on_vendor_committed(self, value: str):
        self.data[MaterialKeys.VENDOR_ID] = ""
        self._commit(MaterialKeys.VENDOR, value)

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
        self._commit(MaterialKeys.UNIT, self._unit_value)

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
        self.btn_delete.move(self.width() - (THEME.delete_button_size + PostItLayout.DELETE_BUTTON_MARGIN_RIGHT), PostItLayout.DELETE_BUTTON_MARGIN_TOP)
        super().resizeEvent(event)

    def update_data(self, data: Dict[str, str]):
        self._syncing_data = True
        try:
            self.data = dict(data or {})
            self._unit_value = (self.data.get(MaterialKeys.UNIT) or "").strip()
            self._unit_label = unit_label_for_value(self._unit_value, self._units)
            widgets = (self.vendor, self.item, self.qty, self.price, self.total)
            blocked = [(widget, widget.blockSignals(True)) for widget in widgets]
            try:
                self.vendor.set_text_silent(self.data.get(MaterialKeys.VENDOR, ""))
                self.data[MaterialKeys.VENDOR_ID] = self.data.get(MaterialKeys.VENDOR_ID, "")
                self.item.set_text_silent(self.data.get(MaterialKeys.ITEM, ""))
                self.qty.set_text_silent(digits_only(self.data.get(MaterialKeys.QTY, "")))
                self.price.setText(self.data.get(MaterialKeys.UNIT_PRICE, ""))
                self.total.setText(self.data.get(MaterialKeys.TOTAL, ""))
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
        if key == MaterialKeys.VENDOR:
            payload[MaterialKeys.VENDOR_ID] = str(self.data.get(MaterialKeys.VENDOR_ID, "") or "")
        self.data_changed.emit(self.index, payload)

    def _on_qty_committed(self, value: str):
        self._commit(MaterialKeys.QTY, value)
        self._recalc_total()

    def _on_price_changed(self):
        self._commit(MaterialKeys.UNIT_PRICE, self.price.text())
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
                self._commit(MaterialKeys.TOTAL, "")
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
            self._commit(MaterialKeys.TOTAL, self.total.text())
