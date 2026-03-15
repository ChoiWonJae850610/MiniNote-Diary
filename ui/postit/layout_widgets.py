from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QStackedLayout, QToolButton, QVBoxLayout, QWidget

from ui.postit.layout_constants import (
    POSTIT_BODY_HEIGHT,
    POSTIT_EXTERNAL_ROW_GAP,
    POSTIT_FOOTER_GAP,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_HEADER_HEIGHT,
    POSTIT_STANDARD_EXTERNAL_ROW_GAP,
    POSTIT_TAB_GROUP_GAP,
    POSTIT_ZERO_MARGIN,
    POSTIT_ZERO_SPACING,
    POSTIT_ZERO_STRETCH,
    POSTIT_SINGLE_STRETCH,
    POSTIT_TAB_INSET_LEFT,
    POSTIT_TAB_OVERLAP,
)
from ui.postit.layout import folder_tab_style, postit_section_height
from ui.theme import THEME, title_badge_style


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
        root.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
        root.setSpacing(spacing)
        if header_alignment is None:
            root.addWidget(header_widget)
        else:
            root.addWidget(header_widget, POSTIT_ZERO_STRETCH, header_alignment)
        root.addWidget(body_widget, POSTIT_ZERO_STRETCH)
        if footer_widget is not None:
            root.addSpacing(footer_gap)
            root.addWidget(footer_widget, POSTIT_ZERO_STRETCH)

        height = body_height if body_height is not None else body_widget.sizeHint().height()
        if height > 0:
            self.setFixedHeight(postit_section_height(body_height=height, has_footer=footer_widget is not None))


class FooterSpacer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(POSTIT_FOOTER_HEIGHT)


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
        root.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
        root.setSpacing(external_row_gap)
        root.addWidget(self.section_wrap, POSTIT_ZERO_STRETCH)
        root.addWidget(self.external_row_widget, POSTIT_ZERO_STRETCH)

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
        root.addStretch(POSTIT_SINGLE_STRETCH)

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


def make_postit_footer_spacer(parent=None) -> FooterSpacer:
    return FooterSpacer(parent)


def make_postit_stack_host(*, parent=None, height: int = POSTIT_BODY_HEIGHT) -> tuple[QWidget, QStackedLayout]:
    host = QWidget(parent)
    host.setFixedHeight(height)
    stack = QStackedLayout(host)
    stack.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
    stack.setSpacing(POSTIT_ZERO_SPACING)
    return host, stack


def make_postit_pager_host(*, parent=None) -> tuple[QWidget, QStackedLayout]:
    host = QWidget(parent)
    host.setFixedHeight(POSTIT_FOOTER_HEIGHT)
    stack = QStackedLayout(host)
    stack.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
    stack.setSpacing(POSTIT_ZERO_SPACING)
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
) -> PostItSectionColumn:
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
