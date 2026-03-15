from __future__ import annotations

from ui.theme_tokens import THEME
from ui.theme_app_stylesheet import build_app_stylesheet
from ui.theme_widget_styles import *


def card_colors(kind: str) -> tuple[str, str]:
    mapping = {
        "basic": (THEME.color_basic_bg, THEME.color_basic_border),
        "fabric": (THEME.color_fabric_bg, THEME.color_fabric_border),
        "trim": (THEME.color_trim_bg, THEME.color_trim_border),
        "change": (THEME.color_change_bg, THEME.color_change_border),
    }
    return mapping.get(kind, (THEME.color_basic_bg, THEME.color_basic_border))


__all__ = [name for name in globals() if not name.startswith("_")]
