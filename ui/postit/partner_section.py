from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from ui.postit.basic_info import BasicInfoPostIt
from ui.postit.layout import (
    FolderTabHeader,
    FooterSpacer,
    POSTIT_BODY_HEIGHT,
    POSTIT_EXTERNAL_ROW_GAP_TIGHT,
    POSTIT_TAB_OVERLAP,
    make_postit_footer_spacer,
    make_postit_pager_host,
    make_postit_stack_host,
    make_static_postit_column,
    PostItSectionColumn,
)
from ui.messages import SectionTitles
from ui.postit.stack_core import PostItStack
from ui.theme import THEME


class PartnerTabbedPostIt(PostItSectionColumn):
    TAB_FABRIC = 'fabric'
    TAB_TRIM = 'trim'
    TAB_DYEING = 'dyeing'
    TAB_FINISHING = 'finishing'
    TAB_OTHER = 'other'

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
                (self.TAB_FABRIC, SectionTitles.FABRIC),
                (self.TAB_TRIM, SectionTitles.TRIM),
                (self.TAB_DYEING, SectionTitles.DYEING),
                (self.TAB_FINISHING, SectionTitles.FINISHING),
                (self.TAB_OTHER, SectionTitles.OTHER),
            ],
            active_key=self.TAB_FABRIC,
            interactive=True,
        )

        self.body_host, self.body_stack = make_postit_stack_host(height=POSTIT_BODY_HEIGHT)
        self.fabric = PostItStack(self.TAB_FABRIC)
        self.trim = PostItStack(self.TAB_TRIM)
        self.dyeing = PostItStack(self.TAB_DYEING)
        self.finishing = PostItStack(self.TAB_FINISHING)
        self.other = PostItStack(self.TAB_OTHER)
        self._tab_stacks = {
            self.TAB_FABRIC: self.fabric,
            self.TAB_TRIM: self.trim,
            self.TAB_DYEING: self.dyeing,
            self.TAB_FINISHING: self.finishing,
            self.TAB_OTHER: self.other,
        }
        for stack in self._tab_stacks.values():
            self.body_stack.addWidget(stack.body_widget())

        self.footer_spacer = FooterSpacer()
        self.pager_host, self.pager_stack = make_postit_pager_host()
        for stack in self._tab_stacks.values():
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
        self._active_tab = tab_key if tab_key in self._tab_stacks else self.TAB_FABRIC
        current = self._tab_stacks[self._active_tab]
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
            SectionTitles.BASIC_INFO,
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

