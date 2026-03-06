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
    section_title_font_px: int = 13
    icon_button_font_px: int = 9
    reset_button_font_px: int = 22
    save_button_font_px: int = 20
    delete_button_font_px: int = 10
    icon_button_size: int = 24
    icon_size_sm: int = 12
    icon_size_md: int = 16
    field_height: int = 26
    card_radius: int = 16
    card_shadow_blur: int = 22
    card_shadow_offset_y: int = 5
    page_padding: int = 12
    block_spacing: int = 10
    shell_radius: int = 22
    control_radius: int = 9
    input_radius: int = 8
    editor_radius: int = 14

    color_window: str = "#FFFFFF"
    color_surface: str = "#FFFCF8"
    color_surface_alt: str = "#FBFBFA"
    color_surface_muted: str = "#F7F4F0"
    color_border: str = "#DCCBBB"
    color_border_soft: str = "#E8E1D9"
    color_border_hover: str = "#CDB9A6"
    color_primary: str = "#F2E3D3"
    color_primary_hover: str = "#ECD9C7"
    color_pressed: str = "#F6ECE1"
    color_text: str = "#4B4036"
    color_text_soft: str = "#5A4B40"
    color_text_muted: str = "#9B8674"
    color_placeholder: str = "#9D9084"
    color_disabled_bg: str = "#F4F1EC"
    color_disabled_border: str = "#E1D7CC"
    color_disabled_text: str = "#A39587"

    color_basic_bg: str = "#F6EDB8"
    color_basic_border: str = "#D4C57A"
    color_fabric_bg: str = "#D9EFF5"
    color_fabric_border: str = "#A9CCD7"
    color_trim_bg: str = "#E8DCF6"
    color_trim_border: str = "#C6B1E7"
    color_change_bg: str = "#DDEDDC"
    color_change_border: str = "#A8C9A6"
    color_change_title: str = "#567159"

    color_shadow: str = "#6C5C4E"
    color_icon: str = "#222222"


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
    icon_bg = hex_to_rgba(t.color_surface, 0.72)
    icon_primary_bg = hex_to_rgba(t.color_primary, 0.92)
    icon_danger_bg = hex_to_rgba(t.color_surface_muted, 0.90)
    return f"""
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
            background: {t.color_primary_hover};
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
            border-color: {t.color_border_hover};
            color: {t.color_text_soft};
        }}
        QPushButton#primaryAction:hover {{
            background: {t.color_primary_hover};
        }}
        QPushButton#dangerSoft {{
            background: {t.color_surface_muted};
            color: {t.color_text_muted};
        }}
        QPushButton#iconPrimary {{
            background: {icon_primary_bg};
            border-color: {t.color_border_hover};
            color: {t.color_text_soft};
        }}
        QPushButton#iconPrimary:hover {{
            background: {t.color_primary_hover};
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
    """


def title_label_style(font_px: int | None = None, color: str | None = None, padding_left: int = 0) -> str:
    t = THEME
    return (
        f"QLabel{{font-weight:700;color:{color or t.color_text_soft};background:transparent;"
        f"font-size:{font_px or t.section_title_font_px}px;padding-left:{padding_left}px;}}"
    )


def field_label_style() -> str:
    t = THEME
    return f"QLabel{{font-weight:600;color:{t.color_text_soft};background:transparent;}}"


def read_only_line_edit_style() -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_surface, 0.28)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 8px;border-radius:{t.control_radius}px;}}"
        f"QLineEdit:hover{{background:{hex_to_rgba(t.color_window, 0.48)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.14)};}}"
    )


def editing_line_edit_style() -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_window, 0.82)};"
        f"border:1px solid {hex_to_rgba(t.color_text_soft, 0.22)};border-radius:{t.control_radius}px;"
        f"padding:0 8px;color:{t.color_text};}}"
    )


def input_line_edit_style(horizontal_padding: int = 6) -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_surface, 0.24)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 {horizontal_padding}px;border-radius:{t.input_radius}px;}}"
        f"QLineEdit:hover{{background:{hex_to_rgba(t.color_window, 0.46)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.12)};}}"
        f"QLineEdit:focus{{background:{hex_to_rgba(t.color_window, 0.84)};"
        f"border:1px solid {hex_to_rgba(t.color_text_soft, 0.22)};border-radius:{t.input_radius}px;"
        f"padding:0 {horizontal_padding}px;}}"
    )


def display_field_style(horizontal_padding: int = 10) -> str:
    t = THEME
    return (
        f"QLabel{{background:{hex_to_rgba(t.color_surface, 0.78)};"
        f"border:1px solid {hex_to_rgba(t.color_text_soft, 0.18)};border-radius:{t.control_radius}px;"
        f"padding:0 {horizontal_padding}px;color:{t.color_text};}}"
    )


def tool_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba(t.color_text_soft, 0.18)};"
        f"border-radius:{t.control_radius}px;background:{hex_to_rgba(t.color_surface, 0.70)};}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_window, 0.90)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.24)};}}"
    )


def unit_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{background:{hex_to_rgba(t.color_surface, 0.24)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 8px;text-align:left;border-radius:{t.input_radius}px;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_window, 0.46)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.12)};}}"
        f"QToolButton:pressed{{background:{hex_to_rgba(t.color_pressed, 0.72)};}}"
        f"QToolButton:focus{{background:{hex_to_rgba(t.color_window, 0.84)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.22)};}}"
    )


def menu_style() -> str:
    t = THEME
    return f"""
        QMenu{{background:{t.color_surface};border:1px solid {t.color_border};border-radius:10px;padding:6px;color:{t.color_text};}}
        QMenu::item{{padding:8px 14px;border-radius:8px;}}
        QMenu::item:selected{{background:{t.color_primary};}}
        QMenu::separator{{height:1px;background:{t.color_border_soft};margin:6px 8px;}}
    """


def plain_text_edit_style() -> str:
    t = THEME
    return (
        f"QPlainTextEdit{{background:{hex_to_rgba(t.color_change_bg, 0.52)};"
        f"border:1px solid {hex_to_rgba(t.color_change_title, 0.14)};color:{t.color_text};"
        f"font-size:{t.base_font_px}px;border-radius:{t.editor_radius}px;padding:10px;}}"
        f"QPlainTextEdit:focus{{background:{hex_to_rgba(t.color_window, 0.88)};"
        f"border:1px solid {hex_to_rgba(t.color_change_title, 0.24)};}}"
    )


def delete_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:none;border-radius:7px;background:{hex_to_rgba(t.color_text_soft, 0.10)};"
        f"color:#6A5748;font-weight:700;font-size:{t.delete_button_font_px}px;padding:0px;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_text_soft, 0.16)};}}"
    )


def index_button_style(active: bool) -> str:
    t = THEME
    if active:
        return (
            f"QToolButton{{border:1px solid {hex_to_rgba('#7D6756', 0.26)};border-radius:{t.control_radius}px;"
            f"background:{hex_to_rgba(t.color_surface, 0.95)};color:{t.color_text_soft};font-weight:800;}}"
            f"QToolButton:hover{{background:{hex_to_rgba(t.color_window, 0.98)};}}"
        )
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba('#7D6756', 0.16)};border-radius:{t.control_radius}px;"
        f"background:{hex_to_rgba(t.color_surface, 0.72)};color:#6A584A;font-weight:700;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_window, 0.94)};}}"
    )


def disabled_index_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba('#7D6756', 0.10)};border-radius:{t.control_radius}px;"
        f"background:{hex_to_rgba(t.color_surface, 0.35)};color:{hex_to_rgba('#6A584A', 0.42)};font-weight:700;}}"
    )


def image_preview_style() -> str:
    t = THEME
    return f"background: transparent; border: none; color: {t.color_placeholder};"


def icon_button_override(font_px: int) -> str:
    return f"font-size: {font_px}px; font-weight: 700; padding: 0; qproperty-iconSize: 0px;"
