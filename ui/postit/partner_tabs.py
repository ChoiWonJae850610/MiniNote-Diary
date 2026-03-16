from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSizePolicy

from ui.postit.layout import FolderTabHeader, FooterSpacer, POSTIT_BODY_HEIGHT, POSTIT_EXTERNAL_ROW_GAP_TIGHT, POSTIT_TAB_OVERLAP, PostItSectionColumn, make_postit_pager_host, make_postit_stack_host
from ui.postit.partner_tab_setup import build_partner_tab_defs, connect_partner_stack_signals
from ui.postit.stack_core import PostItStack


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
        self.tab_header = FolderTabHeader(build_partner_tab_defs(self), active_key=self.TAB_FABRIC, interactive=True)
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

        connect_partner_stack_signals(self)
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

    def set_data(self, fabrics: List[Dict[str, str]], trims: List[Dict[str, str]], dyeings: List[Dict[str, str]] | None = None, finishings: List[Dict[str, str]] | None = None, others: List[Dict[str, str]] | None = None, force_rebuild: bool = False):
        self.fabric.set_items(fabrics or [], force_rebuild=force_rebuild)
        self.trim.set_items(trims or [], force_rebuild=force_rebuild)
        self.dyeing.set_items(dyeings or [], force_rebuild=force_rebuild)
        self.finishing.set_items(finishings or [], force_rebuild=force_rebuild)
        self.other.set_items(others or [], force_rebuild=force_rebuild)


__all__ = ['PartnerTabbedPostIt']
