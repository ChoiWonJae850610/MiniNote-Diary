from __future__ import annotations

from ui.postit import layout_constants as const
from ui.theme import THEME
from ui.postit.layout_helpers import postit_column_height

# Public constant aliases kept here as a single compatibility surface for post-it layout consumers.
POSTIT_BASIC_CARD_MIN_WIDTH = const.POSTIT_BASIC_CARD_MIN_WIDTH
POSTIT_BODY_HEIGHT = const.POSTIT_BODY_HEIGHT
POSTIT_BODY_TOP_PADDING = const.POSTIT_BODY_TOP_PADDING
POSTIT_CALENDAR_ICON_SIZE = const.POSTIT_CALENDAR_ICON_SIZE
POSTIT_CALENDAR_POPUP_OFFSET_Y = const.POSTIT_CALENDAR_POPUP_OFFSET_Y
POSTIT_CARD_HEIGHT = const.POSTIT_CARD_HEIGHT
POSTIT_CHANGE_NOTE_MIN_WIDTH = const.POSTIT_CHANGE_NOTE_MIN_WIDTH
POSTIT_DELETE_BUTTON_MARGIN_RIGHT = const.POSTIT_DELETE_BUTTON_MARGIN_RIGHT
POSTIT_DELETE_BUTTON_MARGIN_TOP = const.POSTIT_DELETE_BUTTON_MARGIN_TOP
POSTIT_EXTERNAL_ROW_GAP = const.POSTIT_EXTERNAL_ROW_GAP
POSTIT_EXTERNAL_ROW_GAP_TIGHT = const.POSTIT_EXTERNAL_ROW_GAP_TIGHT
POSTIT_FOOTER_GAP = const.POSTIT_FOOTER_GAP
POSTIT_FOOTER_HEIGHT = const.POSTIT_FOOTER_HEIGHT
POSTIT_GRID_H_SPACING = const.POSTIT_GRID_H_SPACING
POSTIT_GRID_V_SPACING = const.POSTIT_GRID_V_SPACING
POSTIT_HEADER_HEIGHT = const.POSTIT_HEADER_HEIGHT
POSTIT_INNER_BOTTOM_PADDING = const.POSTIT_INNER_BOTTOM_PADDING
POSTIT_INNER_SIDE_PADDING = const.POSTIT_INNER_SIDE_PADDING
POSTIT_INNER_TOP_PADDING = const.POSTIT_INNER_TOP_PADDING
POSTIT_MATERIAL_CARD_MIN_WIDTH = const.POSTIT_MATERIAL_CARD_MIN_WIDTH
POSTIT_MEMO_BODY_HEIGHT = const.POSTIT_MEMO_BODY_HEIGHT
POSTIT_PARTNER_BAR_BASIC_STRETCH = const.POSTIT_PARTNER_BAR_BASIC_STRETCH
POSTIT_PARTNER_BAR_MATERIAL_STRETCH = const.POSTIT_PARTNER_BAR_MATERIAL_STRETCH
POSTIT_PARTNER_LINK_ICON_SIZE = const.POSTIT_PARTNER_LINK_ICON_SIZE
POSTIT_POPUP_MARGIN = const.POSTIT_POPUP_MARGIN
POSTIT_ROW_ACTION_GAP = const.POSTIT_ROW_ACTION_GAP
POSTIT_ROW_GAP = const.POSTIT_ROW_GAP
POSTIT_SECTION_SPACING = const.POSTIT_SECTION_SPACING
POSTIT_SINGLE_STRETCH = const.POSTIT_SINGLE_STRETCH
POSTIT_STACK_SECTION_OVERLAP = const.POSTIT_STACK_SECTION_OVERLAP
POSTIT_STANDARD_EXTERNAL_ROW_GAP = const.POSTIT_STANDARD_EXTERNAL_ROW_GAP
POSTIT_TAB_GROUP_GAP = const.POSTIT_TAB_GROUP_GAP
POSTIT_TAB_INSET_LEFT = const.POSTIT_TAB_INSET_LEFT
POSTIT_TAB_MIN_WIDTH = const.POSTIT_TAB_MIN_WIDTH
POSTIT_TAB_OVERLAP = const.POSTIT_TAB_OVERLAP
POSTIT_TAB_PADDING_X = const.POSTIT_TAB_PADDING_X
POSTIT_UNIFORM_ROW_SPACING = const.POSTIT_UNIFORM_ROW_SPACING
POSTIT_UNIT_DOWN_ICON_SIZE = const.POSTIT_UNIT_DOWN_ICON_SIZE
POSTIT_UNIT_MENU_CLEAR_LABEL = const.POSTIT_UNIT_MENU_CLEAR_LABEL
POSTIT_UNIT_MENU_EMPTY_LABEL = const.POSTIT_UNIT_MENU_EMPTY_LABEL
POSTIT_ZERO_MARGIN = const.POSTIT_ZERO_MARGIN
POSTIT_ZERO_SPACING = const.POSTIT_ZERO_SPACING
POSTIT_ZERO_STRETCH = const.POSTIT_ZERO_STRETCH

POSTIT_DATE_MIN_WIDTH_EXTRA = 8


def postit_section_height(*, body_height: int, has_footer: bool = False) -> int:
    total = POSTIT_HEADER_HEIGHT + POSTIT_TAB_OVERLAP + body_height
    if has_footer:
        total += THEME.top_button_spacing + POSTIT_FOOTER_HEIGHT
    return total


def postit_wrap_height(*, body_height: int = POSTIT_BODY_HEIGHT, has_footer: bool = False) -> int:
    return postit_section_height(body_height=body_height, has_footer=has_footer)


def embedded_tab_style(*, active: bool = True, selector: str = 'QToolButton') -> str:
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
    if active:
        return base + f"background:{t.color_surface};" + f"color:{t.color_text};" + '}'
    return base + f"background:{t.color_surface_muted};" + f"color:{t.color_text_soft};" + '}'


def folder_tab_style(*, active: bool = True, selector: str = 'QToolButton') -> str:
    return embedded_tab_style(active=active, selector=selector)


class PostItLayout:
    DATE_MIN_WIDTH_EXTRA = POSTIT_DATE_MIN_WIDTH_EXTRA
    CALENDAR_ICON_SIZE = POSTIT_CALENDAR_ICON_SIZE
    PARTNER_LINK_ICON_SIZE = POSTIT_PARTNER_LINK_ICON_SIZE
    UNIT_ICON_SIZE = POSTIT_UNIT_DOWN_ICON_SIZE
    CALENDAR_POPUP_OFFSET_Y = POSTIT_CALENDAR_POPUP_OFFSET_Y
    DELETE_BUTTON_MARGIN_RIGHT = POSTIT_DELETE_BUTTON_MARGIN_RIGHT
    DELETE_BUTTON_MARGIN_TOP = POSTIT_DELETE_BUTTON_MARGIN_TOP


from ui.postit.layout_widgets import (  # noqa: E402
    FolderTabHeader,
    FooterSpacer,
    PostItSectionColumn,
    PostItTabButton,
    SectionContainer,
    SectionTitleBadge,
    DEFAULT_SECTION_LAYOUT,
    SectionLayoutSpec,
    make_postit_footer_spacer,
    make_postit_pager_host,
    make_postit_section_column,
    make_postit_stack_host,
    make_static_postit_column,
)

POSTIT_WRAP_HEIGHT = postit_wrap_height(body_height=POSTIT_BODY_HEIGHT)
POSTIT_WRAP_HEIGHT_WITH_FOOTER = postit_wrap_height(body_height=POSTIT_BODY_HEIGHT, has_footer=True)

_CONSTANT_EXPORTS = [
    'POSTIT_BASIC_CARD_MIN_WIDTH',
    'POSTIT_BODY_HEIGHT',
    'POSTIT_BODY_TOP_PADDING',
    'POSTIT_CALENDAR_ICON_SIZE',
    'POSTIT_CALENDAR_POPUP_OFFSET_Y',
    'POSTIT_CARD_HEIGHT',
    'POSTIT_CHANGE_NOTE_MIN_WIDTH',
    'POSTIT_DATE_MIN_WIDTH_EXTRA',
    'POSTIT_DELETE_BUTTON_MARGIN_RIGHT',
    'POSTIT_DELETE_BUTTON_MARGIN_TOP',
    'POSTIT_EXTERNAL_ROW_GAP',
    'POSTIT_EXTERNAL_ROW_GAP_TIGHT',
    'POSTIT_FOOTER_GAP',
    'POSTIT_FOOTER_HEIGHT',
    'POSTIT_GRID_H_SPACING',
    'POSTIT_GRID_V_SPACING',
    'POSTIT_HEADER_HEIGHT',
    'POSTIT_INNER_BOTTOM_PADDING',
    'POSTIT_INNER_SIDE_PADDING',
    'POSTIT_INNER_TOP_PADDING',
    'POSTIT_MATERIAL_CARD_MIN_WIDTH',
    'POSTIT_MEMO_BODY_HEIGHT',
    'POSTIT_PARTNER_BAR_BASIC_STRETCH',
    'POSTIT_PARTNER_BAR_MATERIAL_STRETCH',
    'POSTIT_PARTNER_LINK_ICON_SIZE',
    'POSTIT_POPUP_MARGIN',
    'POSTIT_ROW_ACTION_GAP',
    'POSTIT_ROW_GAP',
    'POSTIT_SECTION_SPACING',
    'POSTIT_SINGLE_STRETCH',
    'POSTIT_STACK_SECTION_OVERLAP',
    'POSTIT_STANDARD_EXTERNAL_ROW_GAP',
    'POSTIT_TAB_GROUP_GAP',
    'POSTIT_TAB_INSET_LEFT',
    'POSTIT_TAB_MIN_WIDTH',
    'POSTIT_TAB_OVERLAP',
    'POSTIT_TAB_PADDING_X',
    'POSTIT_UNIFORM_ROW_SPACING',
    'POSTIT_UNIT_DOWN_ICON_SIZE',
    'POSTIT_UNIT_MENU_CLEAR_LABEL',
    'POSTIT_UNIT_MENU_EMPTY_LABEL',
    'POSTIT_WRAP_HEIGHT',
    'POSTIT_WRAP_HEIGHT_WITH_FOOTER',
    'POSTIT_ZERO_MARGIN',
    'POSTIT_ZERO_SPACING',
    'POSTIT_ZERO_STRETCH',
]

_WIDGET_EXPORTS = [
    'postit_column_height',
    'DEFAULT_SECTION_LAYOUT',
    'FolderTabHeader',
    'FooterSpacer',
    'PostItLayout',
    'PostItSectionColumn',
    'PostItTabButton',
    'SectionContainer',
    'SectionLayoutSpec',
    'SectionTitleBadge',
    'embedded_tab_style',
    'folder_tab_style',
    'make_postit_footer_spacer',
    'make_postit_pager_host',
    'make_postit_section_column',
    'make_postit_stack_host',
    'make_static_postit_column',
    'postit_section_height',
    'postit_wrap_height',
]

__all__ = _CONSTANT_EXPORTS + _WIDGET_EXPORTS
