from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QWidget

from services.partner.management_service import PartnerManagementService
from ui.partners.browser.view import build_browser_content, build_browser_root
from ui.layout_metrics import PartnerLayout
from ui.messages import Buttons, DialogTitles, Labels, Placeholders, Symbols, Tooltips
from ui.partners.browser.actions import on_add, on_delete, on_edit, on_manage_types
from ui.partners.browser.selection import apply_filter, clear_detail, reload_all, show_partner
from ui.partners.dialogs.common import partner_detail_value_style, partner_field_label_style, partner_shell_style
from ui.theme import dialog_layout_margins, title_label_style
from ui.ui_metrics import CommonSymbolsLayout
from ui.button_layout_utils import make_dialog_button_row
from ui.widget_factory_buttons import make_icon_button
from ui.window_policy import lock_window_size


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

        root = build_browser_root(self)
        build_browser_content(self, root)

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
        lock_window_size(self, width=PartnerLayout.BROWSER_WIDTH, height=PartnerLayout.BROWSER_HEIGHT)

    @staticmethod
    def dialog_margins() -> tuple[int, int, int, int]:
        return dialog_layout_margins()

    @staticmethod
    def title_style() -> str:
        return title_label_style()

    def make_detail_label(self, text: str, parent: QWidget) -> QLabel:
        label = QLabel(text, parent)
        label.setStyleSheet(partner_field_label_style())
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
