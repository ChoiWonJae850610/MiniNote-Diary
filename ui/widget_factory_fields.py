from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton, QTextEdit

from ui.theme import THEME, combo_box_style, display_field_style, input_line_edit_style, plain_text_edit_style
from ui.widget_factory_buttons import refresh_style


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
