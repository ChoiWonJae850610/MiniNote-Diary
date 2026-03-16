from __future__ import annotations

from ui.theme_qss import load_theme_qss
from ui.theme_tokens import THEME, hex_to_rgba


def base_app_qss() -> str:
    return load_theme_qss()


def build_global_widget_styles() -> str:
    t = THEME
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
        QLabel#pageTitle, QLabel#panelTitle, QLabel#sectionTitle {{
            background: transparent;
            color: {t.color_text};
            font-weight: 700;
        }}
        QLabel#pageTitle {{
            font-size: {t.page_title_font_px}px;
        }}
        QLabel#panelTitle {{
            font-size: {t.panel_title_font_px}px;
        }}
        QLabel#sectionTitle {{
            font-size: {t.section_title_font_px}px;
        }}
        QLabel#hintLabel {{
            background: transparent;
            color: {t.color_text_muted};
            padding: 0 {t.label_padding_x}px;
        }}
        QLabel#fieldLabel {{
            background: transparent;
            color: {t.color_text_soft};
            font-weight: 600;
        }}
        QLabel#strongFieldLabel {{
            background: transparent;
            color: {t.color_text};
            font-weight: 700;
        }}
        QLabel#metaLabel {{
            background: transparent;
            color: {t.color_text_soft};
        }}
        QLabel#displayField {{
            background: {hex_to_rgba(t.color_surface, 1.0)};
            border: 1px solid {hex_to_rgba(t.color_text_soft, 0.12)};
            border-radius: {t.control_radius}px;
            padding: 0 10px;
            color: {t.color_text};
        }}
    """


def build_panel_styles() -> str:
    t = THEME
    return f"""
        QWidget#imageShell, QFrame#imageShell {{
            background: {t.color_surface_alt};
            border: 1px solid {t.color_border_soft};
            border-radius: {t.shell_radius}px;
        }}
        QFrame#panelFrame {{
            background: {t.color_surface};
            border: 1px solid {t.color_border};
            border-radius: {t.panel_radius}px;
        }}
        QFrame#panelFrameCompact {{
            background: {t.color_surface};
            border: 1px solid {t.color_border};
            border-radius: {t.panel_radius_sm}px;
        }}
        QFrame#innerPanelFrame {{
            background: {t.color_window};
            border: 1px solid {t.color_border_soft};
            border-radius: {t.panel_radius_sm}px;
        }}
        QFrame#listCard {{
            background: {t.color_window};
            border: 1px solid {t.color_border_soft};
            border-radius: {t.panel_radius_sm}px;
        }}
        QFrame#listCard:hover {{
            border-color: {t.color_border_hover};
            background: {t.color_surface};
        }}
        QWidget#noteShell {{
            background: transparent;
            border: none;
        }}
    """
