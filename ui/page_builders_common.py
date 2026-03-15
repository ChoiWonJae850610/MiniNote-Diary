from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from ui.layout_metrics import OrderPageLayout
from ui.dialog_layout_utils import make_dialog_form_layout, make_dialog_inline_row, make_dialog_root_layout
from ui.theme import THEME
from ui.widget_factory import make_hint_label, make_nav_button, make_page_title_label, make_panel_frame, make_panel_title_label, make_field_label


@dataclass
class PageHeaderRefs:
    row: QHBoxLayout
    back_button: QWidget
    title_layout: QVBoxLayout


@dataclass
class ScrollPanelRefs:
    scroll_area: QScrollArea
    wrap: QWidget
    layout: QVBoxLayout


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



def make_scroll_panel(parent: QWidget) -> ScrollPanelRefs:
    scroll = QScrollArea(parent)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    wrap = QWidget()
    scroll.setWidget(wrap)

    layout = QVBoxLayout(wrap)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(THEME.section_gap)
    return ScrollPanelRefs(scroll_area=scroll, wrap=wrap, layout=layout)



def make_image_shell(parent: QWidget, child: QWidget, *, margin: int = OrderPageLayout.IMAGE_SHELL_MARGIN) -> QFrame:
    shell = QFrame(parent)
    shell.setObjectName('imageShell')
    layout = QVBoxLayout(shell)
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.addWidget(child)
    return shell



def make_form_grid(*, parent: QWidget | None = None) -> QGridLayout:
    grid = QGridLayout(parent)
    grid.setHorizontalSpacing(OrderPageLayout.DETAIL_GRID_HORIZONTAL_SPACING)
    grid.setVerticalSpacing(OrderPageLayout.DETAIL_GRID_VERTICAL_SPACING)
    return grid



def add_form_row(grid: QGridLayout, row: int, label_text: str, field: QWidget, *, align_top: bool = False, label_parent: QWidget | None = None) -> None:
    grid.addWidget(make_field_label(label_text, label_parent), row, 0, Qt.AlignTop if align_top else Qt.Alignment())
    if align_top:
        grid.addWidget(field, row, 1, Qt.AlignTop)
    else:
        grid.addWidget(field, row, 1)



def make_right_aligned_button_row(*buttons: QWidget) -> QHBoxLayout:
    row = QHBoxLayout()
    row.addStretch(1)
    for button in buttons:
        row.addWidget(button)
    return row



