from __future__ import annotations

from ui.theme_tokens import THEME, hex_to_rgba


def build_button_styles() -> str:
    t = THEME
    icon_bg = hex_to_rgba(t.color_surface, 0.96)
    icon_primary_bg = t.color_primary
    icon_danger_bg = hex_to_rgba(t.color_surface_muted, 0.96)
    return f"""
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
    """
