from __future__ import annotations

from pathlib import Path

from ui.theme_tokens import THEME


def _theme_qss_context() -> dict[str, object]:
    t = THEME
    return {
        "__FONT_FAMILY__": t.font_family,
        "__BASE_FONT_PX__": t.base_font_px,
        "__WINDOW_BG__": t.color_window,
        "__TEXT_COLOR__": t.color_text,
        "__SURFACE_BG__": t.color_surface,
        "__SURFACE_ALT_BG__": t.color_surface_alt,
        "__SURFACE_MUTED_BG__": t.color_surface_muted,
        "__BORDER_COLOR__": t.color_border,
        "__BORDER_SOFT_COLOR__": t.color_border_soft,
        "__BORDER_HOVER_COLOR__": t.color_border_hover,
        "__PRIMARY_COLOR__": t.color_primary,
        "__PRIMARY_HOVER_COLOR__": t.color_primary_hover,
        "__PRESSED_COLOR__": t.color_pressed,
        "__TEXT_SOFT_COLOR__": t.color_text_soft,
        "__TEXT_MUTED_COLOR__": t.color_text_muted,
        "__PLACEHOLDER_COLOR__": t.color_placeholder,
        "__DISABLED_BG__": t.color_disabled_bg,
        "__DISABLED_BORDER__": t.color_disabled_border,
        "__DISABLED_TEXT__": t.color_disabled_text,
        "__PANEL_RADIUS__": t.panel_radius,
        "__PANEL_RADIUS_SM__": t.panel_radius_sm,
        "__CONTROL_RADIUS__": t.control_radius,
        "__INPUT_RADIUS__": t.input_radius,
        "__EDITOR_RADIUS__": t.editor_radius,
        "__ICON_BUTTON_SIZE__": t.icon_button_size,
        "__TOOLTIP_FONT_PX__": t.tooltip_font_px,
        "__TOOLTIP_FONT_FAMILY__": t.tooltip_font_family,
        "__TOOLTIP_FONT_WEIGHT__": t.tooltip_font_weight,
        "__TOOLTIP_PADDING_V__": t.tooltip_padding_v,
        "__TOOLTIP_PADDING_H__": t.tooltip_padding_h,
        "__TOOLTIP_RADIUS__": t.tooltip_radius,
        "__TOOLTIP_BG__": t.color_tooltip_bg,
        "__TOOLTIP_BORDER__": t.color_tooltip_border,
        "__TOOLTIP_TEXT__": t.color_tooltip_text,
    }


def load_theme_qss() -> str:
    qss_path = Path(__file__).with_name("theme.qss")
    raw = qss_path.read_text(encoding="utf-8")
    rendered = raw
    for token, value in _theme_qss_context().items():
        rendered = rendered.replace(token, str(value))
    return rendered
