from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QStackedLayout, QToolButton, QVBoxLayout, QWidget

from services.work_order_defaults import empty_material_row
from ui.postit.basic_info import BasicInfoPostIt
from ui.postit.common import MAX_POSTIT_CARDS
from ui.postit.layout import (
    FolderTabHeader,
    FooterSpacer,
    POSTIT_BODY_HEIGHT,
    POSTIT_EXTERNAL_ROW_GAP,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_TAB_OVERLAP,
    POSTIT_WRAP_HEIGHT_WITH_FOOTER,
    PostItSectionColumn,
)
from ui.postit.material_card import PostItCard
from ui.theme import THEME, disabled_index_button_style, index_button_style


class _StackHost(QWidget):
    def __init__(self, fixed_height: int, parent=None):
        super().__init__(parent)
        self.setFixedHeight(fixed_height)
        self._stack = QStackedLayout(self)
        self._stack.setContentsMargins(0, 0, 0, 0)
        self._stack.setSpacing(0)

    def add_widget(self, widget: QWidget):
        self._stack.addWidget(widget)

    def set_current_widget(self, widget: QWidget):
        self._stack.setCurrentWidget(widget)


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

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        root.addWidget(self.stack_host, 0)
        root.addWidget(self.footer_host, 0)
        self.setFixedHeight(POSTIT_BODY_HEIGHT + POSTIT_FOOTER_HEIGHT)

        self._rebuild_index_buttons()

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


class PostItColumn(PostItSectionColumn):
    def __init__(self, section_wrap: QWidget, row_widget: QWidget | None = None, parent=None):
        # backward-compatible wrapper for existing call sites
        super().__init__(
            QWidget(),
            QWidget(),
            parent=parent,
            body_height=0,
            footer_widget=None,
            external_row_widget=row_widget or FooterSpacer(parent),
        )
        self.layout().removeWidget(self.section_wrap)
        self.section_wrap.setParent(None)
        self.section_wrap = section_wrap
        self.layout().insertWidget(0, self.section_wrap, 0)
        self.setFixedHeight(POSTIT_WRAP_HEIGHT_WITH_FOOTER + POSTIT_EXTERNAL_ROW_GAP + POSTIT_FOOTER_HEIGHT)


class PartnerTabbedPostIt(PostItSectionColumn):
    TAB_FABRIC = "fabric"
    TAB_TRIM = "trim"

    fabric_deleted = Signal(int)
    trim_deleted = Signal(int)
    fabric_item_changed = Signal(int, dict)
    trim_item_changed = Signal(int, dict)
    fabric_item_added = Signal()
    trim_item_added = Signal()

    def __init__(self, parent=None):
        self._active_tab = self.TAB_FABRIC

        self.tab_header = FolderTabHeader(
            [(self.TAB_FABRIC, "원단"), (self.TAB_TRIM, "부자재")],
            active_key=self.TAB_FABRIC,
            interactive=True,
        )
        self.body_host = _StackHost(POSTIT_BODY_HEIGHT)

        self.fabric = PostItStack(self.TAB_FABRIC)
        self.trim = PostItStack(self.TAB_TRIM)
        self.body_host.add_widget(self.fabric)
        self.body_host.add_widget(self.trim)

        self.footer_spacer = FooterSpacer()

        self.pager_host = _StackHost(POSTIT_FOOTER_HEIGHT)
        self.pager_host.add_widget(self.fabric.footer_widget())
        self.pager_host.add_widget(self.trim.footer_widget())

        super().__init__(
            self.tab_header,
            self.body_host,
            parent=parent,
            body_height=POSTIT_BODY_HEIGHT,
            footer_widget=self.footer_spacer,
            external_row_widget=self.pager_host,
            spacing=POSTIT_TAB_OVERLAP,
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.fabric.item_deleted.connect(self.fabric_deleted.emit)
        self.trim.item_deleted.connect(self.trim_deleted.emit)
        self.fabric.item_changed.connect(self.fabric_item_changed.emit)
        self.trim.item_changed.connect(self.trim_item_changed.emit)
        self.fabric.item_added.connect(self.fabric_item_added.emit)
        self.trim.item_added.connect(self.trim_item_added.emit)

        self.tab_header.button(self.TAB_FABRIC).clicked.connect(lambda: self.set_active_tab(self.TAB_FABRIC))
        self.tab_header.button(self.TAB_TRIM).clicked.connect(lambda: self.set_active_tab(self.TAB_TRIM))
        self.set_active_tab(self.TAB_FABRIC)

    def set_active_tab(self, tab_key: str):
        self._active_tab = self.TAB_TRIM if tab_key == self.TAB_TRIM else self.TAB_FABRIC
        is_fabric = self._active_tab == self.TAB_FABRIC
        self.tab_header.set_active_tab(self._active_tab)
        self.body_host.set_current_widget(self.fabric if is_fabric else self.trim)
        self.pager_host.set_current_widget(self.fabric.footer_widget() if is_fabric else self.trim.footer_widget())

    def set_data(self, fabrics: List[Dict[str, str]], trims: List[Dict[str, str]], force_rebuild: bool = False):
        self.fabric.set_items(fabrics or [], force_rebuild=force_rebuild)
        self.trim.set_items(trims or [], force_rebuild=force_rebuild)


class PostItBar(QWidget):
    fabric_deleted = Signal(int)
    trim_deleted = Signal(int)
    fabric_item_changed = Signal(int, dict)
    trim_item_changed = Signal(int, dict)
    fabric_item_added = Signal()
    trim_item_added = Signal()
    basic_data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(THEME.section_gap)
        lay.setAlignment(Qt.AlignTop)

        self.basic = BasicInfoPostIt(self)
        self.basic.data_changed.connect(self.basic_data_changed.emit)
        self.basic_title = FolderTabHeader("기본정보", self)
        self.basic_footer = FooterSpacer(self)
        self.basic_column = PostItSectionColumn(
            self.basic_title,
            self.basic,
            parent=self,
            body_height=POSTIT_BODY_HEIGHT,
            footer_widget=self.basic_footer,
        )
        self.basic_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.partner = PartnerTabbedPostIt(self)
        self.partner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.partner.fabric_deleted.connect(self.fabric_deleted.emit)
        self.partner.trim_deleted.connect(self.trim_deleted.emit)
        self.partner.fabric_item_changed.connect(self.fabric_item_changed.emit)
        self.partner.trim_item_changed.connect(self.trim_item_changed.emit)
        self.partner.fabric_item_added.connect(self.fabric_item_added.emit)
        self.partner.trim_item_added.connect(self.trim_item_added.emit)

        self.fabric = self.partner.fabric
        self.trim = self.partner.trim

        lay.addWidget(self.basic_column, 1)
        lay.addWidget(self.partner, 2)

    def set_data(
        self,
        header: dict | None = None,
        fabrics: List[Dict[str, str]] | None = None,
        trims: List[Dict[str, str]] | None = None,
        force_rebuild: bool = False,
    ):
        self.basic.set_header_data(header or {})
        self.partner.set_data(fabrics or [], trims or [], force_rebuild=force_rebuild)
