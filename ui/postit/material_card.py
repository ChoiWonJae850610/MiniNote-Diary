from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtWidgets import QSizePolicy

from services.field_keys import MaterialKeys
from services.unit_repository import unit_label_for_value
from ui.postit.layout import PostItLayout
from ui.messages import Labels
from ui.postit.base import _PostItCardBase
from ui.postit.common import FIELD_H, make_down_icon
from ui.postit.editors import _ClickToEditLineEdit, _MoneyLineEdit, _QtyClickToEditLineEdit
from ui.postit.forms import PostItBodyLayout, make_field_label, make_form_row
from ui.postit.layout import POSTIT_CARD_HEIGHT, POSTIT_DELETE_BUTTON_MARGIN_RIGHT, POSTIT_DELETE_BUTTON_MARGIN_TOP, POSTIT_MATERIAL_CARD_MIN_WIDTH
from ui.postit.material_card_logic import (
    commit_material_value,
    on_price_changed,
    on_qty_committed,
    recalc_material_total,
    set_unit,
    sync_unit_menu_checks,
    update_material_card_data,
)
from ui.postit.material_card_sections import (
    build_amount_rows,
    build_vendor_rows,
    configure_delete_button,
    configure_material_tab_order,
    connect_material_signals,
    open_vendor_picker,
    picker_partner_type,
)
from ui.theme import THEME


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
        self._suppress_unit_menu_once = False

        root = PostItBodyLayout(self)
        configure_delete_button(self)
        build_vendor_rows(self, root)
        build_amount_rows(self, root)
        connect_material_signals(self)
        configure_material_tab_order(self)

        self.setMinimumSize(QSize(POSTIT_MATERIAL_CARD_MIN_WIDTH, POSTIT_CARD_HEIGHT))
        self.setMaximumHeight(POSTIT_CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _partner_type_for_picker(self) -> str:
        return picker_partner_type(self.kind)

    def _open_vendor_picker(self):
        open_vendor_picker(self)

    def _on_vendor_committed(self, value: str):
        self.data[MaterialKeys.VENDOR_ID] = ""
        self._commit(MaterialKeys.VENDOR, value)

    def _apply_unit_button_text(self):
        self.unit_btn.setText((self._unit_value or "").strip())

    def _sync_unit_menu_checks(self):
        sync_unit_menu_checks(self)

    def _set_unit(self, unit: str, label: str):
        set_unit(self, unit, label)

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
        self.btn_delete.move(self.width() - (THEME.delete_button_size + POSTIT_DELETE_BUTTON_MARGIN_RIGHT), POSTIT_DELETE_BUTTON_MARGIN_TOP)
        super().resizeEvent(event)

    def update_data(self, data: Dict[str, str]):
        update_material_card_data(self, data)

    def _commit(self, key: str, value: str):
        commit_material_value(self, key, value)

    def _on_qty_committed(self, value: str):
        on_qty_committed(self, value)

    def _on_price_changed(self):
        on_price_changed(self)

    def _recalc_total(self, *, commit: bool = True):
        recalc_material_total(self, commit=commit)
