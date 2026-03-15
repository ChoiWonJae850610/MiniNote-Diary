from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from services.partner_management_service import PartnerManagementService
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
from ui.theme import THEME, dialog_layout_margins, input_line_edit_style, title_label_style
from ui.ui_metrics import CommonSymbolsLayout
from ui.widget_factory import make_dialog_button_row, make_icon_button


class PartnerDialog(QDialog):
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
        root.setSpacing(THEME.section_spacing)

        title = QLabel(DialogTitles.PARTNER_MANAGE, self)
        title.setStyleSheet(title_label_style())
        root.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(PartnerLayout.CONTENT_SPACING)
        root.addLayout(content, 1)

        content.addWidget(self._build_left_card(), 1)
        content.addWidget(self._build_right_card(), 1)

        self.btn_type = make_icon_button(Symbols.MENU, Tooltips.PARTNER_TYPE_MANAGE, self)
        self.btn_add = make_icon_button(Symbols.ADD, Tooltips.ADD, self)
        self.btn_save = make_icon_button(Symbols.SAVE, Tooltips.EDIT_SAVE, self)
        self.btn_delete = make_icon_button(Symbols.DELETE, Tooltips.DELETE, self)
        self.btn_close = make_icon_button(Symbols.CLOSE, Tooltips.CLOSE, self)
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

    def _build_left_card(self) -> QFrame:
        card = QFrame(self)
        card.setObjectName("partnerShell")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(PartnerLayout.CARD_MARGIN, PartnerLayout.CARD_MARGIN, PartnerLayout.CARD_MARGIN, PartnerLayout.CARD_MARGIN)
        layout.setSpacing(PartnerLayout.CARD_ROW_SPACING)
        title = QLabel(DialogTitles.PARTNER_LIST, card)
        title.setStyleSheet(title_label_style(font_px=THEME.section_title_font_px + 1))
        self.search_edit = QLineEdit(card)
        self.search_edit.setPlaceholderText(Placeholders.PARTNER_SEARCH)
        self.search_edit.setStyleSheet(input_line_edit_style())
        self.search_edit.setFixedHeight(THEME.field_height + PartnerLayout.FIELD_EXTRA_HEIGHT)
        self.list_widget = QListWidget(card)
        self.list_widget.setObjectName("partnerList")
        self.list_widget.setStyleSheet(partner_list_style())
        layout.addWidget(title)
        layout.addWidget(self.search_edit)
        layout.addWidget(self.list_widget, 1)
        return card

    def _build_right_card(self) -> QFrame:
        card = QFrame(self)
        card.setObjectName("partnerShell")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(PartnerLayout.CARD_MARGIN, PartnerLayout.CARD_MARGIN, PartnerLayout.CARD_MARGIN, PartnerLayout.CARD_MARGIN)
        layout.setSpacing(PartnerLayout.DETAIL_CARD_SPACING)
        title = QLabel(DialogTitles.PARTNER_BASIC_INFO, card)
        title.setStyleSheet(title_label_style(font_px=THEME.section_title_font_px + 1))
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
        row = QHBoxLayout()
        row.setSpacing(PartnerLayout.CARD_ROW_SPACING)
        label = QLabel(label_text, self)
        label.setFixedWidth(PartnerLayout.DETAIL_LABEL_WIDTH)
        label.setStyleSheet(partner_field_label_style())
        alignment = Qt.AlignTop if top_align else Qt.AlignVCenter
        row.addWidget(label, 0, alignment)
        row.addWidget(value_widget, 1)
        return row

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
