from __future__ import annotations

from PySide6.QtWidgets import QStackedLayout, QWidget

from ui.postit.layout_constants import (
    POSTIT_BODY_HEIGHT,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_STANDARD_EXTERNAL_ROW_GAP,
    POSTIT_TAB_OVERLAP,
    POSTIT_ZERO_MARGIN,
    POSTIT_ZERO_SPACING,
)
from ui.postit.layout_containers import FooterSpacer, PostItSectionColumn
from ui.postit.layout_tabs import FolderTabHeader


def make_postit_footer_spacer(parent=None) -> FooterSpacer:
    return FooterSpacer(parent)


def make_postit_stack_host(*, parent=None, height: int = POSTIT_BODY_HEIGHT) -> tuple[QWidget, QStackedLayout]:
    host = QWidget(parent)
    host.setFixedHeight(height)
    stack = QStackedLayout(host)
    stack.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
    stack.setSpacing(POSTIT_ZERO_SPACING)
    return host, stack


def make_postit_pager_host(*, parent=None) -> tuple[QWidget, QStackedLayout]:
    host = QWidget(parent)
    host.setFixedHeight(POSTIT_FOOTER_HEIGHT)
    stack = QStackedLayout(host)
    stack.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
    stack.setSpacing(POSTIT_ZERO_SPACING)
    return host, stack


def make_static_postit_column(
    title: str,
    body_widget: QWidget,
    *,
    parent=None,
    body_height: int = POSTIT_BODY_HEIGHT,
    footer_widget: QWidget | None = None,
    external_row_widget: QWidget | None = None,
    spacing: int = POSTIT_TAB_OVERLAP,
    external_row_gap: int = POSTIT_STANDARD_EXTERNAL_ROW_GAP,
) -> PostItSectionColumn:
    resolved_footer = footer_widget if footer_widget is not None else make_postit_footer_spacer(parent)
    return PostItSectionColumn(
        FolderTabHeader(title, parent),
        body_widget,
        parent=parent,
        body_height=body_height,
        footer_widget=resolved_footer,
        external_row_widget=external_row_widget,
        spacing=spacing,
        external_row_gap=external_row_gap,
    )


__all__ = [
    "make_postit_footer_spacer",
    "make_postit_pager_host",
    "make_postit_stack_host",
    "make_static_postit_column",
]
