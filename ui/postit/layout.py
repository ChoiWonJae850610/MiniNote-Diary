from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QStackedLayout, QToolButton, QVBoxLayout, QWidget

from ui.theme import THEME, title_badge_style


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

    @property
    def wrap_height(self) -> int:
        return postit_section_height(body_height=self.body_height)

    @property
    def wrap_height_with_footer(self) -> int:
        return postit_section_height(body_height=self.body_height, has_footer=True)


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


def postit_section_height(*, body_height: int, has_footer: bool = False) -> int:
    total = POSTIT_HEADER_HEIGHT + POSTIT_TAB_OVERLAP + body_height
    if has_footer:
        total += POSTIT_FOOTER_GAP + POSTIT_FOOTER_HEIGHT
    return total


POSTIT_WRAP_HEIGHT = POSTIT_METRICS.wrap_height
POSTIT_WRAP_HEIGHT_WITH_FOOTER = POSTIT_METRICS.wrap_height_with_footer


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


POSTIT_STANDARD_EXTERNAL_ROW_GAP = POSTIT_EXTERNAL_ROW_GAP_TIGHT
POSTIT_STANDARD_SECTION_SPACING = POSTIT_TAB_OVERLAP
POSTIT_STANDARD_BODY_HEIGHT = POSTIT_BODY_HEIGHT


def make_postit_footer_spacer(parent=None) -> "FooterSpacer":
    return FooterSpacer(parent)


def make_postit_stack_host(*, parent=None, height: int = POSTIT_STANDARD_BODY_HEIGHT) -> tuple[QWidget, QStackedLayout]:
    host = QWidget(parent)
    host.setFixedHeight(height)
    stack = QStackedLayout(host)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setSpacing(0)
    return host, stack


def make_postit_pager_host(*, parent=None) -> tuple[QWidget, QStackedLayout]:
    host = QWidget(parent)
    host.setFixedHeight(POSTIT_FOOTER_HEIGHT)
    stack = QStackedLayout(host)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setSpacing(0)
    return host, stack


def make_static_postit_column(
    title: str,
    body_widget: QWidget,
    *,
    parent=None,
    body_height: int = POSTIT_BODY_HEIGHT,
    footer_widget: QWidget | None = None,
    external_row_widget: QWidget | None = None,
    spacing: int = POSTIT_TAB_OVERLAP,
    external_row_gap: int = POSTIT_STANDARD_EXTERNAL_ROW_GAP,
) -> "PostItSectionColumn":
    resolved_footer = footer_widget if footer_widget is not None else make_postit_footer_spacer(parent)
    return PostItSectionColumn(
        FolderTabHeader(title, parent),
        body_widget,
        parent=parent,
        body_height=body_height,
        footer_widget=resolved_footer,
        external_row_widget=external_row_widget,
        spacing=spacing,
        external_row_gap=external_row_gap,
    )


class SectionContainer(QWidget):
    def __init__(
        self,
        header_widget: QWidget,
        body_widget: QWidget,
        *,
        parent=None,
        spacing: int = POSTIT_TAB_OVERLAP,
        header_alignment=Qt.AlignLeft,
        footer_widget: QWidget | None = None,
        footer_gap: int = POSTIT_FOOTER_GAP,
        body_height: int | None = None,
    ):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(spacing)
        if header_alignment is None:
            root.addWidget(header_widget)
        else:
            root.addWidget(header_widget, 0, header_alignment)
        root.addWidget(body_widget, 0)
        if footer_widget is not None:
            root.addSpacing(footer_gap)
            root.addWidget(footer_widget, 0)

        height = body_height if body_height is not None else body_widget.sizeHint().height()
        if height > 0:
            self.setFixedHeight(postit_section_height(body_height=height, has_footer=footer_widget is not None))


class PostItSectionColumn(QWidget):
    def __init__(
        self,
        header_widget: QWidget,
        body_widget: QWidget,
        *,
        parent=None,
        body_height: int | None = None,
        footer_widget: QWidget | None = None,
        external_row_widget: QWidget | None = None,
        spacing: int = POSTIT_TAB_OVERLAP,
        external_row_gap: int = POSTIT_EXTERNAL_ROW_GAP,
    ):
        super().__init__(parent)
        self.section_wrap = SectionContainer(
            header_widget,
            body_widget,
            parent=self,
            spacing=spacing,
            header_alignment=None,
            footer_widget=footer_widget,
            body_height=body_height,
        )
        self.section_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.external_row_widget = external_row_widget or FooterSpacer(self)
        self.external_row_widget.setParent(self)
        self.external_row_widget.setFixedHeight(POSTIT_FOOTER_HEIGHT)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(external_row_gap)
        root.addWidget(self.section_wrap, 0)
        root.addWidget(self.external_row_widget, 0)

        has_footer = footer_widget is not None
        section_height = postit_section_height(body_height=body_height or body_widget.sizeHint().height(), has_footer=has_footer)
        self.setFixedHeight(section_height + external_row_gap + POSTIT_FOOTER_HEIGHT)


class SectionTitleBadge(QLabel):
    def __init__(self, text: str, parent=None, **style_kwargs):
        super().__init__(text, parent)
        self.setFixedHeight(THEME.section_badge_height)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet(title_badge_style(**style_kwargs))


class PostItTabButton(QToolButton):
    def __init__(self, text: str, parent=None, *, active: bool = True):
        super().__init__(parent)
        self.setText(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCheckable(False)
        self.setAutoRaise(False)
        self.setFixedHeight(POSTIT_HEADER_HEIGHT)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet(folder_tab_style(active=active, selector="QToolButton"))

    def set_active(self, active: bool):
        self.setStyleSheet(folder_tab_style(active=active, selector="QToolButton"))


class FolderTabHeader(QWidget):
    def __init__(self, tabs, parent=None, *, active_key: str | None = None, interactive: bool = True):
        super().__init__(parent)
        if isinstance(tabs, str):
            tabs = [(tabs, tabs)]
            interactive = False
        self._buttons: dict[str, PostItTabButton] = {}
        self._interactive = interactive

        root = QHBoxLayout(self)
        root.setContentsMargins(POSTIT_TAB_INSET_LEFT, 0, 0, 0)
        root.setSpacing(POSTIT_TAB_GROUP_GAP)

        first_key = tabs[0][0] if tabs else None
        self._active_key = active_key or first_key

        for key, text in tabs:
            button = PostItTabButton(text, self, active=(key == self._active_key))
            button.setCheckable(True)
            button.setChecked(key == self._active_key)
            button.setEnabled(interactive)
            if not interactive:
                button.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self._buttons[key] = button
            root.addWidget(button, 0, Qt.AlignLeft)
        root.addStretch(1)

    def button(self, key: str) -> PostItTabButton | None:
        return self._buttons.get(key)

    def keys(self) -> list[str]:
        return list(self._buttons.keys())

    def set_active_tab(self, key: str):
        self._active_key = key
        for button_key, button in self._buttons.items():
            active = button_key == key
            button.setChecked(active)
            button.set_active(active)


class FooterSpacer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(POSTIT_FOOTER_HEIGHT)
