from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QDateEdit, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QScrollArea, QSizePolicy, QSpinBox, QTableWidget, QVBoxLayout, QWidget

from ui.layout_metrics import OrderPageLayout
from ui.theme import THEME, input_line_edit_style
from ui.widget_factory import (
    apply_button_metrics,
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


def _apply_standard_header_policy(title_col: QVBoxLayout, title: QLabel, subtitle: QLabel, *, has_subtitle: bool) -> None:
    title_col.setSpacing(THEME.title_stack_spacing if has_subtitle else 0)
    title_min_height = max(
        title.minimumHeight(),
        THEME.page_header_row_min_height,
        THEME.page_title_font_px + THEME.page_header_safe_padding_top + THEME.page_header_safe_padding_bottom + 18,
        THEME.nav_button_size + THEME.page_header_safe_padding_top + THEME.page_header_safe_padding_bottom + 6,
    )
    title.setMinimumHeight(title_min_height)
    title.setContentsMargins(0, THEME.page_header_safe_padding_top, 0, THEME.page_header_safe_padding_bottom)
    title.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    subtitle.setVisible(has_subtitle)
    subtitle.setContentsMargins(0, 0, 0, 0)
    subtitle.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)


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
    title_col.setContentsMargins(0, 0, 0, 0)
    has_subtitle = bool(subtitle_text.strip())

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
    _apply_standard_header_policy(title_col, title, subtitle, has_subtitle=has_subtitle)
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
    row.setContentsMargins(0, THEME.page_header_safe_padding_top + 1, 0, THEME.page_header_safe_padding_bottom)
    row.setSpacing(THEME.top_button_spacing)
    row.setAlignment(Qt.AlignVCenter)

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

    row.addWidget(btn_back, 0, Qt.AlignVCenter)
    row.addLayout(title_refs.layout, 0)
    row.setStretch(1, 0)
    row.setSizeConstraint(QHBoxLayout.SetMinimumSize)
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




def make_compact_toolbar_panel(parent: QWidget, *, object_name: str | None = None) -> tuple[QFrame, QHBoxLayout]:
    panel = make_panel_frame(parent, compact=True)
    if object_name:
        panel.setObjectName(object_name)
    layout = QHBoxLayout(panel)
    layout.setContentsMargins(
        THEME.page_section_padding_compact,
        THEME.page_section_padding_compact - 2,
        THEME.page_section_padding_compact,
        THEME.page_section_padding_compact - 2,
    )
    layout.setSpacing(THEME.row_spacing)
    return panel, layout


def make_standard_toolbar_strip(parent: QWidget, *, object_name: str | None = None) -> tuple[QFrame, QHBoxLayout]:
    panel, layout = make_compact_toolbar_panel(parent, object_name=object_name)
    pad = THEME.work_order_toolbar_inner_padding
    layout.setContentsMargins(pad, 6, pad, 6)
    layout.setSpacing(THEME.top_button_spacing)
    panel.setMinimumHeight(THEME.work_order_toolbar_panel_min_height)
    panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return panel, layout


def apply_toolbar_field_metrics(*widgets: QWidget) -> None:
    target_height = THEME.order_input_height
    for widget in widgets:
        if widget is None:
            continue
        if hasattr(widget, 'setFixedHeight'):
            widget.setFixedHeight(target_height)
        if isinstance(widget, (QLineEdit, QComboBox, QSpinBox, QDateEdit)):
            widget.setStyleSheet(input_line_edit_style())


def apply_form_field_metrics(*widgets: QWidget) -> None:
    target_height = THEME.order_input_height
    for widget in widgets:
        if widget is None:
            continue
        if hasattr(widget, 'setFixedHeight'):
            widget.setFixedHeight(target_height)
        if isinstance(widget, (QLineEdit, QComboBox, QSpinBox, QDateEdit)):
            widget.setStyleSheet(input_line_edit_style())


def make_standard_body_row() -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(THEME.page_body_split_spacing)
    return row


def make_standard_list_panel(
    parent: QWidget,
    *,
    title_text: str,
    hint_text: str = '',
    list_min_height: int = 0,
) -> tuple[QFrame, QVBoxLayout, QListWidget]:
    panel, layout = make_titled_panel(parent, title_text=title_text, hint_text=hint_text)
    panel.setMinimumWidth(THEME.page_list_panel_min_width)
    list_widget = make_standard_list_widget(panel, min_height=list_min_height)
    layout.addWidget(list_widget, 1)
    return panel, layout, list_widget


def apply_scroll_panel_metrics(scroll_area: QScrollArea, *, min_width: int | None = None) -> None:
    if min_width is not None:
        scroll_area.setMinimumWidth(min_width)
    scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


def make_standard_stat_panel(parent: QWidget) -> tuple[QFrame, QGridLayout]:
    panel = QFrame(parent)
    panel.setObjectName('innerPanelFrame')
    grid = make_form_grid(parent=panel)
    grid.setContentsMargins(
        THEME.filter_panel_margin_h,
        THEME.filter_panel_margin_v,
        THEME.filter_panel_margin_h,
        THEME.filter_panel_margin_v,
    )
    return panel, grid


def apply_wide_primary_button_metrics(*buttons: QWidget) -> None:
    apply_primary_button_metrics(*buttons, width=THEME.page_wide_button_width)



def make_standard_feedback_label(parent: QWidget, *, object_name: str = 'hintLabel') -> QLabel:
    label = make_hint_label('', parent, word_wrap=False, alignment=Qt.AlignLeft | Qt.AlignVCenter, object_name=object_name)
    label.setMinimumHeight(THEME.feedback_label_height)
    return label


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
    row.setContentsMargins(0, THEME.page_action_row_top_margin, 0, 0)
    row.setSpacing(THEME.row_spacing)
    row.addStretch(1)
    for button in buttons:
        row.addWidget(button)
    return row



def apply_primary_button_metrics(*buttons: QWidget, width: int | None = None) -> None:
    for button in buttons:
        if button is None:
            continue
        apply_button_metrics(
            button,
            width=width or THEME.primary_button_width,
            height=THEME.primary_button_height,
        )


def apply_secondary_button_metrics(*buttons: QWidget, width: int | None = None) -> None:
    for button in buttons:
        if button is None:
            continue
        apply_button_metrics(
            button,
            width=width or THEME.secondary_button_width,
            height=THEME.primary_button_height,
        )


def make_standard_list_widget(parent: QWidget, *, min_height: int = 0) -> QListWidget:
    widget = QListWidget(parent)
    widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    widget.setSpacing(THEME.page_list_spacing)
    if min_height > 0:
        widget.setMinimumHeight(min_height)
    return widget


def apply_table_widget_metrics(table: QTableWidget, *, min_height: int | None = None) -> None:
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionMode(QTableWidget.NoSelection)
    table.setFocusPolicy(Qt.NoFocus)
    table.setAlternatingRowColors(False)
    table.setWordWrap(False)
    table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    table.setShowGrid(False)
    table.setCornerButtonEnabled(False)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(THEME.table_row_height)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
    table.horizontalHeader().setMinimumHeight(THEME.table_header_height)
    table.horizontalHeader().setFixedHeight(THEME.table_header_height)
    if min_height is not None:
        table.setMinimumHeight(min_height)


__all__ = [
    'LabeledFieldRow',
    'PageHeaderRefs',
    'PageTextHeaderRefs',
    'ScrollPanelRefs',
    'StatFieldRow',
    'add_form_row',
    'add_labeled_field_rows',
    'apply_primary_button_metrics',
    'apply_wide_primary_button_metrics',
    'apply_secondary_button_metrics',
    'add_two_column_stat_rows',
    'make_compact_toolbar_panel',
    'apply_toolbar_field_metrics',
    'apply_table_widget_metrics',
    'apply_form_field_metrics',
    'make_form_grid',
    'make_image_shell',
    'make_right_aligned_button_row',
    'make_standard_body_row',
    'make_standard_list_panel',
    'make_scroll_panel',
    'apply_scroll_panel_metrics',
    'make_standard_stat_panel',
    'make_page_text_header',
    'make_standard_list_widget',
    'make_standard_page_header',
    'make_standard_page_layout',
    'make_titled_panel',
]
