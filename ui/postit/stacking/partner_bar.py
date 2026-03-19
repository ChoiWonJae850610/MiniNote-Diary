from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from ui.messages import SectionTitles
from ui.postit.basic_info import BasicInfoPostIt
from ui.postit.layout import (
    POSTIT_BODY_HEIGHT,
    POSTIT_EXTERNAL_ROW_GAP_TIGHT,
    POSTIT_PARTNER_BAR_BASIC_STRETCH,
    POSTIT_PARTNER_BAR_MATERIAL_STRETCH,
    POSTIT_ZERO_MARGIN,
    make_postit_footer_spacer,
    make_static_postit_column,
)
from ui.postit.stacking.partner_tabs import PartnerTabbedPostIt
from ui.theme import THEME


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
        lay.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
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
        self.basic_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.partner = PartnerTabbedPostIt(self)
        self.partner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._connect_partner_signals()
        self._expose_partner_stacks()

        lay.addWidget(self.basic_column, POSTIT_PARTNER_BAR_BASIC_STRETCH)
        lay.addWidget(self.partner, POSTIT_PARTNER_BAR_MATERIAL_STRETCH)

    def _connect_partner_signals(self) -> None:
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

    def _expose_partner_stacks(self) -> None:
        self.fabric = self.partner.fabric
        self.trim = self.partner.trim
        self.dyeing = self.partner.dyeing
        self.finishing = self.partner.finishing
        self.other = self.partner.other

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


__all__ = ["PostItBar"]
