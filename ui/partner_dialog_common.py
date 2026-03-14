from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QGridLayout, QHBoxLayout, QLabel, QListWidget, QVBoxLayout, QWidget

from services.partner_repository import PartnerRecord
from services.partner_utils import color_for_partner_type
from ui.messages import InfoMessages
from ui.theme import THEME, hex_to_rgba


class TypeBadgeRow(QWidget):
    def __init__(self, types: list[str], all_types: list[str], parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        selected = set(types)
        for idx, type_name in enumerate(all_types[:8]):
            badge = QLabel(type_name[:1], self)
            active = type_name in selected
            color = color_for_partner_type(idx)
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


class PartnerListItem(QWidget):
    def __init__(self, partner: PartnerRecord, all_types: list[str], parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 7, 8, 7)
        layout.setSpacing(6)
        title = QLabel(partner.name, self)
        title.setStyleSheet(f"QLabel{{font-weight:700;color:{THEME.color_text};background:transparent;}}")
        layout.addWidget(title)
        layout.addWidget(TypeBadgeRow(partner.types or [], all_types, self))


class ReadOnlyTypeIndicatorGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_grid = QGridLayout(self)
        self.layout_grid.setContentsMargins(0, 0, 0, 0)
        self.layout_grid.setHorizontalSpacing(10)
        self.layout_grid.setVerticalSpacing(8)

    def set_types(self, all_types: Iterable[str], selected_types: Iterable[str]) -> None:
        selected = set(selected_types)
        while self.layout_grid.count():
            item = self.layout_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for idx, type_name in enumerate(all_types):
            box = QCheckBox(type_name, self)
            box.setEnabled(False)
            color = color_for_partner_type(idx)
            box.setStyleSheet(
                f"QCheckBox{{spacing:8px;color:{THEME.color_text};}}"
                f"QCheckBox::indicator{{width:14px;height:14px;border-radius:4px;border:1px solid {hex_to_rgba(color, 0.36)};background:{hex_to_rgba(color, 0.08)};}}"
                f"QCheckBox::indicator:checked{{background:{color};border-color:{color};}}"
            )
            box.setChecked(type_name in selected)
            self.layout_grid.addWidget(box, idx // 2, idx % 2)


def partner_shell_style() -> str:
    return f"QFrame#partnerShell{{background:{THEME.color_surface};border:1px solid {THEME.color_border};border-radius:18px;}}"


def partner_card_style() -> str:
    return f"QFrame#partnerCard{{background:{THEME.color_surface};border:1px solid {THEME.color_border};border-radius:18px;}}"


def partner_detail_value_style() -> str:
    return (
        f"QLabel#partnerValue{{background:{hex_to_rgba(THEME.color_window, 1.0)};border:1px solid {THEME.color_border_soft};"
        f"border-radius:12px;padding:8px 10px;color:{THEME.color_text};}}"
    )


def partner_list_style() -> str:
    return (
        f"QListWidget{{background:{THEME.color_window};border:1px solid {THEME.color_border};border-radius:12px;padding:6px;}}"
        f"QListWidget::item{{border:none;padding:4px;}}"
        f"QListWidget::item:selected{{background:{hex_to_rgba(THEME.color_primary, 0.10)};border-radius:10px;}}"
    )


def partner_field_label_style() -> str:
    return f"QLabel{{font-weight:600;color:{THEME.color_text_soft};background:transparent;}}"


def partner_type_check_style(index: int) -> str:
    color = color_for_partner_type(index)
    return (
        f"QCheckBox{{spacing:8px;color:{THEME.color_text};}}"
        f"QCheckBox::indicator{{width:14px;height:14px;border-radius:4px;border:1px solid {hex_to_rgba(color, 0.36)};background:{hex_to_rgba(color, 0.08)};}}"
        f"QCheckBox::indicator:checked{{background:{color};border-color:{color};}}"
    )


def detail_value_fallback() -> str:
    return InfoMessages.PARTNER_EMPTY_VALUE
