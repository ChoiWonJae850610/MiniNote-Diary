from __future__ import annotations

from dataclasses import dataclass, replace


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
class ThemePalette:
    name: str
    color_primary: str
    color_primary_hover: str
    color_pressed: str
    color_text_on_primary: str
    color_validation_error: str


@dataclass(frozen=True)
class FontPreset:
    name: str
    font_family: str


DEFAULT_THEME_PALETTE = ThemePalette(
    name="default",
    color_primary="#626B77",
    color_primary_hover="#535B66",
    color_pressed="#E9EDF2",
    color_text_on_primary="#FFFFFF",
    color_validation_error="#FF6B6B",
)

MONO_THEME_PALETTE = ThemePalette(
    name="mono",
    color_primary="#4B5563",
    color_primary_hover="#374151",
    color_pressed="#E5E7EB",
    color_text_on_primary="#FFFFFF",
    color_validation_error="#FF6B6B",
)

THEME_PRESETS: dict[str, ThemePalette] = {
    DEFAULT_THEME_PALETTE.name: DEFAULT_THEME_PALETTE,
    MONO_THEME_PALETTE.name: MONO_THEME_PALETTE,
}

DEFAULT_FONT_PRESET = FontPreset(
    name="pretendard",
    font_family="Pretendard, Noto Sans KR, Segoe UI",
)

CLASSIC_FONT_PRESET = FontPreset(
    name="classic",
    font_family="Noto Sans KR, Malgun Gothic, Segoe UI",
)

FONT_PRESETS: dict[str, FontPreset] = {
    DEFAULT_FONT_PRESET.name: DEFAULT_FONT_PRESET,
    CLASSIC_FONT_PRESET.name: CLASSIC_FONT_PRESET,
}


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
    work_order_left_column_min_width: int = 340
    work_order_left_column_max_width: int = 390
    work_order_right_column_min_width: int = 620
    work_order_left_stretch: int = 4
    work_order_right_stretch: int = 12
    work_order_toolbar_panel_min_height: int = 32
    work_order_column_spacing: int = 10
    work_order_postit_to_note_spacing: int = 0
    work_order_change_note_tab_overlap: int = -20
    work_order_toolbar_inner_padding: int = 4
    work_order_toolbar_inner_padding_y: int = 1
    work_order_postit_top_offset: int = 0
    work_order_postit_top_margin_adjust: int = 2
    work_order_toolbar_to_image_overlap: int = 0
    work_order_toolbar_to_image_gap: int = 14
    work_order_bottom_safe_reserve: int = 0
    work_order_image_preview_min_height: int = 610
    work_order_change_note_body_min_height: int = 180
    work_order_bottom_match_adjust: int = 12
    work_order_change_note_bottom_trim: int = 6
    work_order_change_note_visual_trim: int = 4
    work_order_change_note_min_width: int = 260
    dashboard_metric_card_min_height: int = 100
    dashboard_metric_padding_x: int = 20
    dashboard_metric_padding_y: int = 18
    dashboard_metric_spacing: int = 12
    dashboard_recent_padding: int = 18
    dashboard_recent_spacing: int = 10
    dashboard_recent_item_spacing: int = 4
    stats_note_item_padding_x: int = 12
    stats_note_item_padding_y: int = 10
    stats_note_item_spacing: int = 5
    page_header_row_margin_adjust: int = 0
    toolbar_strip_padding_y: int = 6
    dashboard_recent_panel_min_height: int = 312
    dashboard_metric_value_font_px: int = 28
    menu_hero_padding_x: int = 26
    menu_hero_padding_y: int = 22
    menu_hero_spacing: int = 10
    menu_section_padding: int = 18
    menu_section_spacing: int = 12
    menu_action_card_min_height: int = 84
    menu_action_card_padding_x: int = 16
    menu_action_card_padding_y: int = 12
    menu_recent_row_count: int = 6
    menu_recent_item_min_height: int = 84
    menu_recent_item_padding_x: int = 14
    menu_recent_item_padding_y: int = 12
    menu_recent_item_spacing: int = 6
    menu_recent_primary_height: int = 24
    menu_recent_secondary_height: int = 20
    menu_recent_tertiary_height: int = 18
    menu_utility_card_min_height: int = 76
    table_header_height: int = 34
    dialog_button_height: int = 34
    dialog_field_height: int = 30
    dialog_status_icon_min_width: int = 22
    calendar_button_size: int = 30
    order_input_height: int = 34
    unit_dialog_width: int = 520
    unit_dialog_height: int = 420
    product_type_dialog_width: int = 560
    product_type_dialog_height: int = 520
    window_min_width: int = 800
    window_min_height: int = 900
    note_dialog_min_width: int = 520
    note_dialog_min_height: int = 360
    menu_button_min_width: int = 116
    menu_button_min_height: int = 108
    menu_button_icon_size: tuple[int, int] = (26, 26)

    icon_button_size: int = 24
    nav_button_size: int = 22
    icon_size_sm: int = 12
    icon_size_md: int = 16
    field_height: int = 26
    field_label_width: int = 44
    basic_type_field_width: int = 74
    basic_type_manage_button_width: int = 26
    basic_style_field_extra_width: int = 140
    postit_unit_button_width: int = 90
    calendar_display_width: int = 110
    postit_qty_field_max_width: int = 86
    postit_unit_button_min_width: int = 60
    table_row_height: int = 30
    postit_index_button_min_size: int = 24
    section_badge_height: int = 28
    summary_chip_height: int = 30
    feedback_label_height: int = 20
    image_preview_min_height: int = 520
    image_preview_min_size: int = 240
    memo_min_height: int = 110
    order_memo_min_height: int = 88
    postit_bar_max_height: int = 266
    postit_card_height: int = 198
    postit_index_row_height: int = 28
    postit_index_button_size: int = 24
    delete_button_size: int = 14
    tooltip_font_px: int = 11
    tooltip_font_family: str = DEFAULT_FONT_PRESET.font_family
    tooltip_font_weight: int = 600
    tooltip_padding_v: int = 1
    tooltip_padding_h: int = 5
    tooltip_radius: int = 5

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
    page_header_safe_padding_top: int = 0
    page_header_safe_padding_bottom: int = 0
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

    font_family: str = DEFAULT_FONT_PRESET.font_family

    color_window: str = "#FFFFFF"
    color_surface: str = "#FAFAFB"
    color_surface_alt: str = "#F5F6F8"
    color_surface_muted: str = "#EFF1F4"
    color_border: str = "#D7DCE3"
    color_border_soft: str = "#E7EBF0"
    color_border_hover: str = "#B8C0CC"

    color_primary: str = DEFAULT_THEME_PALETTE.color_primary
    color_primary_hover: str = DEFAULT_THEME_PALETTE.color_primary_hover
    color_pressed: str = DEFAULT_THEME_PALETTE.color_pressed
    color_text_on_primary: str = DEFAULT_THEME_PALETTE.color_text_on_primary

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
    color_validation_error: str = DEFAULT_THEME_PALETTE.color_validation_error


def build_theme_tokens(theme_name: str = "default", font_name: str = "pretendard") -> ThemeTokens:
    palette = THEME_PRESETS.get(str(theme_name or "").strip(), DEFAULT_THEME_PALETTE)
    font = FONT_PRESETS.get(str(font_name or "").strip(), DEFAULT_FONT_PRESET)
    return replace(
        ThemeTokens(),
        font_family=font.font_family,
        color_primary=palette.color_primary,
        color_primary_hover=palette.color_primary_hover,
        color_pressed=palette.color_pressed,
        color_text_on_primary=palette.color_text_on_primary,
        color_validation_error=palette.color_validation_error,
    )


THEME = build_theme_tokens()
