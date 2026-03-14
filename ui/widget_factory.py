from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QCursor, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget

from ui.messages import Symbols
from ui.ui_metrics import CommonSymbolsLayout
from ui.theme import (
    THEME,
    combo_box_style,
    display_field_style,
    icon_button_override,
    input_line_edit_style,
    plain_text_edit_style,
)



def refresh_style(widget: QWidget) -> QWidget:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    return widget


def set_widget_tooltip(widget: QWidget, tooltip: str | None) -> QWidget:
    if tooltip:
        widget.setToolTip(tooltip.strip())
        widget.setToolTipDuration(3000)
    else:
        widget.setToolTip("")
    return refresh_style(widget)


def apply_button_role_style(button: QPushButton, *, object_name: str | None = None, extra_style: str = "",) -> QPushButton:
    if object_name:
        button.setObjectName(object_name)

    if extra_style:
        button.setStyleSheet(extra_style)

    # style refresh
    return refresh_style(button)

def apply_button_metrics(button: QPushButton, *, width: int | None = None, height: int | None = None, font_px: int | None = None, bold: bool = True, point_cursor: bool = True) -> QPushButton:
    if width is not None and height is not None:
        button.setFixedSize(width, height)
    elif width is not None:
        button.setFixedWidth(width)
    elif height is not None:
        button.setFixedHeight(height)

    font = button.font()
    if font_px is not None:
        font.setPixelSize(font_px)
    font.setBold(bold)
    button.setFont(font)

    if point_cursor:
        button.setCursor(QCursor(Qt.PointingHandCursor))
    return button


def make_button(text: str, parent=None, *, width: int | None = None, height: int | None = None, object_name: str | None = None, font_px: int | None = None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_button_metrics(button, width=width, height=height, font_px=font_px)
    apply_button_role_style(button, object_name=object_name)
    return button


def apply_icon_button_metrics(button: QPushButton, *, font_px: int, object_name: str | None = None, tooltip: str | None = None, extra_style: str = "") -> QPushButton:
    apply_button_metrics(
        button,
        width=THEME.icon_button_size,
        height=THEME.icon_button_size,
        font_px=font_px,
        bold=True,
        point_cursor=True,
    )
    button.setContentsMargins(0, 0, 0, 0)
    apply_button_role_style(button, object_name=object_name)
    set_widget_tooltip(button, tooltip)
    button.setStyleSheet(
        icon_button_override(font_px)
        + "QPushButton{text-align:center;padding:0;margin:0;}"
        + extra_style
    )
    return refresh_style(button)


def make_icon_button(*, parent=None, object_name: str, tooltip: str = "", icon: QIcon | None = None, text: str = "", font_px: int | None = None, icon_size: int | None = None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_icon_button_metrics(
        button,
        font_px=font_px or (THEME.icon_button_font_px + 2),
        object_name=object_name,
        tooltip=tooltip,
    )
    if icon is not None and not icon.isNull():
        button.setText("")
        button.setIcon(icon)
        size = icon_size or THEME.icon_size_md
        button.setIconSize(button.iconSize().__class__(size, size))
    return button


def build_centered_glyph_icon(glyph: str, *, font_px: int, color: str, canvas_size: int | None = None) -> QIcon:
    size = canvas_size or THEME.icon_button_size
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)

    font = QFont()
    font.setPixelSize(font_px)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(color))
    painter.drawText(QRectF(0, 0, size, size), Qt.AlignCenter, glyph)
    painter.end()
    return QIcon(pixmap)


def apply_glyph_icon(button: QPushButton, glyph: str, *, font_px: int, color: str) -> QPushButton:
    button.setText("")
    button.setIcon(build_centered_glyph_icon(glyph, font_px=font_px, color=color))
    button.setIconSize(button.size())
    return button


def make_dialog_button(text: str, parent=None, *, role: str | None = None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_button_metrics(button, height=THEME.dialog_button_height)
    if role == "confirm":
        apply_button_role_style(button, object_name="dialogConfirm")
    elif role == "cancel":
        apply_button_role_style(button, object_name="dialogCancel")
    elif role == "close":
        apply_button_role_style(button, object_name="dialogClose")
    return button


def make_dialog_button_row(buttons: Iterable[QPushButton], *, stretch: bool = True, spacing: int | None = None) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(THEME.row_spacing if spacing is None else spacing)
    if stretch:
        row.addStretch(1)
    for button in buttons:
        row.addWidget(button)
    return row


def make_inline_icon_button(*, parent=None, tooltip: str = '', icon: QIcon | None = None, size: int | None = None) -> QPushButton:
    button = QPushButton(parent)
    button_size = size or THEME.field_height
    apply_button_metrics(button, width=button_size, height=button_size, font_px=THEME.base_font_px, bold=False, point_cursor=True)
    set_widget_tooltip(button, tooltip)
    button.setContentsMargins(0, 0, 0, 0)
    if icon is not None and not icon.isNull():
        button.setIcon(icon)
        icon_dim = max(12, button_size - 10)
        button.setIconSize(button.iconSize().__class__(icon_dim, icon_dim))
    apply_button_role_style(button, object_name='iconAction')
    button.setStyleSheet(
        icon_button_override(THEME.base_font_px)
        + 'QPushButton{text-align:center;padding:0;margin:0;}'
    )
    return refresh_style(button)


def make_panel_frame(parent=None, *, compact: bool = False, object_name: str | None = None) -> QFrame:
    frame = QFrame(parent)
    frame.setObjectName(object_name or ('panelFrameCompact' if compact else 'panelFrame'))
    return refresh_style(frame)


def make_page_title_label(text: str, parent=None) -> QLabel:
    label = QLabel(text, parent)
    label.setObjectName('pageTitle')
    return refresh_style(label)


def make_panel_title_label(text: str, parent=None) -> QLabel:
    label = QLabel(text, parent)
    label.setObjectName('panelTitle')
    return refresh_style(label)


def make_hint_label(text: str, parent=None, *, word_wrap: bool = True) -> QLabel:
    label = QLabel(text, parent)
    label.setWordWrap(word_wrap)
    label.setObjectName('hintLabel')
    return refresh_style(label)


def make_value_label(text: str = '-', parent=None, *, min_height: int = 32, padding: int = 10) -> QLabel:
    label = QLabel(text, parent)
    label.setMinimumHeight(min_height)
    label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    label.setObjectName('displayField')
    if padding != 10:
        label.setStyleSheet(display_field_style(padding))
    return refresh_style(label)


def make_nav_button(*, parent=None, tooltip: str = '') -> QPushButton:
    button = QPushButton(Symbols.BACK, parent)
    return apply_icon_button_metrics(button, font_px=CommonSymbolsLayout.NAV_BUTTON_FONT_PX, object_name='navButton', tooltip=tooltip)


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


def make_field_label(text: str, parent=None, *, strong: bool = False) -> QLabel:
    label = QLabel(text, parent)
    label.setObjectName('strongFieldLabel' if strong else 'fieldLabel')
    return refresh_style(label)


def make_meta_label(text: str, parent=None, *, word_wrap: bool = True) -> QLabel:
    label = QLabel(text, parent)
    label.setWordWrap(word_wrap)
    label.setObjectName('metaLabel')
    return refresh_style(label)


def make_section_title_label(text: str, parent=None) -> QLabel:
    label = QLabel(text, parent)
    label.setObjectName('sectionTitle')
    return refresh_style(label)


def make_input_line_edit(parent=None, *, placeholder: str = '') -> QLineEdit:
    edit = QLineEdit(parent)
    if placeholder:
        edit.setPlaceholderText(placeholder)
    edit.setStyleSheet(input_line_edit_style())
    return edit


def make_combo_box(parent=None) -> QComboBox:
    combo = QComboBox(parent)
    combo.setStyleSheet(combo_box_style())
    return combo


def make_plain_text_editor(parent=None, *, read_only: bool = False, min_height: int | None = None) -> QTextEdit:
    editor = QTextEdit(parent)
    editor.setReadOnly(read_only)
    if min_height is not None:
        editor.setMinimumHeight(min_height)
    editor.setStyleSheet(plain_text_edit_style())
    return editor
