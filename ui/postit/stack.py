from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QStackedLayout, QToolButton, QWidget

from services.work_order_defaults import empty_material_row
from ui.postit.basic_info import BasicInfoPostIt
from ui.postit.common import MAX_POSTIT_CARDS
from ui.postit.layout import (
    FolderTabHeader,
    FooterSpacer,
    POSTIT_BODY_HEIGHT,
    POSTIT_EXTERNAL_ROW_GAP_TIGHT,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_TAB_OVERLAP,
    make_postit_footer_spacer,
    make_static_postit_column,
    PostItSectionColumn,
)
from ui.postit.material_card import PostItCard
from ui.theme import THEME, disabled_index_button_style, index_button_style


class PostItStack(QWidget):
    item_deleted = Signal(int)
    item_changed = Signal(int, dict)
    item_added = Signal()

    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.items: List[Dict[str, str]] = []
        self.cards: List[PostItCard] = []
        self.index_buttons: List[QToolButton] = []
        self.plus_button: QToolButton | None = None
        self.active_index = 0
        self._suppress_next_new_card_menu = False

        self.stack_host = QWidget(self)
        self.stack_host.setFixedHeight(POSTIT_BODY_HEIGHT)
        self.stack = QStackedLayout(self.stack_host)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.footer_host = QWidget(self)
        self.footer_host.setFixedHeight(POSTIT_FOOTER_HEIGHT)
        self.index_row = QHBoxLayout(self.footer_host)
        self.index_row.setContentsMargins(0, 0, 0, 0)
        self.index_row.setSpacing(THEME.top_button_spacing)
        self.index_row.addStretch(1)

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

    @staticmethod
    def _button_style(active: bool) -> str:
        return index_button_style(True) if active else index_button_style(False)

    def _make_index_button(self, text: str) -> QToolButton:
        button = QToolButton(self)
        button.setText(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(THEME.icon_button_size, THEME.icon_button_size)
        button.setFocusPolicy(Qt.NoFocus)
        return button

    def _rebuild_index_buttons(self):
        while self.index_row.count() > 1:
            item = self.index_row.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.index_buttons = []
        for idx in range(len(self.items)):
            button = self._make_index_button(str(idx + 1))
            button.clicked.connect(lambda _=False, i=idx: self.set_active_card(i))
            self.index_buttons.append(button)
            self.index_row.addWidget(button, 0)
        self.plus_button = self._make_index_button("+")
        self.plus_button.clicked.connect(self._add_item)
        self.index_row.addWidget(self.plus_button, 0)
        self._apply_active()

    def _apply_active(self):
        for idx, button in enumerate(self.index_buttons):
            button.setStyleSheet(self._button_style(idx == self.active_index))
        if self.plus_button is not None:
            enabled = len(self.items) < MAX_POSTIT_CARDS
            self.plus_button.setEnabled(enabled)
            self.plus_button.setStyleSheet(index_button_style(False) if enabled else disabled_index_button_style())
        for idx, card in enumerate(self.cards):
            card.set_active(idx == self.active_index)

    def set_active_card(self, idx: int):
        if 0 <= idx < len(self.items):
            self.active_index = idx
            self.stack.setCurrentIndex(idx)
            self._apply_active()

    def _add_item(self):
        if len(self.items) >= MAX_POSTIT_CARDS:
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


class PartnerTabbedPostIt(PostItSectionColumn):
    TAB_FABRIC = "fabric"
    TAB_TRIM = "trim"
    TAB_DYEING = "dyeing"
    TAB_FINISHING = "finishing"
    TAB_OTHER = "other"

    fabric_deleted = Signal(int)
    trim_deleted = Signal(int)
    dyeing_deleted = Signal(int)
    finishing_deleted = Signal(int)
    other_deleted = Signal(int)
    fabric_item_changed = Signal(int, dict)
    trim_item_changed = Signal(int, dict)
    dyeing_item_changed = Signal(int, dict)
    finishing_item_changed = Signal(int, dict)
    other_item_changed = Signal(int, dict)
    fabric_item_added = Signal()
    trim_item_added = Signal()
    dyeing_item_added = Signal()
    finishing_item_added = Signal()
    other_item_added = Signal()

    def __init__(self, parent=None):
        self._active_tab = self.TAB_FABRIC

        self.tab_header = FolderTabHeader(
            [
                (self.TAB_FABRIC, "원단"),
                (self.TAB_TRIM, "부자재"),
                (self.TAB_DYEING, "염색"),
                (self.TAB_FINISHING, "마감"),
                (self.TAB_OTHER, "기타"),
            ],
            active_key=self.TAB_FABRIC,
            interactive=True,
        )
        self.body_host = QWidget()
        self.body_host.setFixedHeight(POSTIT_BODY_HEIGHT)
        self.body_stack = QStackedLayout(self.body_host)
        self.body_stack.setContentsMargins(0, 0, 0, 0)
        self.body_stack.setSpacing(0)

        self.fabric = PostItStack(self.TAB_FABRIC)
        self.trim = PostItStack(self.TAB_TRIM)
        self.dyeing = PostItStack(self.TAB_DYEING)
        self.finishing = PostItStack(self.TAB_FINISHING)
        self.other = PostItStack(self.TAB_OTHER)
        for stack in (self.fabric, self.trim, self.dyeing, self.finishing, self.other):
            self.body_stack.addWidget(stack.body_widget())

        self.footer_spacer = FooterSpacer()

        self.pager_host = QWidget()
        self.pager_host.setFixedHeight(POSTIT_FOOTER_HEIGHT)
        self.pager_stack = QStackedLayout(self.pager_host)
        self.pager_stack.setContentsMargins(0, 0, 0, 0)
        self.pager_stack.setSpacing(0)
        for stack in (self.fabric, self.trim, self.dyeing, self.finishing, self.other):
            self.pager_stack.addWidget(stack.footer_widget())

        super().__init__(
            self.tab_header,
            self.body_host,
            parent=parent,
            body_height=POSTIT_BODY_HEIGHT,
            footer_widget=self.footer_spacer,
            external_row_widget=self.pager_host,
            spacing=POSTIT_TAB_OVERLAP,
            external_row_gap=POSTIT_EXTERNAL_ROW_GAP_TIGHT,
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.fabric.item_deleted.connect(self.fabric_deleted.emit)
        self.trim.item_deleted.connect(self.trim_deleted.emit)
        self.dyeing.item_deleted.connect(self.dyeing_deleted.emit)
        self.finishing.item_deleted.connect(self.finishing_deleted.emit)
        self.other.item_deleted.connect(self.other_deleted.emit)
        self.fabric.item_changed.connect(self.fabric_item_changed.emit)
        self.trim.item_changed.connect(self.trim_item_changed.emit)
        self.dyeing.item_changed.connect(self.dyeing_item_changed.emit)
        self.finishing.item_changed.connect(self.finishing_item_changed.emit)
        self.other.item_changed.connect(self.other_item_changed.emit)
        self.fabric.item_added.connect(self.fabric_item_added.emit)
        self.trim.item_added.connect(self.trim_item_added.emit)
        self.dyeing.item_added.connect(self.dyeing_item_added.emit)
        self.finishing.item_added.connect(self.finishing_item_added.emit)
        self.other.item_added.connect(self.other_item_added.emit)

        for tab_key in self.tab_header.keys():
            button = self.tab_header.button(tab_key)
            if button is not None:
                button.clicked.connect(lambda _=False, key=tab_key: self.set_active_tab(key))
        self.set_active_tab(self.TAB_FABRIC)

    def set_active_tab(self, tab_key: str):
        tab_map = {
            self.TAB_FABRIC: self.fabric,
            self.TAB_TRIM: self.trim,
            self.TAB_DYEING: self.dyeing,
            self.TAB_FINISHING: self.finishing,
            self.TAB_OTHER: self.other,
        }
        self._active_tab = tab_key if tab_key in tab_map else self.TAB_FABRIC
        current = tab_map[self._active_tab]
        self.tab_header.set_active_tab(self._active_tab)
        self.body_stack.setCurrentWidget(current.body_widget())
        self.pager_stack.setCurrentWidget(current.footer_widget())

    def set_data(
        self,
        fabrics: List[Dict[str, str]],
        trims: List[Dict[str, str]],
        dyeings: List[Dict[str, str]] | None = None,
        finishings: List[Dict[str, str]] | None = None,
        others: List[Dict[str, str]] | None = None,
        force_rebuild: bool = False,
    ):
        self.fabric.set_items(fabrics or [], force_rebuild=force_rebuild)
        self.trim.set_items(trims or [], force_rebuild=force_rebuild)
        self.dyeing.set_items(dyeings or [], force_rebuild=force_rebuild)
        self.finishing.set_items(finishings or [], force_rebuild=force_rebuild)
        self.other.set_items(others or [], force_rebuild=force_rebuild)


class PostItBar(QWidget):
    fabric_deleted = Signal(int)
    trim_deleted = Signal(int)
    dyeing_deleted = Signal(int)
    finishing_deleted = Signal(int)
    other_deleted = Signal(int)
    fabric_item_changed = Signal(int, dict)
    trim_item_changed = Signal(int, dict)
    dyeing_item_changed = Signal(int, dict)
    finishing_item_changed = Signal(int, dict)
    other_item_changed = Signal(int, dict)
    fabric_item_added = Signal()
    trim_item_added = Signal()
    dyeing_item_added = Signal()
    finishing_item_added = Signal()
    other_item_added = Signal()
    basic_data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(THEME.section_gap)
        lay.setAlignment(Qt.AlignTop)

        self.basic = BasicInfoPostIt(self)
        self.basic.data_changed.connect(self.basic_data_changed.emit)
        self.basic_footer = make_postit_footer_spacer(self)
        self.basic_column = make_static_postit_column(
            "기본정보",
            self.basic,
            parent=self,
            body_height=POSTIT_BODY_HEIGHT,
            footer_widget=self.basic_footer,
            external_row_gap=POSTIT_EXTERNAL_ROW_GAP_TIGHT,
        )
        self.basic_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.partner = PartnerTabbedPostIt(self)
        self.partner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.partner.fabric_deleted.connect(self.fabric_deleted.emit)
        self.partner.trim_deleted.connect(self.trim_deleted.emit)
        self.partner.dyeing_deleted.connect(self.dyeing_deleted.emit)
        self.partner.finishing_deleted.connect(self.finishing_deleted.emit)
        self.partner.other_deleted.connect(self.other_deleted.emit)
        self.partner.fabric_item_changed.connect(self.fabric_item_changed.emit)
        self.partner.trim_item_changed.connect(self.trim_item_changed.emit)
        self.partner.dyeing_item_changed.connect(self.dyeing_item_changed.emit)
        self.partner.finishing_item_changed.connect(self.finishing_item_changed.emit)
        self.partner.other_item_changed.connect(self.other_item_changed.emit)
        self.partner.fabric_item_added.connect(self.fabric_item_added.emit)
        self.partner.trim_item_added.connect(self.trim_item_added.emit)
        self.partner.dyeing_item_added.connect(self.dyeing_item_added.emit)
        self.partner.finishing_item_added.connect(self.finishing_item_added.emit)
        self.partner.other_item_added.connect(self.other_item_added.emit)

        self.fabric = self.partner.fabric
        self.trim = self.partner.trim
        self.dyeing = self.partner.dyeing
        self.finishing = self.partner.finishing
        self.other = self.partner.other

        lay.addWidget(self.basic_column, 1)
        lay.addWidget(self.partner, 2)

    def set_data(
        self,
        header: dict | None = None,
        fabrics: List[Dict[str, str]] | None = None,
        trims: List[Dict[str, str]] | None = None,
        dyeings: List[Dict[str, str]] | None = None,
        finishings: List[Dict[str, str]] | None = None,
        others: List[Dict[str, str]] | None = None,
        force_rebuild: bool = False,
    ):
        self.basic.set_header_data(header or {})
        self.partner.set_data(
            fabrics or [],
            trims or [],
            dyeings or [],
            finishings or [],
            others or [],
            force_rebuild=force_rebuild,
        )
