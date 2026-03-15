from __future__ import annotations

from ui.theme_tokens import THEME
from ui.theme_input_styles import (
    combo_box_style,
    editing_line_edit_style,
    input_line_edit_style,
    plain_text_edit_style,
    read_only_line_edit_style,
    table_line_edit_style,
)
from ui.theme_panel_styles import (
    delete_button_style,
    disabled_index_button_style,
    display_field_style,
    feedback_label_style,
    field_label_style,
    hint_label_style,
    icon_button_override,
    image_preview_style,
    index_button_style,
    inner_panel_frame_style,
    list_widget_style,
    menu_style,
    page_title_style,
    panel_frame_style,
    panel_title_style,
    strong_field_label_style,
    title_badge_style,
    title_label_style,
    tool_button_style,
    tooltip_style_override,
    unit_button_style,
)
from ui.theme_table_styles import table_widget_style


def dialog_layout_margins() -> tuple[int, int, int, int]:
    return (14, 14, 14, 14)


def dialog_inner_margins() -> tuple[int, int, int, int]:
    return (20, 18, 20, 18)


def compact_popup_margins() -> tuple[int, int, int, int]:
    return (8, 8, 8, 8)


def status_row_margins() -> tuple[int, int, int, int]:
    return (14, 10, 14, 10)


def page_layout_margins(extra_x: int = 0, extra_y: int = 0) -> tuple[int, int, int, int]:
    t = THEME
    return (t.page_padding_x + extra_x, t.page_padding_y + extra_y, t.page_padding_x + extra_x, t.page_padding_y + extra_y)


__all__ = [
    'THEME',
    'combo_box_style',
    'compact_popup_margins',
    'delete_button_style',
    'dialog_inner_margins',
    'dialog_layout_margins',
    'disabled_index_button_style',
    'display_field_style',
    'editing_line_edit_style',
    'feedback_label_style',
    'field_label_style',
    'hint_label_style',
    'icon_button_override',
    'image_preview_style',
    'index_button_style',
    'inner_panel_frame_style',
    'input_line_edit_style',
    'list_widget_style',
    'menu_style',
    'page_layout_margins',
    'page_title_style',
    'panel_frame_style',
    'panel_title_style',
    'plain_text_edit_style',
    'read_only_line_edit_style',
    'status_row_margins',
    'strong_field_label_style',
    'table_line_edit_style',
    'table_widget_style',
    'title_badge_style',
    'title_label_style',
    'tool_button_style',
    'tooltip_style_override',
    'unit_button_style',
]
