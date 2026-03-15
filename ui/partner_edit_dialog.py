from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QDialog, QLabel, QLineEdit, QPlainTextEdit, QHBoxLayout, QVBoxLayout

from services.partner_repository import PartnerRecord
from ui.dialogs import show_warning
from ui.messages import DialogTitles, InfoMessages, Labels, Placeholders, Tooltips, WarningMessages
from ui.partner_dialog_common import partner_card_style, partner_field_label_style, partner_type_check_style
from ui.dialog_form_fields import add_dialog_grid_row, build_dialog_card, build_dialog_grid, build_hint_label, build_section_title, configure_text_field
from ui.layout_metrics import DialogLayout, PartnerLayout
from ui.theme import THEME, dialog_layout_margins, plain_text_edit_style, title_label_style
from ui.widget_factory import make_dialog_button_row, make_icon_button


class PartnerEditDialog(QDialog):
    def __init__(self, all_types: list[str], partner: PartnerRecord | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(DialogTitles.PARTNER_ADD if partner is None else DialogTitles.PARTNER_EDIT)
        self.resize(700, 520)
        self._all_types = all_types
        self._partner_id = partner.id if partner else ""

        root = QVBoxLayout(self)
        root.setContentsMargins(*dialog_layout_margins())
        root.setSpacing(THEME.block_spacing)

        title = QLabel(self.windowTitle(), self)
        title.setStyleSheet(title_label_style(font_px=THEME.menu_title_font_px - 3))
        root.addWidget(title)

        body = QHBoxLayout()
        body.setSpacing(THEME.section_gap)
        root.addLayout(body, 1)

        form_card, form_card_layout = build_dialog_card(self, object_name="partnerCard")
        form_layout = build_dialog_grid()
        form_card_layout.addLayout(form_layout)
        body.addWidget(form_card, 7)

        self.name_edit = self._make_line_edit(Placeholders.PARTNER_NAME)
        self.owner_edit = self._make_line_edit(Placeholders.OWNER_NAME)
        self.phone_edit = self._make_line_edit(Placeholders.PHONE)
        self.address_edit = self._make_line_edit(Placeholders.ADDRESS)
        self.memo_edit = QPlainTextEdit(self)
        self.memo_edit.setPlaceholderText(Placeholders.SHORT_MEMO)
        self.memo_edit.setStyleSheet(plain_text_edit_style())
        self.memo_edit.setFixedHeight(PartnerLayout.MEMO_HEIGHT)

        add_dialog_grid_row(form_layout, 0, self._make_label(Labels.PARTNER_NAME), self.name_edit)
        add_dialog_grid_row(form_layout, 1, self._make_label(Labels.OWNER_NAME), self.owner_edit)
        add_dialog_grid_row(form_layout, 2, self._make_label(Labels.PHONE), self.phone_edit)
        add_dialog_grid_row(form_layout, 3, self._make_label(Labels.ADDRESS), self.address_edit)
        add_dialog_grid_row(form_layout, 4, self._make_label(Labels.MEMO), self.memo_edit, top_align=True)

        type_card, type_layout = build_dialog_card(self, object_name="partnerCard")
        type_layout.setSpacing(PartnerLayout.TYPE_SECTION_SPACING)
        type_layout.addWidget(build_section_title(DialogTitles.PARTNER_TYPE, type_card))
        type_layout.addWidget(build_hint_label(InfoMessages.PARTNER_TYPE_SELECT_HINT, type_card))
        self.type_checks: list[QCheckBox] = []
        for idx, type_name in enumerate(all_types):
            check = QCheckBox(type_name, type_card)
            check.setStyleSheet(partner_type_check_style(idx))
            self.type_checks.append(check)
            type_layout.addWidget(check)
        type_layout.addStretch(1)
        body.addWidget(type_card, 4)

        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip=Tooltips.SAVE, text="✓", font_px=18)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.CLOSE, text="×", font_px=18)
        root.addLayout(make_dialog_button_row([self.btn_save, self.btn_close]))

        self.btn_save.clicked.connect(self._accept_if_valid)
        self.btn_close.clicked.connect(self.reject)

        self.setStyleSheet(self.styleSheet() + partner_card_style())

        if partner is not None:
            self._load_partner(partner)

    def _make_label(self, text: str) -> QLabel:
        label = QLabel(text, self)
        label.setStyleSheet(partner_field_label_style())
        return label

    def _make_line_edit(self, placeholder: str) -> QLineEdit:
        edit = configure_text_field(QLineEdit(self))
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(THEME.field_height + PartnerLayout.FIELD_EXTRA_HEIGHT)
        return edit

    def _load_partner(self, partner: PartnerRecord) -> None:
        self.name_edit.setText(partner.name)
        self.owner_edit.setText(partner.owner)
        self.phone_edit.setText(partner.phone)
        self.address_edit.setText(partner.address)
        self.memo_edit.setPlainText(partner.memo)
        selected = set(partner.types or [])
        for check in self.type_checks:
            check.setChecked(check.text() in selected)

    def _accept_if_valid(self) -> None:
        if not self.name_edit.text().strip():
            show_warning(self, DialogTitles.SAVE_BLOCKED, WarningMessages.PARTNER_NAME_REQUIRED)
            self.name_edit.setFocus()
            return
        if not self.selected_types():
            show_warning(self, DialogTitles.SAVE_BLOCKED, WarningMessages.PARTNER_TYPE_REQUIRED)
            return
        self.accept()

    def selected_types(self) -> list[str]:
        return [check.text() for check in self.type_checks if check.isChecked()]

    def to_record(self) -> PartnerRecord:
        return PartnerRecord(
            id=self._partner_id,
            name=self.name_edit.text().strip(),
            owner=self.owner_edit.text().strip(),
            phone=self.phone_edit.text().strip(),
            address=self.address_edit.text().strip(),
            memo=self.memo_edit.toPlainText().strip(),
            types=self.selected_types(),
        )
