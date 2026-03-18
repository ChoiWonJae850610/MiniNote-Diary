from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from ui.postit.layouting.constants import (
    POSTIT_BODY_HEIGHT,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_HEADER_HEIGHT,
    POSTIT_TAB_OVERLAP,
    POSTIT_TAB_PADDING_X,
)
from ui.theme import THEME


@dataclass(frozen=True)
class PostItColumnMetrics:
    body_height: int
    has_footer: bool
    external_row_gap: int
    external_row_height: int

    @property
    def section_height(self) -> int:
        total = POSTIT_HEADER_HEIGHT + POSTIT_TAB_OVERLAP + self.body_height
        if self.has_footer:
            total += THEME.top_button_spacing + POSTIT_FOOTER_HEIGHT
        return total

    @property
    def column_height(self) -> int:
        return self.section_height + self.external_row_gap + self.external_row_height


def resolve_postit_body_height(*, body_height: int | None = None, body_widget: QWidget | None = None) -> int:
    if body_height is not None:
        return max(0, body_height)
    if body_widget is None:
        return 0
    return max(0, body_widget.sizeHint().height())


def build_postit_column_metrics(
    *,
    body_height: int | None = None,
    body_widget: QWidget | None = None,
    has_footer: bool = True,
    external_row_gap: int | None = None,
    external_row_height: int = POSTIT_FOOTER_HEIGHT,
) -> PostItColumnMetrics:
    resolved_external_row_gap = THEME.top_button_spacing if external_row_gap is None else external_row_gap
    resolved_body_height = resolve_postit_body_height(body_height=body_height, body_widget=body_widget)
    return PostItColumnMetrics(
        body_height=resolved_body_height,
        has_footer=has_footer,
        external_row_gap=resolved_external_row_gap,
        external_row_height=external_row_height,
    )


def postit_section_height(*, body_height: int, has_footer: bool = False) -> int:
    return build_postit_column_metrics(
        body_height=body_height,
        has_footer=has_footer,
        external_row_gap=0,
        external_row_height=0,
    ).section_height



def postit_wrap_height(*, body_height: int = POSTIT_BODY_HEIGHT, has_footer: bool = False) -> int:
    return postit_section_height(body_height=body_height, has_footer=has_footer)


def postit_column_height(
    *,
    body_height: int = POSTIT_BODY_HEIGHT,
    has_footer: bool = True,
    external_row_gap: int | None = None,
    external_row_height: int = POSTIT_FOOTER_HEIGHT,
) -> int:
    return build_postit_column_metrics(
        body_height=body_height,
        has_footer=has_footer,
        external_row_gap=external_row_gap,
        external_row_height=external_row_height,
    ).column_height


def embedded_tab_style(*, active: bool = True, invalid: bool = False, selector: str = 'QToolButton') -> str:
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
        'font-weight:700;'
    )
    border_color = t.color_validation_error if invalid else t.color_border
    base = base.replace(f"border:1px solid {t.color_border};", f"border:1px solid {border_color};")
    if active:
        return base + f"background:{t.color_surface};" + f"color:{t.color_text};" + '}'
    return base + f"background:{t.color_surface_muted};" + f"color:{t.color_text_soft};" + '}'



def folder_tab_style(*, active: bool = True, invalid: bool = False, selector: str = 'QToolButton') -> str:
    return embedded_tab_style(active=active, invalid=invalid, selector=selector)


__all__ = [
    'PostItColumnMetrics',
    'build_postit_column_metrics',
    'embedded_tab_style',
    'folder_tab_style',
    'postit_column_height',
    'postit_section_height',
    'postit_wrap_height',
    'resolve_postit_body_height',
]
