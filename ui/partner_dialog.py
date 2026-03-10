from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.partner_repository import PartnerRecord, PartnerRepository
from ui.dialogs import ConfirmActionDialog, show_error, show_info, show_warning
from ui.theme import THEME, dialog_layout_margins, hex_to_rgba, input_line_edit_style, plain_text_edit_style, title_label_style
from ui.widget_factory import make_dialog_button_row, make_icon_button

_CHOSEONG = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

_TYPE_COLORS = [
    "#778295",
    "#6F8F89",
    "#9A7A6C",
    "#8A7AA8",
    "#A08060",
    "#7D8794",
    "#6784A5",
    "#7FA071",
]


@dataclass
class _PartnerDraft:
    name: str = ""
    owner: str = ""
    phone: str = ""
    address: str = ""
    memo: str = ""
    types: list[str] | None = None


def _chosung_string(text: str) -> str:
    result = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            result.append(_CHOSEONG[(code - 0xAC00) // 588])
        else:
            result.append(ch)
    return "".join(result)


def _normalize_for_search(text: str) -> str:
    compact = "".join(str(text or "").strip().lower().split())
    return compact


def _matches_keyword(keyword: str, *values: str) -> bool:
    needle = _normalize_for_search(keyword)
    if not needle:
        return True
    for value in values:
        normalized = _normalize_for_search(value)
        chosung = _normalize_for_search(_chosung_string(value))
        if needle in normalized or needle in chosung:
            return True
    return False


class _TypeBadgeRow(QWidget):
    def __init__(self, types: list[str], all_types: list[str], parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        selected = set(types)
        for idx, type_name in enumerate(all_types[:8]):
            badge = QLabel(type_name[:1], self)
            active = type_name in selected
            color = _TYPE_COLORS[idx % len(_TYPE_COLORS)]
            if active:
                badge.setStyleSheet(
                    f"QLabel{{min-width:16px;max-width:16px;min-height:16px;max-height:16px;"
                    f"border-radius:4px;background:{color};color:white;font-size:10px;font-weight:700;}}"
                )
            else:
                badge.setStyleSheet(
                    f"QLabel{{min-width:16px;max-width:16px;min-height:16px;max-height:16px;"
                    f"border-radius:4px;background:{hex_to_rgba(color, 0.12)};border:1px solid {hex_to_rgba(color, 0.32)};"
                    f"color:{hex_to_rgba(color, 0.86)};font-size:10px;font-weight:700;}}"
                )
            badge.setAlignment(Qt.AlignCenter)
            badge.setToolTip(type_name)
            row.addWidget(badge)
        row.addStretch(1)


class _PartnerListItem(QWidget):
    def __init__(self, partner: PartnerRecord, all_types: list[str], parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 7, 8, 7)
        layout.setSpacing(6)
        title = QLabel(partner.name, self)
        title.setStyleSheet(f"QLabel{{font-weight:700;color:{THEME.color_text};background:transparent;}}")
        layout.addWidget(title)
        layout.addWidget(_TypeBadgeRow(partner.types or [], all_types, self))


class PartnerEditDialog(QDialog):
    def __init__(self, all_types: list[str], partner: PartnerRecord | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("거래처 추가" if partner is None else "거래처 수정")
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

        form_card = QFrame(self)
        form_card.setObjectName("partnerCard")
        form_layout = QGridLayout(form_card)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)
        body.addWidget(form_card, 7)

        self.name_edit = self._make_line_edit("상호명")
        self.owner_edit = self._make_line_edit("사장명")
        self.phone_edit = self._make_line_edit("연락처")
        self.address_edit = self._make_line_edit("주소")
        self.memo_edit = QPlainTextEdit(self)
        self.memo_edit.setPlaceholderText("간단한 메모")
        self.memo_edit.setStyleSheet(plain_text_edit_style())
        self.memo_edit.setFixedHeight(120)

        form_layout.addWidget(self._make_label("상호명"), 0, 0)
        form_layout.addWidget(self.name_edit, 0, 1)
        form_layout.addWidget(self._make_label("사장명"), 1, 0)
        form_layout.addWidget(self.owner_edit, 1, 1)
        form_layout.addWidget(self._make_label("연락처"), 2, 0)
        form_layout.addWidget(self.phone_edit, 2, 1)
        form_layout.addWidget(self._make_label("주소"), 3, 0)
        form_layout.addWidget(self.address_edit, 3, 1)
        form_layout.addWidget(self._make_label("메모"), 4, 0, Qt.AlignTop)
        form_layout.addWidget(self.memo_edit, 4, 1)

        type_card = QFrame(self)
        type_card.setObjectName("partnerCard")
        type_layout = QVBoxLayout(type_card)
        type_layout.setContentsMargins(18, 18, 18, 18)
        type_layout.setSpacing(10)
        type_title = QLabel("거래처 타입", type_card)
        type_title.setStyleSheet(title_label_style(font_px=THEME.section_title_font_px + 1))
        type_layout.addWidget(type_title)
        type_hint = QLabel("최소 1개 이상 선택", type_card)
        type_hint.setStyleSheet(f"QLabel{{color:{THEME.color_text_muted};background:transparent;}}")
        type_layout.addWidget(type_hint)
        self.type_checks: list[QCheckBox] = []
        for idx, type_name in enumerate(all_types):
            check = QCheckBox(type_name, type_card)
            color = _TYPE_COLORS[idx % len(_TYPE_COLORS)]
            check.setStyleSheet(
                f"QCheckBox{{spacing:8px;color:{THEME.color_text};}}"
                f"QCheckBox::indicator{{width:14px;height:14px;border-radius:4px;border:1px solid {hex_to_rgba(color, 0.36)};background:{hex_to_rgba(color, 0.08)};}}"
                f"QCheckBox::indicator:checked{{background:{color};border-color:{color};}}"
            )
            self.type_checks.append(check)
            type_layout.addWidget(check)
        type_layout.addStretch(1)
        body.addWidget(type_card, 4)

        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip="저장", text="✓", font_px=18)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip="닫기", text="×", font_px=18)
        root.addLayout(make_dialog_button_row([self.btn_save, self.btn_close]))

        self.btn_save.clicked.connect(self._accept_if_valid)
        self.btn_close.clicked.connect(self.reject)

        self.setStyleSheet(self.styleSheet() + self._extra_style())

        if partner is not None:
            self._load_partner(partner)

    def _extra_style(self) -> str:
        return (
            f"QFrame#partnerCard{{background:{THEME.color_surface};border:1px solid {THEME.color_border};border-radius:18px;}}"
        )

    def _make_label(self, text: str) -> QLabel:
        label = QLabel(text, self)
        label.setStyleSheet(f"QLabel{{font-weight:600;color:{THEME.color_text_soft};background:transparent;}}")
        return label

    def _make_line_edit(self, placeholder: str) -> QLineEdit:
        edit = QLineEdit(self)
        edit.setPlaceholderText(placeholder)
        edit.setStyleSheet(input_line_edit_style())
        edit.setFixedHeight(THEME.field_height + 6)
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
            show_warning(self, "저장 불가", "상호명을 입력하세요.")
            self.name_edit.setFocus()
            return
        if not self.selected_types():
            show_warning(self, "저장 불가", "거래처 타입을 1개 이상 선택하세요.")
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


class PartnerTypeDialog(QDialog):
    def __init__(self, repo: PartnerRepository, parent=None):
        super().__init__(parent)
        self.setWindowTitle("거래처 타입 관리")
        self.resize(540, 420)
        self.repo = repo

        from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem
        self.QTableWidgetItem = QTableWidgetItem

        root = QVBoxLayout(self)
        root.setContentsMargins(*dialog_layout_margins())
        root.setSpacing(THEME.block_spacing)

        self.table = QTableWidget(0, 1, self)
        self.table.setHorizontalHeaderLabels(["거래처 타입"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.SelectedClicked | QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.itemClicked.connect(lambda it: self.table.editItem(it))
        self.table.setStyleSheet(
            f"QTableWidget{{background:{THEME.color_window};border:1px solid {THEME.color_border};border-radius:12px;padding:4px;}}"
            f"QHeaderView::section{{background:{THEME.color_surface};border:none;border-bottom:1px solid {THEME.color_border_soft};padding:8px 10px;font-weight:600;color:{THEME.color_text_soft};}}"
        )
        self.table.verticalHeader().setDefaultSectionSize(THEME.table_row_height)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        root.addWidget(self.table)

        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip="저장", text="✓", font_px=18)
        self.btn_add = make_icon_button(parent=self, object_name="iconAction", tooltip="추가", text="+", font_px=18)
        self.btn_delete = make_icon_button(parent=self, object_name="iconDanger", tooltip="삭제", text="−", font_px=18)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip="닫기", text="×", font_px=18)
        root.addLayout(make_dialog_button_row([self.btn_save, self.btn_add, self.btn_delete, self.btn_close]))

        self.btn_save.clicked.connect(self.on_save)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_close.clicked.connect(self.reject)

        self._ensure_rows(16)
        self.load_types()

    def _ensure_rows(self, target: int) -> None:
        while self.table.rowCount() < target:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setRowHeight(r, THEME.table_row_height)

    def load_types(self) -> None:
        types = self.repo.load_types()
        self.table.clearContents()
        self.table.setRowCount(0)
        self._ensure_rows(max(16, len(types) + 1))
        for row, type_name in enumerate(types):
            self.table.setItem(row, 0, self.QTableWidgetItem(type_name))

    def on_add(self) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is None or not item.text().strip():
                if item is None:
                    item = self.QTableWidgetItem("")
                    self.table.setItem(row, 0, item)
                self.table.setCurrentCell(row, 0)
                self.table.editItem(item)
                return

    def on_delete(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        self.table.setItem(row, 0, self.QTableWidgetItem(""))

    def on_save(self) -> None:
        values = []
        seen = set()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            text = item.text().strip() if item else ""
            if text and text not in seen:
                values.append(text)
                seen.add(text)
        self.repo.save_types(values)
        show_info(self, "저장", "거래처 타입 목록이 저장되었습니다.")
        self.accept()


class PartnerDialog(QDialog):
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("거래처 관리")
        self.resize(880, 580)
        self.repo = PartnerRepository(project_root)
        self._partners: list[PartnerRecord] = []
        self._filtered: list[PartnerRecord] = []
        self._type_order = self.repo.load_types()
        self._current_partner_id = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(*dialog_layout_margins())
        root.setSpacing(THEME.block_spacing)

        body = QHBoxLayout()
        body.setSpacing(THEME.section_gap)
        root.addLayout(body, 1)

        left_card = QFrame(self)
        left_card.setObjectName("partnerShell")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(10)
        left_title = QLabel("거래처 목록", left_card)
        left_title.setStyleSheet(title_label_style(font_px=THEME.section_title_font_px + 1))
        self.search_edit = QLineEdit(left_card)
        self.search_edit.setPlaceholderText("검색")
        self.search_edit.setStyleSheet(input_line_edit_style())
        self.search_edit.setFixedHeight(THEME.field_height + 6)
        self.list_widget = QListWidget(left_card)
        self.list_widget.setObjectName("partnerList")
        self.list_widget.setStyleSheet(self._list_style())
        left_layout.addWidget(left_title)
        left_layout.addWidget(self.search_edit)
        left_layout.addWidget(self.list_widget, 1)
        body.addWidget(left_card, 5)

        right_card = QFrame(self)
        right_card.setObjectName("partnerShell")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)
        right_title = QLabel("거래처 기본 정보", right_card)
        right_title.setStyleSheet(title_label_style(font_px=THEME.section_title_font_px + 1))
        self.detail_name = self._detail_value_label(min_height=42)
        self.detail_owner = self._detail_value_label()
        self.detail_phone = self._detail_value_label()
        self.detail_address = self._detail_value_label(min_height=52, wrap=True)
        self.detail_memo = self._detail_value_label(min_height=110, wrap=True, align_top=True)
        self.type_caption = QLabel("타입", right_card)
        self.type_caption.setStyleSheet(f"QLabel{{font-weight:600;color:{THEME.color_text_soft};background:transparent;}}")
        self.type_checks_container = QWidget(right_card)
        self.type_checks_layout = QGridLayout(self.type_checks_container)
        self.type_checks_layout.setContentsMargins(0, 0, 0, 0)
        self.type_checks_layout.setHorizontalSpacing(10)
        self.type_checks_layout.setVerticalSpacing(8)
        self._build_type_indicators([])

        right_layout.addWidget(right_title)
        right_layout.addLayout(self._detail_row("상호명", self.detail_name))
        right_layout.addLayout(self._detail_row("사장명", self.detail_owner))
        right_layout.addLayout(self._detail_row("연락처", self.detail_phone))
        right_layout.addLayout(self._detail_row("주소", self.detail_address, top_align=True))
        right_layout.addLayout(self._detail_row("메모", self.detail_memo, top_align=True))
        right_layout.addWidget(self.type_caption)
        right_layout.addWidget(self.type_checks_container)
        right_layout.addStretch(1)
        body.addWidget(right_card, 6)

        self.btn_type = make_icon_button(parent=self, object_name="iconAction", tooltip="타입 관리", text="≡", font_px=15)
        self.btn_add = make_icon_button(parent=self, object_name="iconAction", tooltip="추가", text="+", font_px=18)
        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip="수정", text="✓", font_px=18)
        self.btn_delete = make_icon_button(parent=self, object_name="iconDanger", tooltip="삭제", text="−", font_px=18)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip="닫기", text="×", font_px=18)
        root.addLayout(make_dialog_button_row([self.btn_type, self.btn_add, self.btn_save, self.btn_delete, self.btn_close]))

        self.setStyleSheet(self.styleSheet() + self._dialog_style())

        self.search_edit.textChanged.connect(self.apply_filter)
        self.list_widget.currentRowChanged.connect(self._on_current_row_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_save.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_type.clicked.connect(self.on_manage_types)
        self.btn_close.clicked.connect(self.accept)

        self.reload_all()

    def _dialog_style(self) -> str:
        return (
            f"QFrame#partnerShell{{background:{THEME.color_surface};border:1px solid {THEME.color_border};border-radius:18px;}}"
            f"QLabel#partnerValue{{background:{hex_to_rgba(THEME.color_window, 1.0)};border:1px solid {THEME.color_border_soft};"
            f"border-radius:12px;padding:8px 10px;color:{THEME.color_text};}}"
        )

    def _list_style(self) -> str:
        return (
            f"QListWidget{{background:{THEME.color_window};border:1px solid {THEME.color_border};border-radius:12px;padding:6px;}}"
            f"QListWidget::item{{border:none;padding:4px;}}"
            f"QListWidget::item:selected{{background:{hex_to_rgba(THEME.color_primary, 0.10)};border-radius:10px;}}"
        )

    def _detail_row(self, label_text: str, value_widget: QWidget, top_align: bool = False):
        row = QHBoxLayout()
        row.setSpacing(10)
        label = QLabel(label_text, self)
        label.setFixedWidth(54)
        label.setStyleSheet(f"QLabel{{font-weight:600;color:{THEME.color_text_soft};background:transparent;}}")
        alignment = Qt.AlignTop if top_align else Qt.AlignVCenter
        row.addWidget(label, 0, alignment)
        row.addWidget(value_widget, 1)
        return row

    def _detail_value_label(self, min_height: int = 34, wrap: bool = False, align_top: bool = False) -> QLabel:
        label = QLabel("", self)
        label.setObjectName("partnerValue")
        label.setMinimumHeight(min_height)
        label.setWordWrap(wrap)
        label.setAlignment((Qt.AlignTop | Qt.AlignLeft) if align_top else (Qt.AlignVCenter | Qt.AlignLeft))
        return label

    def _build_type_indicators(self, selected_types: Iterable[str]) -> None:
        selected = set(selected_types)
        while self.type_checks_layout.count():
            item = self.type_checks_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for idx, type_name in enumerate(self._type_order):
            box = QCheckBox(type_name, self.type_checks_container)
            box.setEnabled(False)
            color = _TYPE_COLORS[idx % len(_TYPE_COLORS)]
            box.setStyleSheet(
                f"QCheckBox{{spacing:8px;color:{THEME.color_text};}}"
                f"QCheckBox::indicator{{width:14px;height:14px;border-radius:4px;border:1px solid {hex_to_rgba(color, 0.36)};background:{hex_to_rgba(color, 0.08)};}}"
                f"QCheckBox::indicator:checked{{background:{color};border-color:{color};}}"
            )
            box.setChecked(type_name in selected)
            self.type_checks_layout.addWidget(box, idx // 2, idx % 2)

    def reload_all(self) -> None:
        self._type_order = self.repo.load_types()
        self._partners = self.repo.load_partners()
        self.apply_filter(self.search_edit.text())

    def apply_filter(self, text: str) -> None:
        self._filtered = [
            row for row in self._partners
            if _matches_keyword(text, row.name, row.owner, row.phone, row.address, " ".join(row.types or []))
        ]
        self._populate_list()

    def _populate_list(self) -> None:
        self.list_widget.clear()
        for partner in self._filtered:
            item = QListWidgetItem(self.list_widget)
            item.setData(Qt.UserRole, partner.id)
            item.setSizeHint(self.list_widget.sizeHintForIndex(self.list_widget.indexFromItem(item)))
            widget = _PartnerListItem(partner, self._type_order, self.list_widget)
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
        if item is None:
            return
        self.on_edit()

    def _show_partner(self, partner: PartnerRecord) -> None:
        self.detail_name.setText(partner.name or "-")
        self.detail_owner.setText(partner.owner or "-")
        self.detail_phone.setText(partner.phone or "-")
        self.detail_address.setText(partner.address or "-")
        self.detail_memo.setText(partner.memo or "-")
        self._build_type_indicators(partner.types or [])

    def _clear_detail(self) -> None:
        self._current_partner_id = ""
        for label in [self.detail_name, self.detail_owner, self.detail_phone, self.detail_address, self.detail_memo]:
            label.setText("-")
        self._build_type_indicators([])

    def on_add(self) -> None:
        dlg = PartnerEditDialog(self._type_order, parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        record = dlg.to_record()
        record.id = self.repo.next_partner_id(self._partners)
        self._partners.append(record)
        self.repo.save_partners(self._partners)
        self.reload_all()
        self._select_partner(record.id)
        show_info(self, "저장", "거래처가 저장되었습니다.")

    def on_edit(self) -> None:
        record = self._find_by_id(self._current_partner_id)
        if record is None:
            show_warning(self, "수정", "수정할 거래처를 먼저 선택하세요.")
            return
        dlg = PartnerEditDialog(self._type_order, partner=record, parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        new_record = dlg.to_record()
        new_record.id = record.id
        for idx, item in enumerate(self._partners):
            if item.id == record.id:
                self._partners[idx] = new_record
                break
        self.repo.save_partners(self._partners)
        self.reload_all()
        self._select_partner(new_record.id)
        show_info(self, "저장", "거래처가 수정되었습니다.")

    def on_delete(self) -> None:
        record = self._find_by_id(self._current_partner_id)
        if record is None:
            return
        confirm = ConfirmActionDialog("삭제", f"'{record.name}' 거래처를 삭제하시겠습니까?", confirm_text="삭제", cancel_text="취소", parent=self)
        if confirm.exec() != QDialog.Accepted:
            return
        self._partners = [row for row in self._partners if row.id != record.id]
        self.repo.save_partners(self._partners)
        self.reload_all()

    def on_manage_types(self) -> None:
        dlg = PartnerTypeDialog(self.repo, parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        active_types = set(self.repo.load_types())
        changed = False
        for row in self._partners:
            original = list(row.types or [])
            row.types = [name for name in original if name in active_types]
            if row.types != original:
                changed = True
        if changed:
            self.repo.save_partners(self._partners)
        self.reload_all()

    def _select_partner(self, partner_id: str) -> None:
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item and item.data(Qt.UserRole) == partner_id:
                self.list_widget.setCurrentRow(row)
                return
