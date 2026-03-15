from __future__ import annotations

from dataclasses import dataclass

from ui.theme import THEME


@dataclass(frozen=True)
class PostItMetrics:
    tab_inset_left: int = THEME.filter_panel_margin_h + 4
    tab_overlap: int = -12
    header_height: int = THEME.icon_button_size
    body_height: int = THEME.postit_bar_max_height
    footer_height: int = THEME.section_badge_height
    footer_gap: int = THEME.top_button_spacing
    external_row_gap: int = THEME.top_button_spacing
    external_row_gap_tight: int = 0
    tab_min_width: int = 0
    tab_padding_x: int = 10
    row_action_gap: int = 6
    tab_group_gap: int = 0
    inner_side_padding: int = 14
    body_top_padding: int = 4
    inner_bottom_padding: int = 4
    section_spacing: int = 2
    grid_h_spacing: int = 8
    grid_v_spacing: int = 4
    memo_body_height: int = 292
    basic_card_min_width: int = 320
    material_card_min_width: int = 320
    change_note_min_width: int = 340
    delete_button_margin_top: int = 6
    delete_button_margin_right: int = 4
    calendar_popup_offset_y: int = 4
    calendar_icon_size: int = 16
    partner_link_icon_size: int = 14
    unit_down_icon_size: int = 12
    unit_menu_empty_label: str = "(단위 목록 없음)"
    unit_menu_clear_label: str = "(비움)"

    @property
    def card_height(self) -> int:
        return self.body_height

    @property
    def stack_section_overlap(self) -> int:
        return self.tab_overlap

    @property
    def inner_top_padding(self) -> int:
        return self.body_top_padding

    @property
    def row_gap(self) -> int:
        return self.grid_v_spacing

    @property
    def uniform_row_spacing(self) -> int:
        return self.row_gap


POSTIT_METRICS = PostItMetrics()
POSTIT_TAB_INSET_LEFT = POSTIT_METRICS.tab_inset_left
POSTIT_TAB_OVERLAP = POSTIT_METRICS.tab_overlap
POSTIT_HEADER_HEIGHT = POSTIT_METRICS.header_height
POSTIT_BODY_HEIGHT = POSTIT_METRICS.body_height
POSTIT_CARD_HEIGHT = POSTIT_METRICS.card_height
POSTIT_FOOTER_HEIGHT = POSTIT_METRICS.footer_height
POSTIT_FOOTER_GAP = POSTIT_METRICS.footer_gap
POSTIT_EXTERNAL_ROW_GAP = POSTIT_METRICS.external_row_gap
POSTIT_EXTERNAL_ROW_GAP_TIGHT = POSTIT_METRICS.external_row_gap_tight
POSTIT_TAB_MIN_WIDTH = POSTIT_METRICS.tab_min_width
POSTIT_TAB_PADDING_X = POSTIT_METRICS.tab_padding_x
POSTIT_ROW_ACTION_GAP = POSTIT_METRICS.row_action_gap
POSTIT_TAB_GROUP_GAP = POSTIT_METRICS.tab_group_gap
POSTIT_INNER_SIDE_PADDING = POSTIT_METRICS.inner_side_padding
POSTIT_BODY_TOP_PADDING = POSTIT_METRICS.body_top_padding
POSTIT_STACK_SECTION_OVERLAP = POSTIT_METRICS.stack_section_overlap
POSTIT_INNER_TOP_PADDING = POSTIT_METRICS.inner_top_padding
POSTIT_INNER_BOTTOM_PADDING = POSTIT_METRICS.inner_bottom_padding
POSTIT_SECTION_SPACING = POSTIT_METRICS.section_spacing
POSTIT_GRID_H_SPACING = POSTIT_METRICS.grid_h_spacing
POSTIT_GRID_V_SPACING = POSTIT_METRICS.grid_v_spacing
POSTIT_ROW_GAP = POSTIT_METRICS.row_gap
POSTIT_UNIFORM_ROW_SPACING = POSTIT_METRICS.uniform_row_spacing
POSTIT_MEMO_BODY_HEIGHT = POSTIT_METRICS.memo_body_height
POSTIT_BASIC_CARD_MIN_WIDTH = POSTIT_METRICS.basic_card_min_width
POSTIT_MATERIAL_CARD_MIN_WIDTH = POSTIT_METRICS.material_card_min_width
POSTIT_CHANGE_NOTE_MIN_WIDTH = POSTIT_METRICS.change_note_min_width
POSTIT_DELETE_BUTTON_MARGIN_TOP = POSTIT_METRICS.delete_button_margin_top
POSTIT_DELETE_BUTTON_MARGIN_RIGHT = POSTIT_METRICS.delete_button_margin_right
POSTIT_CALENDAR_POPUP_OFFSET_Y = POSTIT_METRICS.calendar_popup_offset_y
POSTIT_CALENDAR_ICON_SIZE = POSTIT_METRICS.calendar_icon_size
POSTIT_PARTNER_LINK_ICON_SIZE = POSTIT_METRICS.partner_link_icon_size
POSTIT_UNIT_DOWN_ICON_SIZE = POSTIT_METRICS.unit_down_icon_size
POSTIT_UNIT_MENU_EMPTY_LABEL = POSTIT_METRICS.unit_menu_empty_label
POSTIT_UNIT_MENU_CLEAR_LABEL = POSTIT_METRICS.unit_menu_clear_label
POSTIT_STANDARD_EXTERNAL_ROW_GAP = POSTIT_EXTERNAL_ROW_GAP_TIGHT
POSTIT_STANDARD_SECTION_SPACING = POSTIT_TAB_OVERLAP
POSTIT_STANDARD_BODY_HEIGHT = POSTIT_BODY_HEIGHT
