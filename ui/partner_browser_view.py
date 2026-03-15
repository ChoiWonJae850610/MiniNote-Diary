from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QListWidget, QVBoxLayout, QWidget

from ui.dialog_form_fields import build_dialog_card, build_labeled_value_row, build_section_title, configure_text_field
from ui.layout_metrics import PartnerLayout
from ui.messages import DialogTitles, Labels, Placeholders
from ui.partner_dialog_common import ReadOnlyTypeIndicatorGrid, detail_value_fallback, partner_field_label_style, partner_list_style
from ui.theme import THEME


def build_browser_root(dialog) -> QVBoxLayout:
    root = QVBoxLayout(dialog)
    root.setContentsMargins(*dialog.dialog_margins())
    root.setSpacing(PartnerLayout.TYPE_SECTION_SPACING)

    title = QLabel(DialogTitles.PARTNER_MANAGE, dialog)
    title.setStyleSheet(dialog.title_style())
    root.addWidget(title)

    return root


def build_browser_content(dialog, root: QVBoxLayout) -> None:
    content = QHBoxLayout()
    content.setSpacing(PartnerLayout.CONTENT_SPACING)
    root.addLayout(content, 1)
    content.addWidget(build_left_card(dialog), 1)
    content.addWidget(build_right_card(dialog), 1)


def build_left_card(dialog):
    card, layout = build_dialog_card(dialog, object_name='partnerShell')
    layout.addWidget(build_section_title(DialogTitles.PARTNER_LIST, card))
    dialog.search_edit = configure_text_field(QLineEdit(card))
    dialog.search_edit.setPlaceholderText(Placeholders.PARTNER_SEARCH)
    dialog.search_edit.setFixedHeight(THEME.field_height + PartnerLayout.FIELD_EXTRA_HEIGHT)
    dialog.list_widget = QListWidget(card)
    dialog.list_widget.setObjectName('partnerList')
    dialog.list_widget.setStyleSheet(partner_list_style())
    layout.addWidget(dialog.search_edit)
    layout.addWidget(dialog.list_widget, 1)
    return card


def build_right_card(dialog):
    card, layout = build_dialog_card(dialog, object_name='partnerShell')
    layout.setSpacing(PartnerLayout.DETAIL_CARD_SPACING)
    layout.addWidget(build_section_title(DialogTitles.PARTNER_BASIC_INFO, card))

    dialog.detail_name = make_detail_value_label(dialog, min_height=42)
    dialog.detail_owner = make_detail_value_label(dialog)
    dialog.detail_phone = make_detail_value_label(dialog)
    dialog.detail_address = make_detail_value_label(dialog, min_height=52, wrap=True)
    dialog.detail_memo = make_detail_value_label(dialog, min_height=110, wrap=True, align_top=True)
    dialog.type_caption = QLabel(Labels.PARTNER_TYPE, card)
    dialog.type_caption.setStyleSheet(partner_field_label_style())
    dialog.type_indicator_grid = ReadOnlyTypeIndicatorGrid(card)

    layout.addLayout(build_detail_row(dialog, Labels.PARTNER_NAME, dialog.detail_name))
    layout.addLayout(build_detail_row(dialog, Labels.OWNER_NAME, dialog.detail_owner))
    layout.addLayout(build_detail_row(dialog, Labels.PHONE, dialog.detail_phone))
    layout.addLayout(build_detail_row(dialog, Labels.ADDRESS, dialog.detail_address, top_align=True))
    layout.addLayout(build_detail_row(dialog, Labels.MEMO, dialog.detail_memo, top_align=True))
    layout.addWidget(dialog.type_caption)
    layout.addWidget(dialog.type_indicator_grid)
    layout.addStretch(1)
    return card


def build_detail_row(dialog, label_text: str, value_widget: QWidget, top_align: bool = False):
    return build_labeled_value_row(
        dialog,
        label_text,
        value_widget,
        label_width=PartnerLayout.DETAIL_LABEL_WIDTH,
        spacing=PartnerLayout.CARD_ROW_SPACING,
        label_builder=dialog.make_detail_label,
        top_align=top_align,
    )


def make_detail_value_label(dialog, min_height: int = 34, wrap: bool = False, align_top: bool = False) -> QLabel:
    label = QLabel(detail_value_fallback(), dialog)
    label.setObjectName('partnerValue')
    label.setMinimumHeight(min_height)
    label.setWordWrap(wrap)
    label.setAlignment((Qt.AlignTop | Qt.AlignLeft) if align_top else (Qt.AlignVCenter | Qt.AlignLeft))
    return label


__all__ = [
    'build_browser_content',
    'build_browser_root',
    'build_detail_row',
    'build_left_card',
    'build_right_card',
    'make_detail_value_label',
]
