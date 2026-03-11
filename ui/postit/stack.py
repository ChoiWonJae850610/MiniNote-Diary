from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QStackedLayout, QToolButton, QVBoxLayout, QWidget

from services.work_order_defaults import empty_material_row
from ui.postit.basic_info import BasicInfoPostIt
from ui.postit.common import MAX_POSTIT_CARDS
from ui.postit.layout import FolderTabHeader, SectionContainer
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

        self.index_row_wrap = QWidget(self)
        self.index_row_wrap.setFixedHeight(THEME.section_badge_height)
        self.index_row = QHBoxLayout(self.index_row_wrap)
        self.index_row.setContentsMargins(0, 0, 0, 0)
        self.index_row.setSpacing(THEME.top_button_spacing)

        self.stack_host = QWidget(self)
        self.stack = QStackedLayout(self.stack_host)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.section = SectionContainer(self.index_row_wrap, self.stack_host, parent=self, spacing=THEME.top_button_spacing, header_alignment=None)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.section)

        self._rebuild_index_buttons()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(THEME.postit_bar_max_height)

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
            for idx, (card, item) in enumerate(zip(self.cards, self.items)):
                self.cards[idx].index = idx
                self.cards[idx].update_data(self.items[idx])
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

    @staticmethod
    def _find_single_removed_index(old_items, new_items):
        if len(old_items) != len(new_items) + 1:
            return None
        for idx in range(len(old_items)):
            if old_items[:idx] + old_items[idx + 1:] == new_items:
                return idx
        return None

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
        self._apply_active()

    def _remove_card_at(self, idx: int):
        if 0 <= idx < len(self.cards):
            card = self.cards.pop(idx)
            self.stack.removeWidget(card)
            card.setParent(None)
            card.deleteLater()

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
        while self.index_row.count():
            item = self.index_row.takeAt(0)
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
        self.plus_button = self._make_index_button('+')
        self.plus_button.clicked.connect(self._on_add_clicked)
        self.index_row.addWidget(self.plus_button)
        self.index_row.addStretch(1)
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

    TAB_FABRIC = 'fabric'
    TAB_TRIM = 'trim'

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_tab = self.TAB_FABRIC

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.tab_row_wrap = QWidget(self)
        self.tab_row_layout = QHBoxLayout(self.tab_row_wrap)
        self.tab_row_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_row_layout.setSpacing(0)

        self.btn_fabric = self._make_tab_button('원단', self.TAB_FABRIC)
        self.btn_trim = self._make_tab_button('거래처', self.TAB_TRIM)

        self.tab_row_layout.addWidget(self.btn_fabric, 0)
        self.tab_row_layout.addWidget(self.btn_trim, 0)
        self.tab_row_layout.addStretch(1)

        root.addWidget(self.tab_row_wrap, 0)

        self.body_host = QWidget(self)
        self.body_stack = QStackedLayout(self.body_host)
        self.body_stack.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.body_host, 1)

        self.fabric = PostItStack(self.TAB_FABRIC, self)
        self.trim = PostItStack(self.TAB_TRIM, self)
        self.body_stack.addWidget(self.fabric)
        self.body_stack.addWidget(self.trim)

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
        button.setProperty('partnerTabKey', tab_key)
        return button

    def _tab_button_style(self, active: bool) -> str:
        t = THEME
        common = (
            'QToolButton{{'
            f'padding:0 16px;'
            f'border:1px solid {t.color_border};'
            f'font-weight:700;'
            f'min-height:{t.dialog_button_height}px;'
            f'max-height:{t.dialog_button_height}px;'
            f'border-top-left-radius:{t.control_radius + 5}px;'
            f'border-top-right-radius:{t.control_radius + 5}px;'
            'border-bottom-left-radius:0px;'
            'border-bottom-right-radius:0px;'
            'margin-right:2px;'
        )
        if active:
            return (
                common
                + f'background:{t.color_surface};color:{t.color_text};border-bottom:none;'
                + '}}'
            )
        return (
            common
            + f'background:{t.color_surface_muted};color:{t.color_text_soft};'
            + f'border-bottom:1px solid {t.color_border};'
            + '}}'
            + f'QToolButton:hover{{background:{t.color_surface_alt};color:{t.color_text};}}'
        )

    def set_active_tab(self, tab_key: str):
        self._active_tab = self.TAB_TRIM if tab_key == self.TAB_TRIM else self.TAB_FABRIC
        is_fabric = self._active_tab == self.TAB_FABRIC
        self.btn_fabric.setChecked(is_fabric)
        self.btn_trim.setChecked(not is_fabric)
        self.btn_fabric.setStyleSheet(self._tab_button_style(is_fabric))
        self.btn_trim.setStyleSheet(self._tab_button_style(not is_fabric))
        self.body_stack.setCurrentWidget(self.fabric if is_fabric else self.trim)

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

        self.basic = BasicInfoPostIt(self)
        self.basic.data_changed.connect(self.basic_data_changed.emit)
        self.basic_title = FolderTabHeader('기본정보', self)
        self.basic_wrap = SectionContainer(self.basic_title, self.basic, parent=self, spacing=0, header_alignment=None)

        self.partner = PartnerTabbedPostIt(self)

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
