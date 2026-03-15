from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from services.partner_management_service import PartnerManagementService
from ui.dialog_form_fields import build_dialog_card, build_labeled_value_row, build_section_title, configure_text_field
from ui.layout_metrics import PartnerLayout
from ui.messages import Buttons, DialogTitles, Labels, Placeholders, Symbols, Tooltips
from ui.partner_browser_actions import on_add, on_delete, on_edit, on_manage_types
from ui.partner_browser_selection import apply_filter, clear_detail, reload_all, show_partner
from ui.partner_dialog_common import (
    ReadOnlyTypeIndicatorGrid,
    detail_value_fallback,
    partner_detail_value_style,
    partner_field_label_style,
    partner_list_style,
    partner_shell_style,
)
from ui.theme import THEME, dialog_layout_margins, title_label_style
from ui.ui_metrics import CommonSymbolsLayout
from ui.widget_factory import make_dialog_button_row, make_icon_button


class PartnerBrowserDialog(QDialog):
    def __init__(self, project_root, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.partner_service = PartnerManagementService(project_root)
        self.setWindowTitle(DialogTitles.PARTNER_MANAGE)
        self.resize(PartnerLayout.BROWSER_WIDTH, PartnerLayout.BROWSER_HEIGHT)

        self._type_order: list[str] = []
        self._partners = []
        self._filtered = []
        self._current_partner_id = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(*dialog_layout_margins())
        root.setSpacing(PartnerLayout.TYPE_SECTION_SPACING)

        title = QLabel(DialogTitles.PARTNER_MANAGE, self)
        title.setStyleSheet(title_label_style())
        root.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(PartnerLayout.CONTENT_SPACING)
        root.addLayout(content, 1)

        content.addWidget(self._build_left_card(), 1)
        content.addWidget(self._build_right_card(), 1)

        self.btn_type = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.PARTNER_TYPE_MANAGE, text=Symbols.MENU)
        self.btn_add = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.ADD, text=Symbols.ADD)
        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip=Tooltips.EDIT_SAVE, text=Symbols.SAVE)
        self.btn_delete = make_icon_button(parent=self, object_name="iconDanger", tooltip=Tooltips.DELETE, text=Symbols.DELETE)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.CLOSE, text=Symbols.CLOSE)
        root.addLayout(make_dialog_button_row([self.btn_type, self.btn_add, self.btn_save, self.btn_delete, self.btn_close]))

        self.setStyleSheet(self.styleSheet() + partner_shell_style() + partner_detail_value_style())

        self.search_edit.textChanged.connect(lambda text: apply_filter(self, text))
        self.list_widget.currentRowChanged.connect(self._on_current_row_changed)
        self.list_widget.itemDoubleClicked.connect(lambda item: self.on_edit())
        self.btn_add.clicked.connect(self.on_add)
        self.btn_save.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_type.clicked.connect(self.on_manage_types)
        self.btn_close.clicked.connect(self.accept)

        self.reload_all()

    def _build_left_card(self):
        card, layout = build_dialog_card(self, object_name="partnerShell")
        title = build_section_title(DialogTitles.PARTNER_LIST, card)
        self.search_edit = configure_text_field(QLineEdit(card))
        self.search_edit.setPlaceholderText(Placeholders.PARTNER_SEARCH)
        self.search_edit.setFixedHeight(THEME.field_height + PartnerLayout.FIELD_EXTRA_HEIGHT)
        self.list_widget = QListWidget(card)
        self.list_widget.setObjectName("partnerList")
        self.list_widget.setStyleSheet(partner_list_style())
        layout.addWidget(title)
        layout.addWidget(self.search_edit)
        layout.addWidget(self.list_widget, 1)
        return card

    def _build_right_card(self):
        card, layout = build_dialog_card(self, object_name="partnerShell")
        layout.setSpacing(PartnerLayout.DETAIL_CARD_SPACING)
        title = build_section_title(DialogTitles.PARTNER_BASIC_INFO, card)
        self.detail_name = self._detail_value_label(min_height=42)
        self.detail_owner = self._detail_value_label()
        self.detail_phone = self._detail_value_label()
        self.detail_address = self._detail_value_label(min_height=52, wrap=True)
        self.detail_memo = self._detail_value_label(min_height=110, wrap=True, align_top=True)
        self.type_caption = QLabel(Labels.PARTNER_TYPE, card)
        self.type_caption.setStyleSheet(partner_field_label_style())
        self.type_indicator_grid = ReadOnlyTypeIndicatorGrid(card)

        layout.addWidget(title)
        layout.addLayout(self._detail_row(Labels.PARTNER_NAME, self.detail_name))
        layout.addLayout(self._detail_row(Labels.OWNER_NAME, self.detail_owner))
        layout.addLayout(self._detail_row(Labels.PHONE, self.detail_phone))
        layout.addLayout(self._detail_row(Labels.ADDRESS, self.detail_address, top_align=True))
        layout.addLayout(self._detail_row(Labels.MEMO, self.detail_memo, top_align=True))
        layout.addWidget(self.type_caption)
        layout.addWidget(self.type_indicator_grid)
        layout.addStretch(1)
        return card

    def _detail_row(self, label_text: str, value_widget: QWidget, top_align: bool = False):
        return build_labeled_value_row(
            self,
            label_text,
            value_widget,
            label_width=PartnerLayout.DETAIL_LABEL_WIDTH,
            spacing=PartnerLayout.CARD_ROW_SPACING,
            label_builder=self._make_detail_label,
            top_align=top_align,
        )

    def _make_detail_label(self, text: str, parent: QWidget) -> QLabel:
        label = QLabel(text, parent)
        label.setStyleSheet(partner_field_label_style())
        return label

    def _detail_value_label(self, min_height: int = 34, wrap: bool = False, align_top: bool = False) -> QLabel:
        label = QLabel(detail_value_fallback(), self)
        label.setObjectName("partnerValue")
        label.setMinimumHeight(min_height)
        label.setWordWrap(wrap)
        label.setAlignment((Qt.AlignTop | Qt.AlignLeft) if align_top else (Qt.AlignVCenter | Qt.AlignLeft))
        return label

    def reload_all(self) -> None:
        reload_all(self)

    def apply_filter(self, text: str) -> None:
        apply_filter(self, text)

    def _on_current_row_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._filtered):
            clear_detail(self)
            return
        partner = self._filtered[row]
        self._current_partner_id = partner.id
        show_partner(self, partner)

    def on_add(self) -> None:
        on_add(self)

    def on_edit(self) -> None:
        on_edit(self)

    def on_delete(self) -> None:
        on_delete(self)

    def on_manage_types(self) -> None:
        on_manage_types(self)


__all__ = ["PartnerBrowserDialog"]
