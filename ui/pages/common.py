from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from ui.layout_metrics import OrderPageLayout
from ui.theme import THEME
from ui.widget_factory import (
    make_field_label,
    make_hint_label,
    make_nav_button,
    make_page_title_label,
    make_panel_frame,
    make_panel_title_label,
)


@dataclass(frozen=True)
class PageHeaderRefs:
    row: QHBoxLayout
    back_button: QWidget
    title_layout: QVBoxLayout
    title_label: QLabel
    subtitle_label: QLabel


@dataclass(frozen=True)
class PageTextHeaderRefs:
    layout: QVBoxLayout
    title_label: QLabel
    subtitle_label: QLabel


@dataclass(frozen=True)
class ScrollPanelRefs:
    scroll_area: QScrollArea
    wrap: QWidget
    layout: QVBoxLayout


@dataclass(frozen=True)
class LabeledFieldRow:
    label_text: str
    field: QWidget
    align_top: bool = False
    label_parent: QWidget | None = None


@dataclass(frozen=True)
class StatFieldRow:
    label_text: str
    field: QWidget


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


def make_page_text_header(
    parent: QWidget,
    *,
    title_text: str,
    subtitle_text: str,
    title_object_name: str | None = None,
    subtitle_object_name: str | None = None,
    title_alignment: Qt.AlignmentFlag | Qt.Alignment = Qt.AlignLeft | Qt.AlignVCenter,
    subtitle_alignment: Qt.AlignmentFlag | Qt.Alignment = Qt.AlignLeft | Qt.AlignVCenter,
    subtitle_word_wrap: bool = True,
    title_min_height: int | None = None,
) -> PageTextHeaderRefs:
    title_col = QVBoxLayout()
    title_col.setContentsMargins(0, 1, 0, 1)
    title_col.setSpacing(THEME.title_stack_spacing)

    title = make_page_title_label(
        title_text,
        parent,
        alignment=title_alignment,
        object_name=title_object_name or 'pageTitle',
        min_height=title_min_height,
    )
    subtitle = make_hint_label(
        subtitle_text,
        parent,
        word_wrap=subtitle_word_wrap,
        alignment=subtitle_alignment,
        object_name=subtitle_object_name or 'hintLabel',
    )

    title_col.addWidget(title)
    title_col.addWidget(subtitle)
    return PageTextHeaderRefs(layout=title_col, title_label=title, subtitle_label=subtitle)



def make_standard_page_header(
    page: QWidget,
    *,
    title_text: str,
    subtitle_text: str,
    subtitle_object_name: str | None = None,
    title_object_name: str | None = None,
    add_trailing_stretch: bool = True,
    subtitle_word_wrap: bool = True,
    title_alignment: Qt.AlignmentFlag | Qt.Alignment = Qt.AlignLeft | Qt.AlignVCenter,
    subtitle_alignment: Qt.AlignmentFlag | Qt.Alignment = Qt.AlignLeft | Qt.AlignVCenter,
    title_min_height: int | None = None,
) -> PageHeaderRefs:
    row = QHBoxLayout()
    row.setSpacing(THEME.top_button_spacing)

    btn_back = make_nav_button(parent=page)
    title_refs = make_page_text_header(
        page,
        title_text=title_text,
        subtitle_text=subtitle_text,
        title_object_name=title_object_name,
        subtitle_object_name=subtitle_object_name,
        title_alignment=title_alignment,
        subtitle_alignment=subtitle_alignment,
        subtitle_word_wrap=subtitle_word_wrap,
        title_min_height=title_min_height,
    )

    row.setAlignment(Qt.AlignVCenter)
    row.addWidget(btn_back, 0, Qt.AlignVCenter)
    title_refs.title_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    title_refs.subtitle_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
    row.addLayout(title_refs.layout, 0)
    if add_trailing_stretch:
        row.addStretch(1)

    return PageHeaderRefs(
        row=row,
        back_button=btn_back,
        title_layout=title_refs.layout,
        title_label=title_refs.title_label,
        subtitle_label=title_refs.subtitle_label,
    )



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



def add_form_row(
    grid: QGridLayout,
    row: int,
    label_text: str,
    field: QWidget,
    *,
    align_top: bool = False,
    label_parent: QWidget | None = None,
) -> None:
    grid.addWidget(make_field_label(label_text, label_parent), row, 0, Qt.AlignTop if align_top else Qt.Alignment())
    if align_top:
        grid.addWidget(field, row, 1, Qt.AlignTop)
    else:
        grid.addWidget(field, row, 1)



def add_labeled_field_rows(grid: QGridLayout, rows: list[LabeledFieldRow]) -> None:
    for row_index, row in enumerate(rows):
        add_form_row(
            grid,
            row_index,
            row.label_text,
            row.field,
            align_top=row.align_top,
            label_parent=row.label_parent,
        )



def add_two_column_stat_rows(grid: QGridLayout, rows: list[StatFieldRow], *, label_parent: QWidget) -> None:
    for row_index, row in enumerate(rows):
        base_column = (row_index % 2) * 2
        grid.addWidget(make_field_label(row.label_text, label_parent), row_index // 2, base_column)
        grid.addWidget(row.field, row_index // 2, base_column + 1)



def make_right_aligned_button_row(*buttons: QWidget) -> QHBoxLayout:
    row = QHBoxLayout()
    row.addStretch(1)
    for button in buttons:
        row.addWidget(button)
    return row


__all__ = [
    'LabeledFieldRow',
    'PageHeaderRefs',
    'PageTextHeaderRefs',
    'ScrollPanelRefs',
    'StatFieldRow',
    'add_form_row',
    'add_labeled_field_rows',
    'add_two_column_stat_rows',
    'make_form_grid',
    'make_image_shell',
    'make_right_aligned_button_row',
    'make_scroll_panel',
    'make_page_text_header',
    'make_standard_page_header',
    'make_standard_page_layout',
    'make_titled_panel',
]
