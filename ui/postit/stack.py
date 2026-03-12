
from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QStackedLayout, QToolButton, QVBoxLayout, QWidget

from services.work_order_defaults import empty_material_row
from ui.postit.basic_info import BasicInfoPostIt
from ui.postit.common import MAX_POSTIT_CARDS
from ui.postit.layout import (
    FolderTabHeader,
    SectionContainer,
    folder_tab_style,
    POSTIT_TAB_INSET_LEFT,
    POSTIT_TAB_OVERLAP,
    POSTIT_BODY_HEIGHT,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_WRAP_HEIGHT,
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

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(THEME.top_button_spacing)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        root.addWidget(self.stack_host, 0)
        root.addWidget(self.footer_host, 0)
        self.setFixedHeight(POSTIT_BODY_HEIGHT + THEME.top_button_spacing + POSTIT_FOOTER_HEIGHT)

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
                widget.setParent(None)
                widget.deleteLater()
        self.index_buttons = []
        for idx in range(len(self.items)):
            button = self._make_index_button(str(idx + 1))
            button.clicked.connect(lambda _=False, i=idx: self.set_active_card(i))
            self.index_buttons.append(button)
            self.index_row.addWidget(button)
        self.plus_button = self._make_index_button("+")
        self.plus_button.clicked.connect(self._on_add_clicked)
        self.index_row.addWidget(self.plus_button)
        self._update_index_button_states()

    def _update_index_button_states(self):
        for idx, button in enumerate(self.index_buttons):
            button.setStyleSheet(self._button_style(idx == self.active_index))
        if self.plus_button is not None:
            enabled = len(self.items) < MAX_POSTIT_CARDS
            self.plus_button.setEnabled(enabled)
            self.plus_button.setStyleSheet(self._button_style(False) if enabled else disabled_index_button_style())

    def _on_add_clicked(self):
        if len(self.items) < MAX_POSTIT_CARDS:
            self._suppress_next_new_card_menu = True
            self.item_added.emit()

    def set_active_card(self, idx: int):
        if 0 <= idx < len(self.items):
            self.active_index = idx
            self.stack.setCurrentIndex(idx)
            self._apply_active()
            self._update_index_button_states()

    def _apply_active(self):
        for idx, card in enumerate(self.cards):
            card.set_active(idx == self.active_index)
        self._update_index_button_states()


class PartnerTabbedPostIt(QWidget):
    fabric_deleted = Signal(int)
    trim_deleted = Signal(int)
    fabric_item_changed = Signal(int, dict)
    trim_item_changed = Signal(int, dict)
    fabric_item_added = Signal()
    trim_item_added = Signal()

    TAB_FABRIC = "fabric"
    TAB_TRIM = "trim"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_tab = self.TAB_FABRIC

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(POSTIT_WRAP_HEIGHT + THEME.top_button_spacing + POSTIT_FOOTER_HEIGHT)

        self.tab_row_wrap = QWidget(self)
        self.tab_row_layout = QHBoxLayout(self.tab_row_wrap)
        self.tab_row_layout.setContentsMargins(POSTIT_TAB_INSET_LEFT, 0, 0, 0)
        self.tab_row_layout.setSpacing(0)

        self.btn_fabric = self._make_tab_button("원단", self.TAB_FABRIC)
        self.btn_trim = self._make_tab_button("부자재", self.TAB_TRIM)
        self.tab_row_layout.addWidget(self.btn_fabric, 0)
        self.tab_row_layout.addWidget(self.btn_trim, 0)
        self.tab_row_layout.addStretch(1)
        root.addWidget(self.tab_row_wrap, 0)

        self.body_host = QWidget(self)
        self.body_host.setFixedHeight(POSTIT_BODY_HEIGHT)
        self.body_stack = QStackedLayout(self.body_host)
        self.body_stack.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.body_host, 0)

        self.fabric = PostItStack(self.TAB_FABRIC, self)
        self.trim = PostItStack(self.TAB_TRIM, self)
        self.body_stack.addWidget(self.fabric)
        self.body_stack.addWidget(self.trim)

        self.footer_stack = QStackedLayout()
        self.footer_stack.addWidget(self.fabric.footer_widget())
        self.footer_stack.addWidget(self.trim.footer_widget())

        footer_host = QWidget(self)
        footer_host.setFixedHeight(POSTIT_FOOTER_HEIGHT)
        footer_host.setLayout(self.footer_stack)
        root.addSpacing(THEME.top_button_spacing)
        root.addWidget(footer_host, 0)

        self.fabric.item_deleted.connect(self.fabric_deleted.emit)
        self.trim.item_deleted.connect(self.trim_deleted.emit)
        self.fabric.item_changed.connect(self.fabric_item_changed.emit)
        self.trim.item_changed.connect(self.trim_item_changed.emit)
        self.fabric.item_added.connect(self.fabric_item_added.emit)
        self.trim.item_added.connect(self.trim_item_added.emit)

        self.btn_fabric.clicked.connect(lambda: self.set_active_tab(self.TAB_FABRIC))
        self.btn_trim.clicked.connect(lambda: self.set_active_tab(self.TAB_TRIM))
        self.set_active_tab(self.TAB_FABRIC)

    def _make_tab_button(self, text: str, tab_key: str) -> QToolButton:
        button = QToolButton(self)
        button.setText(text)
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedHeight(THEME.dialog_button_height)
        button.setMinimumWidth(84)
        button.setFocusPolicy(Qt.NoFocus)
        button.setProperty("partnerTabKey", tab_key)
        return button

    def _tab_button_style(self, active: bool) -> str:
        base = folder_tab_style(active=active).replace("QLabel", "QToolButton")
        if active:
            return base
        return base + f"QToolButton:hover{{background:{THEME.color_surface_alt};color:{THEME.color_text};}}"

    def set_active_tab(self, tab_key: str):
        self._active_tab = self.TAB_TRIM if tab_key == self.TAB_TRIM else self.TAB_FABRIC
        is_fabric = self._active_tab == self.TAB_FABRIC
        self.btn_fabric.setChecked(is_fabric)
        self.btn_trim.setChecked(not is_fabric)
        self.btn_fabric.setStyleSheet(self._tab_button_style(is_fabric))
        self.btn_trim.setStyleSheet(self._tab_button_style(not is_fabric))
        self.body_stack.setCurrentWidget(self.fabric if is_fabric else self.trim)
        self.footer_stack.setCurrentWidget(self.fabric.footer_widget() if is_fabric else self.trim.footer_widget())

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
        self.basic_wrap = SectionContainer(self.basic_title, self.basic, parent=self, spacing=POSTIT_TAB_OVERLAP, header_alignment=None)
        self.basic_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.basic_wrap.setFixedHeight(POSTIT_WRAP_HEIGHT)

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

        lay.addWidget(self.basic_wrap, 1)
        lay.addWidget(self.partner, 2)

    def set_data(self, header: Dict[str, str], fabrics: List[Dict[str, str]], trims: List[Dict[str, str]], force_rebuild: bool = False):
        self.basic.set_header_data(header or {})
        self.partner.set_data(fabrics or [], trims or [], force_rebuild=force_rebuild)
