from __future__ import annotations

from ui.theme_tokens import THEME, hex_to_rgba
from ui.theme_qss import load_theme_qss


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
