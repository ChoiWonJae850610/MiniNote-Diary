from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QCursor, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from ui.theme import (
    THEME,
    display_field_style,
    hint_label_style,
    icon_button_override,
    panel_frame_style,
    page_title_style,
    panel_title_style,
    tooltip_style_override,
)




def set_widget_tooltip(widget: QWidget, tooltip: str | None) -> QWidget:
    if tooltip:
        widget.setToolTip(tooltip.strip())
        widget.setToolTipDuration(3000)
    else:
        widget.setToolTip("")
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    return widget


def apply_button_role_style(button: QPushButton, *, object_name: str | None = None, extra_style: str = "",) -> QPushButton:
    if object_name:
        button.setObjectName(object_name)

    if extra_style:
        button.setStyleSheet(extra_style)

    # style refresh
    button.style().unpolish(button)
    button.style().polish(button)

    return button

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
        + tooltip_style_override()
        + extra_style
    )
    button.style().unpolish(button)
    button.style().polish(button)
    return button


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
    button.setStyleSheet(
        icon_button_override(THEME.base_font_px)
        + 'QPushButton{text-align:center;padding:0;margin:0;}'
        + tooltip_style_override()
    )
    button.style().unpolish(button)
    button.style().polish(button)
    return button


def make_panel_frame(parent=None, *, compact: bool = False, object_name: str | None = None) -> QFrame:
    frame = QFrame(parent)
    frame.setStyleSheet(panel_frame_style(radius=THEME.panel_radius_sm if compact else THEME.panel_radius))
    if object_name:
        frame.setObjectName(object_name)
    return frame


def make_page_title_label(text: str, parent=None) -> QLabel:
    label = QLabel(text, parent)
    label.setStyleSheet(page_title_style())
    return label


def make_panel_title_label(text: str, parent=None) -> QLabel:
    label = QLabel(text, parent)
    label.setStyleSheet(panel_title_style())
    return label


def make_hint_label(text: str, parent=None, *, word_wrap: bool = True) -> QLabel:
    label = QLabel(text, parent)
    label.setWordWrap(word_wrap)
    label.setStyleSheet(hint_label_style())
    return label


def make_value_label(text: str = '-', parent=None, *, min_height: int = 32, padding: int = 10) -> QLabel:
    label = QLabel(text, parent)
    label.setMinimumHeight(min_height)
    label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    label.setStyleSheet(display_field_style(padding))
    return label
