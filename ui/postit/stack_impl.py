from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSizePolicy, QWidget

from services.work_order_defaults import empty_material_row
from ui.postit.layout import (
    POSTIT_BODY_HEIGHT,
    POSTIT_FOOTER_HEIGHT,
    make_postit_stack_host,
)
from ui.postit.material_card import PostItCard
from ui.postit.stack_index_controls import PostItIndexControls


class PostItStack(QWidget):
    item_deleted = Signal(int)
    item_changed = Signal(int, dict)
    item_added = Signal()

    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.items: List[Dict[str, str]] = []
        self.cards: List[PostItCard] = []
        self.active_index = 0
        self._suppress_next_new_card_menu = False

        self.stack_host, self.stack = make_postit_stack_host(parent=self, height=POSTIT_BODY_HEIGHT)

        self.footer_host = QWidget(self)
        self.footer_host.setFixedHeight(POSTIT_FOOTER_HEIGHT)
        self.index_controls = PostItIndexControls(self, self.footer_host)
        self.index_buttons = self.index_controls.index_buttons
        self.plus_button = self.index_controls.plus_button

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(POSTIT_BODY_HEIGHT + POSTIT_FOOTER_HEIGHT)

        self._rebuild_index_buttons()

    def body_widget(self) -> QWidget:
        return self.stack_host

    def footer_widget(self) -> QWidget:
        return self.footer_host

    def set_items(self, items: List[Dict[str, str]], force_rebuild: bool = False):
        items = list(items or []) or [empty_material_row()]
        if force_rebuild or not self.cards:
            self.items = items
            if self.active_index >= len(self.items):
                self.active_index = max(0, len(self.items) - 1)
            self._rebuild()
            return
        if len(items) == len(self.items) == len(self.cards):
            self.items = items
            for idx, item in enumerate(self.items):
                self.cards[idx].index = idx
                self.cards[idx].update_data(item)
            if self.active_index >= len(self.items):
                self.active_index = max(0, len(self.items) - 1)
            self.stack.setCurrentIndex(self.active_index)
            self._refresh_delete_buttons()
            self._apply_active()
            self._rebuild_index_buttons()
            return
        self.items = items
        if self.active_index >= len(self.items):
            self.active_index = max(0, len(self.items) - 1)
        self._rebuild()

    def _create_card(self, idx: int, item: Dict[str, str]) -> PostItCard:
        card = PostItCard(self.kind, idx, item, parent=self)
        card.delete_clicked.connect(self.item_deleted.emit)
        card.selected.connect(self.set_active_card)
        card.data_changed.connect(self.item_changed.emit)
        return card

    def _append_card(self, item: Dict[str, str], idx: int):
        card = self._create_card(idx, item)
        if self._suppress_next_new_card_menu:
            card.suppress_unit_menu_once()
            self._suppress_next_new_card_menu = False
        self.stack.addWidget(card)
        self.cards.append(card)

    def _refresh_delete_buttons(self):
        single = len(self.cards) == 1
        for card in self.cards:
            card.btn_delete.setVisible(not single)

    def _rebuild(self):
        while self.stack.count():
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
        self.cards = []
        for idx, item in enumerate(self.items):
            self._append_card(item, idx)
        self.stack.setCurrentIndex(self.active_index)
        self._refresh_delete_buttons()
        self._rebuild_index_buttons()
        self._apply_active()

    def _rebuild_index_buttons(self):
        self.index_buttons, self.plus_button = self.index_controls.rebuild(
            item_count=len(self.items),
            active_index=self.active_index,
            on_select=self.set_active_card,
            on_add=self._add_item,
        )

    def _apply_active(self):
        self.index_controls.apply_active(active_index=self.active_index, item_count=len(self.items))
        for idx, card in enumerate(self.cards):
            card.set_active(idx == self.active_index)

    def set_active_card(self, idx: int):
        if 0 <= idx < len(self.items):
            self.active_index = idx
            self.stack.setCurrentIndex(idx)
            self._apply_active()

    def _add_item(self):
        if self.plus_button is not None and not self.plus_button.isEnabled():
            return
        self._suppress_next_new_card_menu = True
        self.items.append(empty_material_row())
        idx = len(self.items) - 1
        self._append_card(self.items[idx], idx)
        self.active_index = idx
        self.stack.setCurrentIndex(idx)
        self._refresh_delete_buttons()
        self._rebuild_index_buttons()
        self._apply_active()
        self.item_added.emit()


__all__ = ["PostItStack"]
