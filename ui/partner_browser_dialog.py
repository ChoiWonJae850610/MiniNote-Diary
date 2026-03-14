from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from services.partner_management_service import PartnerManagementService
from services.partner_repository import PartnerRecord
from services.search_utils import matches_keyword
from ui.dialogs import ConfirmActionDialog, show_info, show_warning
from ui.ui_metrics import CommonSymbolsLayout
from ui.layout_metrics import PartnerLayout
from ui.messages import Buttons, DialogTitles, InfoMessages, Labels, Placeholders, Symbols, Tooltips, WarningMessages
from ui.partner_dialog_common import (
    PartnerListItem,
    ReadOnlyTypeIndicatorGrid,
    detail_value_fallback,
    partner_detail_value_style,
    partner_field_label_style,
    partner_list_style,
    partner_shell_style,
)
from ui.partner_edit_dialog import PartnerEditDialog
from ui.partner_type_dialog import PartnerTypeDialog
from ui.theme import THEME, dialog_layout_margins, input_line_edit_style, title_label_style
from ui.widget_factory import make_dialog_button_row, make_icon_button


class PartnerDialog(QDialog):
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(DialogTitles.PARTNER_MANAGE)
        self.resize(880, 580)
        self.partner_service = PartnerManagementService(project_root)
        self._partners: list[PartnerRecord] = []
        self._filtered: list[PartnerRecord] = []
        self._type_order = self.partner_service.list_types()
        self._current_partner_id = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(*dialog_layout_margins())
        root.setSpacing(THEME.block_spacing)

        body = QHBoxLayout()
        body.setSpacing(THEME.section_gap)
        root.addLayout(body, 1)

        left_card = self._build_left_card()
        body.addWidget(left_card, 5)

        right_card = self._build_right_card()
        body.addWidget(right_card, 6)

        self.btn_type = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.TYPE_MANAGE, text=Symbols.TYPE_MANAGE, font_px=CommonSymbolsLayout.TYPE_BUTTON_FONT_PX)
        self.btn_add = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.ADD, text=Symbols.ADD, font_px=CommonSymbolsLayout.ACTION_ICON_FONT_PX)
        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip=Tooltips.EDIT, text=Symbols.SAVE, font_px=CommonSymbolsLayout.ACTION_ICON_FONT_PX)
        self.btn_delete = make_icon_button(parent=self, object_name="iconDanger", tooltip=Tooltips.DELETE, text=Symbols.DELETE, font_px=CommonSymbolsLayout.ACTION_ICON_FONT_PX)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.CLOSE, text=Symbols.CLOSE, font_px=CommonSymbolsLayout.ACTION_ICON_FONT_PX)
        root.addLayout(make_dialog_button_row([self.btn_type, self.btn_add, self.btn_save, self.btn_delete, self.btn_close]))

        self.setStyleSheet(self.styleSheet() + partner_shell_style() + partner_detail_value_style())

        self.search_edit.textChanged.connect(self.apply_filter)
        self.list_widget.currentRowChanged.connect(self._on_current_row_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
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
        self._type_order = self.partner_service.list_types()
        self._partners = self.partner_service.list_partners()
        self.apply_filter(self.search_edit.text())

    def apply_filter(self, text: str) -> None:
        self._filtered = [
            row
            for row in self._partners
            if matches_keyword(text, row.name, row.owner, row.phone, row.address, ' '.join(row.types or []))
        ]
        self._populate_list()

    def _populate_list(self) -> None:
        self.list_widget.clear()
        for partner in self._filtered:
            item = QListWidgetItem(self.list_widget)
            item.setData(Qt.UserRole, partner.id)
            widget = PartnerListItem(partner, self._type_order, self.list_widget)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
        if self._filtered:
            self.list_widget.setCurrentRow(0)
        else:
            self._clear_detail()

    def _find_by_id(self, partner_id: str) -> PartnerRecord | None:
        for row in self._partners:
            if row.id == partner_id:
                return row
        return None

    def _on_current_row_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._filtered):
            self._clear_detail()
            return
        partner = self._filtered[row]
        self._current_partner_id = partner.id
        self._show_partner(partner)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        if item is not None:
            self.on_edit()

    def _show_partner(self, partner: PartnerRecord) -> None:
        fallback = detail_value_fallback()
        self.detail_name.setText(partner.name or fallback)
        self.detail_owner.setText(partner.owner or fallback)
        self.detail_phone.setText(partner.phone or fallback)
        self.detail_address.setText(partner.address or fallback)
        self.detail_memo.setText(partner.memo or fallback)
        self.type_indicator_grid.set_types(self._type_order, partner.types or [])

    def _clear_detail(self) -> None:
        self._current_partner_id = ""
        fallback = detail_value_fallback()
        for label in [self.detail_name, self.detail_owner, self.detail_phone, self.detail_address, self.detail_memo]:
            label.setText(fallback)
        self.type_indicator_grid.set_types(self._type_order, [])

    def on_add(self) -> None:
        dialog = PartnerEditDialog(self._type_order, parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        created = self.partner_service.create_partner(self._partners, dialog.to_record())
        self.reload_all()
        self._select_partner(created.id)
        show_info(self, DialogTitles.SAVE, InfoMessages.PARTNER_SAVED)

    def on_edit(self) -> None:
        record = self._find_by_id(self._current_partner_id)
        if record is None:
            show_warning(self, DialogTitles.EDIT, WarningMessages.PARTNER_SELECT_TO_EDIT)
            return
        dialog = PartnerEditDialog(self._type_order, partner=record, parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        updated = self.partner_service.update_partner(self._partners, record.id, dialog.to_record())
        self.reload_all()
        self._select_partner(updated.id)
        show_info(self, DialogTitles.SAVE, InfoMessages.PARTNER_UPDATED)

    def on_delete(self) -> None:
        record = self._find_by_id(self._current_partner_id)
        if record is None:
            return
        confirm = ConfirmActionDialog(
            Buttons.DELETE,
            f"'{record.name}' {WarningMessages.PARTNER_DELETE_CONFIRM}",
            confirm_text=Buttons.DELETE,
            cancel_text=Buttons.CANCEL,
            parent=self,
        )
        if confirm.exec() != QDialog.Accepted:
            return
        self.partner_service.delete_partner(self._partners, record.id)
        self.reload_all()

    def on_manage_types(self) -> None:
        dialog = PartnerTypeDialog(self.partner_service, parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.partner_service.prune_partners_to_active_types(self._partners)
        self.reload_all()

    def _select_partner(self, partner_id: str) -> None:
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item and item.data(Qt.UserRole) == partner_id:
                self.list_widget.setCurrentRow(row)
                return
