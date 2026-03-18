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

        QLabel#menuHeroTitle {{
            font-size: {t.page_title_font_px + 5}px;
            font-weight: 800;
            color: {t.color_text};
            background: transparent;
            padding: 0;
        }}
        QLabel#menuHeroDate {{
            color: {t.color_primary};
            font-weight: 700;
            background: transparent;
            padding: 0;
        }}
        QLabel#menuHeroSubtitle {{
            color: {t.color_text_muted};
            background: transparent;
        }}
        QLabel#menuSectionLabel {{
            font-size: {t.panel_title_font_px}px;
            font-weight: 800;
            color: {t.color_text};
            background: transparent;
            padding: 0 0 2px 0;
        }}
        QLabel#menuSectionHint {{
            color: {t.color_text_muted};
            background: transparent;
        }}
        QLabel#menuMetricTitle {{
            color: {t.color_text_muted};
            background: transparent;
            font-weight: 700;
        }}
        QLabel#menuMetricValue {{
            font-size: {t.dashboard_metric_value_font_px}px;
            font-weight: 800;
            color: {t.color_text};
            background: transparent;
            padding-top: 2px;
        }}

        QLabel#menuSectionHint {{
            color: {t.color_text_muted};
            background: transparent;
            font-size: 12px;
        }}
        QLabel#menuListPrimary {{
            font-size: 13px;
            font-weight: 800;
            color: {t.color_text};
            background: transparent;
            min-height: {t.menu_recent_primary_height}px;
        }}
        QLabel#menuListSecondary {{
            color: {t.color_text_soft};
            background: transparent;
            min-height: {t.menu_recent_secondary_height}px;
            font-size: 12px;
        }}
        QLabel#menuListTertiary {{
            color: {t.color_text_muted};
            background: transparent;
            min-height: {t.menu_recent_tertiary_height}px;
            font-size: 11px;
        }}
    """


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
            border-radius: {t.control_radius}px;
            padding: 0;
        }}
        QPushButton#navButton {{
            min-width: {t.nav_button_size}px;
            max-width: {t.nav_button_size}px;
            min-height: {t.nav_button_size}px;
            max-height: {t.nav_button_size}px;
            background: {icon_bg};
        }}
        QPushButton#iconAction, QPushButton#iconPrimary, QPushButton#iconDanger {{
            min-width: {t.icon_button_size}px;
            max-width: {t.icon_button_size}px;
            min-height: {t.icon_button_size}px;
            max-height: {t.icon_button_size}px;
        }}
        QPushButton#iconAction {{
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
        QPushButton#menuActionCard, QPushButton#menuUtilityCard {{
            text-align: left;
            padding: {t.menu_action_card_padding_y}px {t.menu_action_card_padding_x}px;
            border-radius: {t.panel_radius}px;
            font-weight: 800;
        }}
        QPushButton#menuActionCard {{
            background: #FFFFFF;
            color: {t.color_text};
            border: 1px solid #D9DEE7;
            border-left: 5px solid #C7D2E2;
        }}
        QPushButton#menuActionCard:hover {{
            background: #F8FAFC;
            border-color: {t.color_border_hover};
            border-left: 5px solid {t.color_primary};
        }}
        QPushButton#menuUtilityCard {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FBF7FF, stop:1 #F2EAFE);
            color: {t.color_text};
            border: 1px solid #D8CAE9;
            border-left: 5px solid #C7B7EC;
        }}
        QPushButton#menuUtilityCard:hover {{
            background: #FCFAFF;
            border-color: #C7B7EC;
        }}
        QPushButton#menuIconCard {{
            background: #FFFFFF;
            color: {t.color_text};
            border: 1px solid #E2E7EF;
            border-radius: {t.panel_radius}px;
            padding: 10px 8px 8px 8px;
            text-align: center;
            font-weight: 800;
            line-height: 1.35;
        }}
        QPushButton#menuIconCard:hover {{
            background: #FFFCF6;
            border-color: {t.color_border_hover};
        }}
        QPushButton#menuIconCard[accent="peach"] {{
            border-top: 5px solid #E8D8B8;
        }}
        QPushButton#menuIconCard[accent="lavender"] {{
            border-top: 5px solid #D9CCF2;
        }}
        QPushButton#menuIconCard[accent="mint"] {{
            border-top: 5px solid #CBE8DD;
        }}
        QPushButton#menuIconCard[accent="sky"] {{
            border-top: 5px solid #CFE0F6;
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
        QFrame#menuHeroPanel {{
            background: #FFF9EF;
            border: 1px solid #E8D8B8;
            border-radius: {t.panel_radius}px;
        }}
        QFrame#menuSectionPanel {{
            background: #FCFCFE;
            border: 1px solid #E0E4EB;
            border-radius: {t.panel_radius}px;
        }}
        QFrame#menuMetricCard {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFFFFF, stop:1 #F8F4FF);
            border: 1px solid #E3DCEF;
            border-radius: {t.panel_radius_sm + 3}px;
        }}
        QFrame#menuRecentPanel {{
            background: #FCFCFE;
            border: 1px solid #E0E4EB;
            border-radius: {t.panel_radius}px;
        }}
        QWidget#menuRecentViewport {{
            background: transparent;
        }}
        QScrollArea#menuRecentScroll {{
            background: transparent;
            border: none;
        }}
        QFrame#menuRecentItemCard {{
            background: #FFFFFF;
            border: 1px solid #E5EAF0;
            border-left: 4px solid #E8D8B8;
            border-radius: {t.panel_radius_sm + 2}px;
        }}
        QFrame#menuRecentItemCard:hover {{
            border-color: {t.color_border_hover};
            border-left: 4px solid {t.color_primary};
            background: #FFFEFB;
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


def build_feature_styles() -> str:
    t = THEME
    return f"""
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


def build_app_stylesheet() -> str:
    return "\n".join([
        base_app_qss(),
        build_global_widget_styles(),
        build_button_styles(),
        build_panel_styles(),
        build_feature_styles(),
    ])