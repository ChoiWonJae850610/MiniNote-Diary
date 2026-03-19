from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QDateEdit, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QScrollArea, QSizePolicy, QSpinBox, QTableWidget, QVBoxLayout, QWidget, QPushButton

from ui.layout_metrics import OrderPageLayout
from ui.theme import THEME, input_line_edit_style
from ui.widget_factory import (
    apply_button_metrics,
    make_field_label,
    apply_glyph_icon,
    make_action_button,
    make_hint_label,
    make_icon_button,
    make_nav_button,
    make_page_title_label,
    make_panel_frame,
    make_panel_title_label,
)


@dataclass(frozen=True)
class PageHeaderRefs:
    row: QVBoxLayout
    back_button: QWidget
    title_layout: QVBoxLayout
    title_label: QLabel
    subtitle_label: QLabel
    action_layout: QHBoxLayout
    help_button: QWidget | None = None


@dataclass(frozen=True)
class PageActionBarRefs:
    panel: QFrame
    layout: QHBoxLayout


@dataclass(frozen=True)
class TwoColumnPageBodyRefs:
    panel: QWidget
    layout: QHBoxLayout
    left_column: QWidget
    left_layout: QVBoxLayout
    right_column: QWidget
    right_layout: QVBoxLayout


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


def _today_record_text() -> str:
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    now = datetime.now()
    return f"기록 기준 · {now:%Y.%m.%d} {weekdays[now.weekday()]}요일"


def make_diary_action_bar(parent: QWidget) -> PageActionBarRefs:
    panel = make_panel_frame(parent, object_name='featureCard')
    panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout = QHBoxLayout(panel)
    layout.setContentsMargins(14, 10, 14, 10)
    layout.setSpacing(8)
    return PageActionBarRefs(panel=panel, layout=layout)



def make_diary_two_column_body(
    parent: QWidget,
    *,
    left_stretch: int = 3,
    right_stretch: int = 2,
    spacing: int = 12,
) -> TwoColumnPageBodyRefs:
    panel = QWidget(parent)
    layout = QHBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)

    left_column = QWidget(panel)
    left_column.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    left_layout = QVBoxLayout(left_column)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(spacing)

    right_column = QWidget(panel)
    right_column.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    right_layout = QVBoxLayout(right_column)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(0)

    layout.addWidget(left_column, left_stretch)
    layout.addWidget(right_column, right_stretch)
    return TwoColumnPageBodyRefs(
        panel=panel,
        layout=layout,
        left_column=left_column,
        left_layout=left_layout,
        right_column=right_column,
        right_layout=right_layout,
    )



@dataclass(frozen=True)
class DiaryTwoColumnBodyRefs:
    container: QWidget
    layout: QHBoxLayout
    left_column: QWidget
    left_layout: QVBoxLayout
    right_column: QWidget
    right_layout: QVBoxLayout


def make_diary_two_column_body(
    parent: QWidget,
    *,
    left_stretch: int = 1,
    right_stretch: int = 1,
    spacing: int = 12,
) -> DiaryTwoColumnBodyRefs:
    container = QWidget(parent)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)

    left_column = QWidget(container)
    left_layout = QVBoxLayout(left_column)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(spacing)

    right_column = QWidget(container)
    right_layout = QVBoxLayout(right_column)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(spacing)

    layout.addWidget(left_column, left_stretch)
    layout.addWidget(right_column, right_stretch)

    return DiaryTwoColumnBodyRefs(
        container=container,
        layout=layout,
        left_column=left_column,
        left_layout=left_layout,
        right_column=right_column,
        right_layout=right_layout,
    )


def make_diary_section_card(
    parent: QWidget,
    *,
    title_text: str,
    body: QWidget,
    stretch: bool = False,
    contents_margins: tuple[int, int, int, int] = (12, 12, 12, 12),
    spacing: int = 8,
) -> QFrame:
    card = make_panel_frame(parent, object_name='featureCard')
    card.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding if stretch else QSizePolicy.Policy.Minimum,
    )
    layout = QVBoxLayout(card)
    layout.setContentsMargins(*contents_margins)
    layout.setSpacing(spacing)

    title_label = QLabel(title_text, card)
    title_label.setObjectName('featureSectionTitle')
    title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    title_label.setMinimumHeight(24)

    layout.addWidget(title_label, 0, Qt.AlignTop)
    layout.addWidget(body, 1 if stretch else 0)
    return card


def make_standard_page_layout(page: QWidget) -> QVBoxLayout:
    layout = QVBoxLayout(page)
    layout.setContentsMargins(
        THEME.page_padding_x,
        THEME.page_header_top_margin,
        THEME.page_padding_x,
        THEME.page_top_bottom,
    )
    layout.setSpacing(THEME.section_gap)
    return layout


def _apply_standard_header_policy(title_col: QVBoxLayout, title: QLabel, subtitle: QLabel, *, has_subtitle: bool) -> None:
    title_col.setSpacing(THEME.title_stack_spacing if has_subtitle else 0)
    title_col.setAlignment(Qt.AlignVCenter)
    title_min_height = max(
        title.minimumHeight(),
        THEME.page_header_row_min_height,
        THEME.page_title_font_px + 10,
        THEME.nav_button_size + 4,
    )
    title.setMinimumHeight(title_min_height)
    title.setContentsMargins(0, 0, 0, 0)
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

    title_col.addWidget(title, 0, Qt.AlignVCenter)
    title_col.addWidget(subtitle, 0, Qt.AlignVCenter)
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
    header_panel = make_panel_frame(page, object_name='menuHeroPanel')
    header_layout = QVBoxLayout(header_panel)
    header_layout.setContentsMargins(
        THEME.menu_hero_padding_x,
        THEME.menu_hero_padding_y,
        THEME.menu_hero_padding_x,
        THEME.menu_hero_padding_y,
    )
    header_layout.setSpacing(THEME.menu_hero_spacing)

    top_row = QHBoxLayout()
    top_row.setContentsMargins(0, 0, 0, 0)
    top_row.setSpacing(THEME.section_gap)

    action_layout = QHBoxLayout()
    action_layout.setContentsMargins(0, 0, 0, 0)
    action_layout.setSpacing(8)

    btn_back = make_nav_button(parent=page, tooltip='뒤로가기')

    title_label = QLabel(title_text, header_panel)
    title_label.setObjectName(title_object_name or 'menuHeroTitle')
    if title_min_height is not None:
        title_label.setMinimumHeight(title_min_height)
    title_label.setAlignment(title_alignment)

    subtitle_label = QLabel(subtitle_text or _today_record_text(), header_panel)
    subtitle_label.setObjectName(subtitle_object_name or 'menuHeroDate')
    subtitle_label.setWordWrap(subtitle_word_wrap)
    subtitle_label.setAlignment(subtitle_alignment)

    title_col = QVBoxLayout()
    title_col.setContentsMargins(0, 0, 0, 0)
    title_col.setSpacing(6)

    title_row = QHBoxLayout()
    title_row.setContentsMargins(0, 0, 0, 0)
    title_row.setSpacing(10)
    title_row.addWidget(btn_back, 0, Qt.AlignVCenter)
    title_row.addWidget(title_label, 0, Qt.AlignVCenter)
    title_row.addStretch(1)

    title_col.addLayout(title_row)
    title_col.addWidget(subtitle_label, 0, Qt.AlignLeft | Qt.AlignVCenter)

    help_button = make_icon_button(parent=header_panel, object_name='iconAction', tooltip='도움말', font_px=THEME.icon_button_font_px + 1)
    help_button.setFixedSize(THEME.icon_button_size + 10, THEME.icon_button_size + 10)
    apply_glyph_icon(help_button, '?', font_px=THEME.icon_button_font_px + 3, color=THEME.color_icon)

    top_row.addLayout(title_col, 1)
    if add_trailing_stretch:
        action_layout.addWidget(help_button, 0, Qt.AlignTop)
    top_row.addLayout(action_layout, 0)
    header_layout.addLayout(top_row)

    row = QVBoxLayout()
    row.setContentsMargins(
        0,
        THEME.page_header_safe_padding_top + THEME.page_header_row_margin_adjust,
        0,
        THEME.page_header_safe_padding_bottom,
    )
    row.setSpacing(0)
    row.addWidget(header_panel)

    return PageHeaderRefs(
        row=row,
        back_button=btn_back,
        title_layout=title_col,
        title_label=title_label,
        subtitle_label=subtitle_label,
        action_layout=action_layout,
        help_button=help_button,
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


def make_standard_panel_layout(
    parent: QWidget,
    *,
    object_name: str | None = None,
    compact: bool = False,
) -> tuple[QFrame, QVBoxLayout]:
    panel = make_panel_frame(parent, compact=compact, object_name=object_name)
    layout = QVBoxLayout(panel)
    padding = THEME.page_section_padding_compact if compact else THEME.page_section_padding
    layout.setContentsMargins(padding, padding, padding, padding)
    layout.setSpacing(THEME.section_gap if not compact else THEME.row_spacing)
    return panel, layout


def make_standard_action_row() -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(THEME.row_spacing)
    return row


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
    layout.setContentsMargins(pad, THEME.toolbar_strip_padding_y, pad, THEME.toolbar_strip_padding_y)
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
