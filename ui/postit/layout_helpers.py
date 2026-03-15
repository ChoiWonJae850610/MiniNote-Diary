from __future__ import annotations

from ui.postit.layout_constants import (
    POSTIT_BODY_HEIGHT,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_HEADER_HEIGHT,
    POSTIT_TAB_OVERLAP,
    POSTIT_TAB_PADDING_X,
)
from ui.theme import THEME


def postit_section_height(*, body_height: int, has_footer: bool = False) -> int:
    total = POSTIT_HEADER_HEIGHT + POSTIT_TAB_OVERLAP + body_height
    if has_footer:
        total += THEME.top_button_spacing + POSTIT_FOOTER_HEIGHT
    return total


def embedded_tab_style(*, active: bool = True, selector: str = "QToolButton") -> str:
    t = THEME
    base = (
        f"{selector}{{"
        f"padding:0 {POSTIT_TAB_PADDING_X}px;"
        f"max-height:{POSTIT_HEADER_HEIGHT}px;"
        f"min-height:{POSTIT_HEADER_HEIGHT}px;"
        f"border:1px solid {t.color_border};"
        f"border-top-left-radius:{t.control_radius + 6}px;"
        f"border-top-right-radius:{t.control_radius + 6}px;"
        f"border-bottom-left-radius:{t.control_radius + 2}px;"
        f"border-bottom-right-radius:{t.control_radius + 2}px;"
        f"font-size:{t.section_title_font_px}px;"
        "font-weight:700;"
    )
    if active:
        return base + f"background:{t.color_surface};" + f"color:{t.color_text};" + "}"
    return base + f"background:{t.color_surface_muted};" + f"color:{t.color_text_soft};" + "}"


def folder_tab_style(*, active: bool = True, selector: str = "QToolButton") -> str:
    return embedded_tab_style(active=active, selector=selector)


def postit_wrap_height(*, body_height: int = POSTIT_BODY_HEIGHT, has_footer: bool = False) -> int:
    return postit_section_height(body_height=body_height, has_footer=has_footer)
