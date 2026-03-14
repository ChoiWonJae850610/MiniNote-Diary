from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from ui.theme import THEME
from ui.widget_factory import make_hint_label, make_nav_button, make_page_title_label, make_panel_frame, make_panel_title_label


@dataclass
class PageHeaderRefs:
    row: QHBoxLayout
    back_button: QWidget
    title_layout: QVBoxLayout


def make_standard_page_layout(page: QWidget) -> QVBoxLayout:
    layout = QVBoxLayout(page)
    layout.setContentsMargins(
        THEME.page_padding_x,
        THEME.page_header_top_margin,
        THEME.page_padding_x,
        THEME.page_padding_y,
    )
    layout.setSpacing(THEME.section_gap)
    return layout


def make_standard_page_header(
    page: QWidget,
    *,
    title_text: str,
    subtitle_text: str,
    subtitle_object_name: str | None = None,
    title_object_name: str | None = None,
) -> PageHeaderRefs:
    row = QHBoxLayout()
    row.setSpacing(THEME.top_button_spacing)

    btn_back = make_nav_button(parent=page)
    title_col = QVBoxLayout()
    title_col.setSpacing(THEME.title_stack_spacing)

    title = make_page_title_label(title_text, page)
    if title_object_name:
        title.setObjectName(title_object_name)

    subtitle = make_hint_label(subtitle_text, page)
    if subtitle_object_name:
        subtitle.setObjectName(subtitle_object_name)

    title_col.addWidget(title)
    title_col.addWidget(subtitle)

    row.addWidget(btn_back, 0, Qt.AlignTop)
    row.addLayout(title_col, 1)

    return PageHeaderRefs(row=row, back_button=btn_back, title_layout=title_col)


def make_titled_panel(
    parent: QWidget,
    *,
    title_text: str,
    hint_text: str = '',
    compact: bool = False,
    title_object_name: str | None = None,
    hint_object_name: str | None = None,
) -> tuple[QFrame, QVBoxLayout]:
    panel = make_panel_frame(parent, compact=compact)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(
        THEME.page_section_padding,
        THEME.page_section_padding,
        THEME.page_section_padding,
        THEME.page_section_padding,
    )
    layout.setSpacing(THEME.row_spacing)

    title = make_panel_title_label(title_text, panel)
    if title_object_name:
        title.setObjectName(title_object_name)
    layout.addWidget(title)

    if hint_text:
        hint = make_hint_label(hint_text, panel)
        if hint_object_name:
            hint.setObjectName(hint_object_name)
        layout.addWidget(hint)

    return panel, layout
