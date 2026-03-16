from __future__ import annotations

from ui.theme_tokens import THEME


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
