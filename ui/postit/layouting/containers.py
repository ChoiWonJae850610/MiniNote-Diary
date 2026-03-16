from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from ui.postit.layouting.constants import (
    POSTIT_EXTERNAL_ROW_GAP,
    POSTIT_FOOTER_GAP,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_TAB_OVERLAP,
    POSTIT_ZERO_MARGIN,
    POSTIT_ZERO_STRETCH,
)
from ui.postit.layouting.helpers import postit_section_height


@dataclass(frozen=True)
class SectionLayoutSpec:
    tab_overlap: int = POSTIT_TAB_OVERLAP
    footer_gap: int = POSTIT_FOOTER_GAP
    external_row_gap: int = POSTIT_EXTERNAL_ROW_GAP
    footer_height: int = POSTIT_FOOTER_HEIGHT


DEFAULT_SECTION_LAYOUT = SectionLayoutSpec()


class SectionContainer(QWidget):
    def __init__(
        self,
        header_widget: QWidget,
        body_widget: QWidget,
        *,
        parent=None,
        layout_spec: SectionLayoutSpec = DEFAULT_SECTION_LAYOUT,
        header_alignment=Qt.AlignLeft,
        footer_widget: QWidget | None = None,
        body_height: int | None = None,
    ):
        super().__init__(parent)
        self.layout_spec = layout_spec
        root = QVBoxLayout(self)
        root.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
        root.setSpacing(layout_spec.tab_overlap)
        if header_alignment is None:
            root.addWidget(header_widget)
        else:
            root.addWidget(header_widget, POSTIT_ZERO_STRETCH, header_alignment)
        root.addWidget(body_widget, POSTIT_ZERO_STRETCH)
        if footer_widget is not None:
            root.addSpacing(layout_spec.footer_gap)
            root.addWidget(footer_widget, POSTIT_ZERO_STRETCH)

        height = body_height if body_height is not None else body_widget.sizeHint().height()
        if height > 0:
            self.setFixedHeight(postit_section_height(body_height=height, has_footer=footer_widget is not None))


class FooterSpacer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(POSTIT_FOOTER_HEIGHT)


class PostItSectionColumn(QWidget):
    def __init__(
        self,
        header_widget: QWidget,
        body_widget: QWidget,
        *,
        parent=None,
        body_height: int | None = None,
        footer_widget: QWidget | None = None,
        external_row_widget: QWidget | None = None,
        layout_spec: SectionLayoutSpec = DEFAULT_SECTION_LAYOUT,
    ):
        super().__init__(parent)
        self.section_wrap = SectionContainer(
            header_widget,
            body_widget,
            parent=self,
            layout_spec=layout_spec,
            header_alignment=None,
            footer_widget=footer_widget,
            body_height=body_height,
        )
        self.section_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.external_row_widget = external_row_widget or FooterSpacer(self)
        self.external_row_widget.setParent(self)
        self.external_row_widget.setFixedHeight(layout_spec.footer_height)

        root = QVBoxLayout(self)
        root.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
        root.setSpacing(layout_spec.external_row_gap)
        root.addWidget(self.section_wrap, POSTIT_ZERO_STRETCH)
        root.addWidget(self.external_row_widget, POSTIT_ZERO_STRETCH)

        has_footer = footer_widget is not None
        section_height = postit_section_height(body_height=body_height or body_widget.sizeHint().height(), has_footer=has_footer)
        self.setFixedHeight(section_height + layout_spec.external_row_gap + layout_spec.footer_height)


__all__ = [
    "DEFAULT_SECTION_LAYOUT",
    "FooterSpacer",
    "PostItSectionColumn",
    "SectionContainer",
    "SectionLayoutSpec",
]
