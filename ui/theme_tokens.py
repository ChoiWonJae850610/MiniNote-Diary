from __future__ import annotations

from dataclasses import dataclass


def _clamp_alpha(alpha: float) -> float:
    return max(0.0, min(1.0, alpha))


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    color = (hex_color or "#000000").lstrip("#")
    if len(color) != 6:
        color = "000000"
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {_clamp_alpha(alpha):.3f})"


@dataclass(frozen=True)
class ThemeTokens:
    base_font_px: int = 12
    menu_title_font_px: int = 22
    page_title_font_px: int = 22
    panel_title_font_px: int = 14
    section_title_font_px: int = 13
    icon_button_font_px: int = 9
    reset_button_font_px: int = 22
    save_button_font_px: int = 20
    delete_button_font_px: int = 10

    menu_button_width: int = 360
    menu_button_height: int = 54
    footer_button_width: int = 140
    footer_button_height: int = 32
    primary_button_height: int = 38
    primary_button_width: int = 170
    secondary_button_width: int = 140
    reload_button_width: int = 130
    page_list_panel_min_width: int = 320
    page_list_spacing: int = 6
    page_master_detail_list_stretch: int = 4
    page_master_detail_detail_stretch: int = 6
    page_body_split_spacing: int = 14
    page_right_panel_min_width: int = 640
    page_detail_panel_spacing: int = 16
    page_action_row_top_margin: int = 10
    page_wide_button_width: int = 210
    work_order_left_column_min_width: int = 420
    work_order_right_column_min_width: int = 520
    work_order_left_stretch: int = 5
    work_order_right_stretch: int = 6
    work_order_toolbar_panel_min_height: int = 52
    work_order_column_spacing: int = 10
    work_order_toolbar_inner_padding: int = 10
    work_order_change_note_min_width: int = 220
    dashboard_metric_card_min_height: int = 96
    dashboard_recent_panel_min_height: int = 228
    dashboard_metric_value_font_px: int = 18
    table_header_height: int = 34
    dialog_button_height: int = 34
    dialog_field_height: int = 30
    order_input_height: int = 34
    unit_dialog_width: int = 520
    unit_dialog_height: int = 420
    window_min_width: int = 1080
    window_min_height: int = 760
    note_dialog_min_width: int = 520
    note_dialog_min_height: int = 360

    icon_button_size: int = 24
    nav_button_size: int = 32
    icon_size_sm: int = 12
    icon_size_md: int = 16
    field_height: int = 26
    field_label_width: int = 44
    calendar_display_width: int = 110
    table_row_height: int = 30
    section_badge_height: int = 28
    summary_chip_height: int = 30
    feedback_label_height: int = 20
    image_preview_min_height: int = 520
    image_preview_min_size: int = 240
    memo_min_height: int = 110
    order_memo_min_height: int = 88
    postit_bar_max_height: int = 232
    postit_card_height: int = 198
    postit_index_row_height: int = 28
    postit_index_button_size: int = 24
    delete_button_size: int = 14
    tooltip_font_px: int = 12
    tooltip_padding_v: int = 6
    tooltip_padding_h: int = 10
    tooltip_radius: int = 8

    page_padding: int = 12
    page_padding_x: int = 30
    page_padding_y: int = 0
    page_section_padding: int = 16
    page_section_padding_compact: int = 14
    page_top_bottom: int = 20
    page_header_top_margin: int = 20
    page_header_block_gap: int = 14
    page_header_row_min_height: int = 46
    block_spacing: int = 10
    row_spacing: int = 8
    top_button_spacing: int = 6
    section_gap: int = 14
    card_inner_spacing: int = 8
    title_stack_spacing: int = 3
    page_header_safe_padding_top: int = 5
    page_header_safe_padding_bottom: int = 3
    filter_panel_margin_h: int = 14
    filter_panel_margin_v: int = 12
    image_shell_margin: int = 18
    label_padding_x: int = 2
    section_panel_min_height: int = 0

    card_radius: int = 16
    card_shadow_blur: int = 22
    card_shadow_offset_y: int = 5
    shell_radius: int = 22
    panel_radius: int = 18
    panel_radius_sm: int = 14
    list_radius: int = 12
    control_radius: int = 9
    input_radius: int = 8
    editor_radius: int = 14

    font_family: str = "Pretendard, Noto Sans KR, Segoe UI"

    color_window: str = "#FFFFFF"
    color_surface: str = "#FAFAFB"
    color_surface_alt: str = "#F5F6F8"
    color_surface_muted: str = "#EFF1F4"
    color_border: str = "#D7DCE3"
    color_border_soft: str = "#E7EBF0"
    color_border_hover: str = "#B8C0CC"

    color_primary: str = "#626B77"
    color_primary_hover: str = "#535B66"
    color_pressed: str = "#E9EDF2"
    color_text_on_primary: str = "#FFFFFF"

    color_text: str = "#1F2933"
    color_text_soft: str = "#364152"
    color_text_muted: str = "#6C7684"
    color_placeholder: str = "#98A2B3"
    color_disabled_bg: str = "#F3F5F7"
    color_disabled_border: str = "#E1E6EC"
    color_disabled_text: str = "#A0A8B5"

    color_basic_bg: str = "#F8F9FB"
    color_basic_border: str = "#D9DEE6"
    color_fabric_bg: str = "#F8F9FB"
    color_fabric_border: str = "#D9DEE6"
    color_trim_bg: str = "#F8F9FB"
    color_trim_border: str = "#D9DEE6"
    color_change_bg: str = "#EDF1F4"
    color_change_border: str = "#CAD2DC"
    color_change_title: str = "#525C69"

    color_shadow: str = "#6B7280"
    color_icon: str = "#2F3945"
    color_tooltip_bg: str = "#FFFFFF"
    color_tooltip_border: str = "#D7DCE3"
    color_tooltip_text: str = "#364152"


THEME = ThemeTokens()
