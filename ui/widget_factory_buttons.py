from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from ui.button_icon_utils import apply_glyph_icon, build_centered_glyph_icon
from ui.button_style_utils import (
    apply_button_metrics,
    apply_button_role_style,
    apply_icon_button_metrics,
    refresh_style,
    set_widget_tooltip,
)
from ui.messages import Symbols
from ui.theme import THEME, icon_button_override
from ui.ui_metrics import CommonSymbolsLayout


def make_button(text: str, parent=None, *, primary: bool = False, width: int | None = None, height: int | None = None) -> QPushButton:
    return make_action_button(text, parent, primary=primary, width=width, height=height)


def make_icon_button(
    *,
    text: str = '',
    parent=None,
    object_name: str = 'iconAction',
    tooltip: str = '',
    font_px: int | None = None,
) -> QPushButton:
    button = QPushButton(text, parent)
    return apply_icon_button_metrics(button, font_px=font_px, object_name=object_name, tooltip=tooltip)


def make_dialog_button(text: str, parent=None, *, role: str | None = None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_button_metrics(button, height=THEME.dialog_button_height)
    role_to_object = {
        'confirm': 'dialogConfirm',
        'cancel': 'dialogCancel',
        'close': 'dialogClose',
    }
    apply_button_role_style(button, object_name=role_to_object.get(role))
    return button


def make_inline_icon_button(*, parent=None, tooltip: str = '', icon: QIcon | None = None, size: int | None = None) -> QPushButton:
    button = QPushButton(parent)
    button_size = size or THEME.field_height
    apply_button_metrics(button, width=button_size, height=button_size, font_px=THEME.base_font_px, bold=False, point_cursor=True)
    set_widget_tooltip(button, tooltip)
    button.setContentsMargins(0, 0, 0, 0)
    if icon is not None and not icon.isNull():
        button.setIcon(icon)
        icon_dim = max(12, button_size - 10)
        button.setIconSize(QSize(icon_dim, icon_dim))
    apply_button_role_style(button, object_name='iconAction')
    button.setStyleSheet(icon_button_override(THEME.base_font_px) + 'QPushButton{text-align:center;padding:0;margin:0;}')
    return refresh_style(button)


def make_nav_button(*, parent=None, tooltip: str = '') -> QPushButton:
    button = QPushButton('', parent)
    apply_icon_button_metrics(
        button,
        font_px=max(THEME.base_font_px, THEME.page_title_font_px - 2),
        object_name='navButton',
        tooltip=tooltip,
        size=THEME.nav_button_size,
    )
    return apply_glyph_icon(button, Symbols.BACK, font_px=max(THEME.base_font_px, THEME.page_title_font_px - 2), color=THEME.color_icon)


def make_toolbar_icon_button(*, parent=None, object_name: str = 'iconAction', tooltip: str = '', icon: QIcon | None = None, font_px: int | None = None) -> QPushButton:
    button = QPushButton('', parent)
    apply_icon_button_metrics(button, font_px=font_px or THEME.icon_button_font_px, object_name=object_name, tooltip=tooltip)
    if icon is not None and not icon.isNull():
        button.setIcon(icon)
    return button


def make_action_button(text: str, parent=None, *, primary: bool = False, width: int | None = None, height: int | None = None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_button_metrics(button, width=width, height=height)
    apply_button_role_style(button, object_name='primaryAction' if primary else None)
    return button


__all__ = [
    'apply_button_metrics',
    'apply_button_role_style',
    'apply_glyph_icon',
    'apply_icon_button_metrics',
    'build_centered_glyph_icon',
    'make_action_button',
    'make_button',
    'make_dialog_button',
    'make_icon_button',
    'make_inline_icon_button',
    'make_nav_button',
    'make_toolbar_icon_button',
    'refresh_style',
    'set_widget_tooltip',
]
