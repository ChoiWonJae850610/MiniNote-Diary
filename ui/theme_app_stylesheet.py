from __future__ import annotations

from ui.theme_app_button_sections import build_button_styles
from ui.theme_app_core_sections import base_app_qss, build_global_widget_styles, build_panel_styles
from ui.theme_app_feature_sections import build_feature_styles


def build_app_stylesheet() -> str:
    return "\n".join([
        base_app_qss(),
        build_global_widget_styles(),
        build_button_styles(),
        build_panel_styles(),
        build_feature_styles(),
    ])
