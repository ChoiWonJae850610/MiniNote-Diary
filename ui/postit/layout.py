from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QToolButton, QVBoxLayout, QWidget

from ui.theme import THEME, title_badge_style

POSTIT_TAB_INSET_LEFT = THEME.filter_panel_margin_h + 4
POSTIT_TAB_OVERLAP = -12
POSTIT_HEADER_HEIGHT = THEME.icon_button_size
POSTIT_BODY_HEIGHT = THEME.postit_bar_max_height
POSTIT_CARD_HEIGHT = POSTIT_BODY_HEIGHT
POSTIT_FOOTER_HEIGHT = THEME.section_badge_height
POSTIT_FOOTER_GAP = THEME.top_button_spacing
POSTIT_EXTERNAL_ROW_GAP = THEME.top_button_spacing
POSTIT_EXTERNAL_ROW_GAP_TIGHT = 0
POSTIT_TAB_MIN_WIDTH = 0
POSTIT_TAB_PADDING_X = 10
POSTIT_ROW_ACTION_GAP = 6
POSTIT_TAB_GROUP_GAP = 0

POSTIT_INNER_SIDE_PADDING = 14
POSTIT_BODY_TOP_PADDING = 4
POSTIT_STACK_SECTION_OVERLAP = POSTIT_TAB_OVERLAP
POSTIT_INNER_TOP_PADDING = POSTIT_BODY_TOP_PADDING
POSTIT_INNER_BOTTOM_PADDING = 4
POSTIT_SECTION_SPACING = 2
POSTIT_GRID_H_SPACING = 8
POSTIT_GRID_V_SPACING = 4
POSTIT_ROW_GAP = POSTIT_GRID_V_SPACING
POSTIT_UNIFORM_ROW_SPACING = POSTIT_ROW_GAP
POSTIT_MEMO_BODY_HEIGHT = 320


def postit_section_height(*, body_height: int, has_footer: bool = False) -> int:
    total = POSTIT_HEADER_HEIGHT + POSTIT_TAB_OVERLAP + body_height
    if has_footer:
        total += POSTIT_FOOTER_GAP + POSTIT_FOOTER_HEIGHT
    return total


POSTIT_WRAP_HEIGHT = postit_section_height(body_height=POSTIT_BODY_HEIGHT)
POSTIT_WRAP_HEIGHT_WITH_FOOTER = postit_section_height(body_height=POSTIT_BODY_HEIGHT, has_footer=True)


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
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addStretch(1)
