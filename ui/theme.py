from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
    block_spacing: int = 10
    row_spacing: int = 8
    top_button_spacing: int = 6
    section_gap: int = 14
    card_inner_spacing: int = 8
    title_stack_spacing: int = 2
    filter_panel_margin_h: int = 14
    filter_panel_margin_v: int = 12
    image_shell_margin: int = 18
    label_padding_x: int = 2

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


def card_colors(kind: str) -> tuple[str, str]:
    mapping = {
        "basic": (THEME.color_basic_bg, THEME.color_basic_border),
        "fabric": (THEME.color_fabric_bg, THEME.color_fabric_border),
        "trim": (THEME.color_trim_bg, THEME.color_trim_border),
        "change": (THEME.color_change_bg, THEME.color_change_border),
    }
    return mapping.get(kind, (THEME.color_basic_bg, THEME.color_basic_border))


def build_app_stylesheet() -> str:
    t = THEME
    icon_bg = hex_to_rgba(t.color_surface, 0.96)
    icon_primary_bg = t.color_primary
    icon_danger_bg = hex_to_rgba(t.color_surface_muted, 0.96)
    dynamic_qss = f"""
        QMainWindow, QWidget {{
            background: {t.color_window};
            color: {t.color_text};
            font-size: {t.base_font_px}px;
        }}
        QWidget#workOrderPage {{
            background: {t.color_window};
        }}
        QLabel {{
            color: {t.color_text};
        }}
        QPushButton {{
            background: {t.color_surface};
            color: {t.color_text_soft};
            border: 1px solid {t.color_border};
            border-radius: 14px;
            padding: 0 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {t.color_surface_alt};
            border-color: {t.color_border_hover};
        }}
        QPushButton:pressed {{
            background: {t.color_pressed};
        }}
        QPushButton:disabled {{
            background: {t.color_disabled_bg};
            color: {t.color_disabled_text};
            border-color: {t.color_disabled_border};
        }}
        QPushButton#navButton, QPushButton#iconAction, QPushButton#iconPrimary, QPushButton#iconDanger {{
            min-width: {t.icon_button_size}px;
            max-width: {t.icon_button_size}px;
            min-height: {t.icon_button_size}px;
            max-height: {t.icon_button_size}px;
            border-radius: {t.control_radius}px;
            padding: 0;
        }}
        QPushButton#navButton, QPushButton#iconAction {{
            background: {icon_bg};
        }}
        QPushButton#primaryAction {{
            background: {t.color_primary};
            border-color: {t.color_primary};
            color: {t.color_text_on_primary};
        }}
        QPushButton#primaryAction:hover {{
            background: {t.color_primary_hover};
            border-color: {t.color_primary_hover};
        }}
        QPushButton#dangerSoft {{
            background: {t.color_surface_muted};
            color: {t.color_text_muted};
        }}
        QPushButton#iconPrimary {{
            background: {icon_primary_bg};
            border-color: {icon_primary_bg};
            color: {t.color_text_on_primary};
        }}
        QPushButton#iconPrimary:hover {{
            background: {t.color_primary_hover};
            border-color: {t.color_primary_hover};
        }}
        QPushButton#iconDanger {{
            background: {icon_danger_bg};
            color: {t.color_text_muted};
            border: 1px solid {t.color_disabled_border};
        }}
        QPushButton#iconDanger:hover {{
            background: {t.color_disabled_bg};
        }}
        QWidget#imageShell {{
            background: {t.color_surface_alt};
            border: 1px solid {t.color_border_soft};
            border-radius: {t.shell_radius}px;
        }}
        QWidget#noteShell {{
            background: transparent;
            border: none;
        }}
        QLabel#featureTitle {{
            font-size: {t.page_title_font_px}px;
            font-weight: 700;
            color: {t.color_text};
            background: transparent;
        }}
        QLabel#featureSubtitle, QLabel#featureHint {{
            color: {t.color_text_muted};
            background: transparent;
        }}
        QLabel#featurePanelTitle, QLabel#featureSectionTitle {{
            font-size: {t.panel_title_font_px}px;
            font-weight: 700;
            color: {t.color_text};
            background: transparent;
        }}
        QFrame#featurePanel {{
            background: {t.color_surface};
            border: 1px solid {t.color_border};
            border-radius: {t.panel_radius}px;
        }}
        QFrame#featureCard {{
            background: {t.color_window};
            border: 1px solid {t.color_border_soft};
            border-radius: {t.panel_radius_sm}px;
        }}
        QLabel#featureLine {{
            color: {t.color_text_soft};
            background: transparent;
        }}
        QListWidget#featureList {{
            border: none;
            background: transparent;
            outline: none;
        }}
        QListWidget#featureList::item {{
            border: none;
            padding: 6px 0;
        }}
        QListWidget#featureList::item:selected {{
            background: transparent;
            color: {t.color_text};
            font-weight: 700;
        }}
        QLabel#summaryChip {{
            background: {t.color_surface};
            border: 1px solid {t.color_border};
            border-radius: {t.control_radius + 3}px;
            padding: 4px 10px;
            font-weight: 600;
            color: {t.color_text_soft};
        }}
    """
    return load_theme_qss() + "\n" + dynamic_qss


def _theme_qss_context() -> dict[str, object]:
    t = THEME
    return {
        "FONT_FAMILY": t.font_family,
        "BASE_FONT_PX": t.base_font_px,
        "WINDOW_BG": t.color_window,
        "TEXT_COLOR": t.color_text,
        "SURFACE_BG": t.color_surface,
        "SURFACE_ALT_BG": t.color_surface_alt,
        "SURFACE_MUTED_BG": t.color_surface_muted,
        "BORDER_COLOR": t.color_border,
        "BORDER_SOFT_COLOR": t.color_border_soft,
        "BORDER_HOVER_COLOR": t.color_border_hover,
        "PRIMARY_COLOR": t.color_primary,
        "PRIMARY_HOVER_COLOR": t.color_primary_hover,
        "PRESSED_COLOR": t.color_pressed,
        "TEXT_SOFT_COLOR": t.color_text_soft,
        "TEXT_MUTED_COLOR": t.color_text_muted,
        "PLACEHOLDER_COLOR": t.color_placeholder,
        "DISABLED_BG": t.color_disabled_bg,
        "DISABLED_BORDER": t.color_disabled_border,
        "DISABLED_TEXT": t.color_disabled_text,
        "PANEL_RADIUS": t.panel_radius,
        "PANEL_RADIUS_SM": t.panel_radius_sm,
        "CONTROL_RADIUS": t.control_radius,
        "INPUT_RADIUS": t.input_radius,
        "EDITOR_RADIUS": t.editor_radius,
        "ICON_BUTTON_SIZE": t.icon_button_size,
        "TOOLTIP_FONT_PX": t.tooltip_font_px,
        "TOOLTIP_PADDING_V": t.tooltip_padding_v,
        "TOOLTIP_PADDING_H": t.tooltip_padding_h,
        "TOOLTIP_RADIUS": t.tooltip_radius,
        "TOOLTIP_BG": t.color_tooltip_bg,
        "TOOLTIP_BORDER": t.color_tooltip_border,
        "TOOLTIP_TEXT": t.color_tooltip_text,
    }


def load_theme_qss() -> str:
    qss_path = Path(__file__).with_name("theme.qss")
    raw = qss_path.read_text(encoding="utf-8")
    return raw.format_map(_theme_qss_context())


def title_label_style(font_px: int | None = None, color: str | None = None, padding_left: int = 0) -> str:
    t = THEME
    return (
        f"QLabel{{font-weight:700;color:{color or t.color_text_soft};background:transparent;"
        f"font-size:{font_px or t.section_title_font_px}px;padding-left:{padding_left}px;}}"
    )


def page_title_style(font_px: int | None = None) -> str:
    return title_label_style(font_px=font_px or THEME.page_title_font_px, color=THEME.color_text)


def panel_title_style(font_px: int | None = None) -> str:
    return title_label_style(font_px=font_px or THEME.panel_title_font_px, color=THEME.color_text)


def title_badge_style(font_px: int | None = None, color: str | None = None,
                      border_color: str | None = None, background: str | None = None,
                      horizontal_padding: int = 12) -> str:
    t = THEME
    return (
        f"QLabel{{font-weight:700;color:{color or t.color_text_soft};"
        f"background:{background or t.color_window};"
        f"border:1px solid {border_color or t.color_border_hover};"
        f"border-radius:{t.control_radius + 4}px;"
        f"font-size:{font_px or t.section_title_font_px}px;"
        f"padding:2px {horizontal_padding}px;}}"
    )


def field_label_style() -> str:
    t = THEME
    return f"QLabel{{font-weight:600;color:{t.color_text_soft};background:transparent;}}"


def strong_field_label_style() -> str:
    t = THEME
    return f"QLabel{{font-weight:700;color:{t.color_text};background:transparent;}}"


def hint_label_style() -> str:
    t = THEME
    return f"QLabel{{background:transparent;color:{t.color_text_muted};padding:0 2px;}}"


def panel_frame_style(*, radius: int | None = None, background: str | None = None, border_color: str | None = None) -> str:
    t = THEME
    return (
        f"QFrame{{border:1px solid {border_color or t.color_border};"
        f"border-radius:{radius or t.panel_radius}px;"
        f"background:{background or t.color_surface};}}"
    )


def inner_panel_frame_style() -> str:
    return panel_frame_style(radius=THEME.panel_radius_sm, background=THEME.color_window, border_color=THEME.color_border_soft)


def list_widget_style() -> str:
    return (
        'QListWidget{border:none;background:transparent;outline:none;}'
        'QListWidget::item{border:none;padding:0px;}'
        'QListWidget::item:selected{background:transparent;}'
    )


def feedback_label_style() -> str:
    t = THEME
    return f'QLabel{{background:transparent;border:none;padding:0 {t.label_padding_x}px;color:{t.color_text};font-weight:700;}}'


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


def read_only_line_edit_style() -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_surface_alt, 0.90)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 8px;border-radius:{t.control_radius}px;}}"
        f"QLineEdit:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.10)};}}"
    )


def editing_line_edit_style() -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.28)};border-radius:{t.control_radius}px;"
        f"padding:0 8px;color:{t.color_text};}}"
    )


def input_line_edit_style(horizontal_padding: int = 6) -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_surface_alt, 0.98)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 {horizontal_padding}px;border-radius:{t.input_radius}px;}}"
        f"QLineEdit:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.10)};}}"
        f"QLineEdit:focus{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.28)};border-radius:{t.input_radius}px;"
        f"padding:0 {horizontal_padding}px;}}"
    )


def combo_box_style() -> str:
    t = THEME
    return (
        f"QComboBox{{background:{hex_to_rgba(t.color_surface_alt, 0.98)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 8px;border-radius:{t.input_radius}px;}}"
        f"QComboBox:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.10)};}}"
        f"QComboBox:focus{{background:{hex_to_rgba(t.color_window, 1.0)};border:1px solid {hex_to_rgba(t.color_primary, 0.28)};}}"
    )


def display_field_style(horizontal_padding: int = 10) -> str:
    t = THEME
    return (
        f"QLabel{{background:{hex_to_rgba(t.color_surface, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_text_soft, 0.12)};border-radius:{t.control_radius}px;"
        f"padding:0 {horizontal_padding}px;color:{t.color_text};}}"
    )


def tool_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba(t.color_text_soft, 0.14)};"
        f"border-radius:{t.control_radius}px;background:{hex_to_rgba(t.color_surface, 1.0)};}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_primary, 0.24)};}}"
    )


def unit_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{background:{hex_to_rgba(t.color_surface_alt, 0.98)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 8px;text-align:left;border-radius:{t.input_radius}px;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.10)};}}"
        f"QToolButton:pressed{{background:{hex_to_rgba(t.color_pressed, 1.0)};}}"
        f"QToolButton:focus{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_primary, 0.28)};}}"
    )


def menu_style() -> str:
    t = THEME
    return f"""
        QMenu{{background:{t.color_surface};border:1px solid {t.color_border};border-radius:10px;padding:6px;color:{t.color_text};}}
        QMenu::item{{padding:8px 14px;border-radius:8px;}}
        QMenu::item:selected{{background:{hex_to_rgba(t.color_primary, 0.14)};color:{t.color_text};}}
        QMenu::separator{{height:1px;background:{t.color_border_soft};margin:6px 8px;}}
    """


def plain_text_edit_style() -> str:
    t = THEME
    return (
        f"QPlainTextEdit{{background:{hex_to_rgba(t.color_surface_alt, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_text_soft, 0.10)};color:{t.color_text};"
        f"font-size:{t.base_font_px}px;border-radius:{t.editor_radius}px;padding:10px;}}"
        f"QPlainTextEdit:focus{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.24)};}}"
    )


def delete_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:none;border-radius:7px;background:{hex_to_rgba(t.color_text_soft, 0.08)};"
        f"color:{t.color_text_soft};font-weight:700;font-size:{t.delete_button_font_px}px;padding:0px;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_text_soft, 0.14)};}}"
    )


def index_button_style(active: bool) -> str:
    t = THEME
    if active:
        return (
            f"QToolButton{{border:1px solid {hex_to_rgba(t.color_primary, 0.30)};border-radius:{t.control_radius}px;"
            f"background:{hex_to_rgba(t.color_window, 1.0)};color:{t.color_text_soft};font-weight:800;}}"
            f"QToolButton:hover{{background:{hex_to_rgba(t.color_surface, 1.0)};}}"
        )
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba(t.color_text_soft, 0.12)};border-radius:{t.control_radius}px;"
        f"background:{hex_to_rgba(t.color_surface_alt, 1.0)};color:{t.color_text_muted};font-weight:700;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_surface, 1.0)};}}"
    )


def disabled_index_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba(t.color_text_soft, 0.08)};border-radius:{t.control_radius}px;"
        f"background:{hex_to_rgba(t.color_surface_muted, 0.86)};color:{hex_to_rgba(t.color_text_muted, 0.48)};font-weight:700;}}"
    )


def table_widget_style() -> str:
    t = THEME
    return (
        "QTableWidget{" 
        f"background:{t.color_window};"
        f"border:1px solid {t.color_border};"
        "border-radius:12px;"
        "gridline-color:transparent;"
        "selection-background-color:transparent;"
        f"selection-color:{t.color_text};"
        "padding:4px;"
        "}"
        "QHeaderView::section{" 
        f"background:{t.color_surface};"
        f"color:{t.color_text_soft};"
        "border:none;"
        f"border-bottom:1px solid {t.color_border_soft};"
        "padding:8px 10px;"
        "font-weight:600;"
        "}"
        "QTableWidget::item{" 
        "border:1px solid transparent;"
        "padding:4px 6px;"
        "}"
        "QTableWidget::item:selected{" 
        f"background:{t.color_surface_alt};"
        f"color:{t.color_text};"
        f"border:1px solid {t.color_border_soft};"
        "}"
        "QTableWidget::item:focus{outline:none;}"
        + table_line_edit_style(prefix="QTableWidget ")
    )


def table_line_edit_style(prefix: str = "") -> str:
    t = THEME
    return (
        f"{prefix}QLineEdit{{"
        f"background:{t.color_surface_alt};"
        "border:1px solid transparent;"
        "border-radius:8px;"
        "padding:0 6px;"
        f"color:{t.color_text};"
        f"selection-background-color:{t.color_pressed};"
        f"selection-color:{t.color_text};"
        "}"
        f"{prefix}QLineEdit:focus{{"
        f"background:{t.color_window};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.28)};"
        "}"
    )


def image_preview_style() -> str:
    t = THEME
    return f"background: transparent; border: none; color: {t.color_placeholder};"


def icon_button_override(font_px: int) -> str:
    return f"font-size: {font_px}px; font-weight: 700; padding: 0;"
