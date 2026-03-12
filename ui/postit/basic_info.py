from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QDate, QPoint, QSize, Qt, Signal, QSignalBlocker
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QToolButton, QVBoxLayout

from ui.icon_factory import make_calendar_icon, make_partner_link_icon
from ui.postit.base import _PostItCardBase
from ui.postit.common import FIELD_H, InlineCalendarPopup
from ui.postit.editors import _ClickToEditLineEdit, _MoneyLineEdit
from ui.partner_ui_utils import PARTNER_PICKER_TYPE_FACTORY, set_partner_line_edit, show_partner_picker
from ui.theme import display_field_style, field_label_style, input_line_edit_style, tool_button_style

from ui.theme import THEME

class BasicInfoPostIt(_PostItCardBase):
    data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("basic", parent=parent)
        self.setMinimumSize(QSize(320, THEME.postit_bar_max_height))
        self.setFixedHeight(THEME.postit_bar_max_height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        root = QVBoxLayout(self)
        root.setContentsMargins(THEME.filter_panel_margin_h, THEME.filter_panel_margin_v, THEME.filter_panel_margin_h, THEME.block_spacing)
        root.setSpacing(THEME.row_spacing)

        date_row = QHBoxLayout()
        date_row.setSpacing(6)
        lbl_date = QLabel("날  짜", self)
        lbl_date.setFixedWidth(THEME.field_label_width)
        lbl_date.setFixedHeight(FIELD_H)
        lbl_date.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_date.setStyleSheet(field_label_style())
        date_row.addWidget(lbl_date)

        self._date_value = QDate.currentDate()
        self.date_text = QLabel(self._date_value.toString("yyyy-MM-dd"), self)
        self.date_text.setFixedHeight(FIELD_H)
        self.date_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_text.setStyleSheet(display_field_style())
        self.date_text.setMinimumWidth(THEME.calendar_display_width + 8)

        self.btn_calendar = QToolButton(self)
        self.btn_calendar.setIcon(make_calendar_icon(16))
        self.btn_calendar.setIconSize(QSize(16, 16))
        self.btn_calendar.setFixedSize(FIELD_H, FIELD_H)
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.setStyleSheet(tool_button_style())
        self.btn_calendar.clicked.connect(self._open_calendar)

        date_row.addWidget(self.date_text, 1)
        date_row.addWidget(self.btn_calendar)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        def mk_label(text: str) -> QLabel:
            label = QLabel(text, self)
            label.setFixedWidth(THEME.field_label_width)
            label.setFixedHeight(FIELD_H)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setStyleSheet(field_label_style())
            return label

        self.style_no = _ClickToEditLineEdit(self)
        self.factory = _ClickToEditLineEdit(self)
        self.btn_factory_partner = QToolButton(self)
        self.btn_factory_partner.setIcon(make_partner_link_icon(14))
        self.btn_factory_partner.setIconSize(QSize(14, 14))
        self.btn_factory_partner.setFixedSize(FIELD_H, FIELD_H)
        self.btn_factory_partner.setCursor(Qt.PointingHandCursor)
        self.btn_factory_partner.setToolTip('거래처 관리')
        self.btn_factory_partner.setStyleSheet(tool_button_style())
        self.btn_factory_partner.clicked.connect(self._open_factory_picker)
        self.style_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._style_no_min = 140
        self._style_no_max = 320
        self.style_no.textChanged.connect(self._adjust_style_width)
        self._adjust_style_width(self.style_no.text())

        grid.addWidget(mk_label("제품명"), 0, 0)
        grid.addWidget(self.style_no, 0, 1)
        grid.addWidget(mk_label("공  장"), 1, 0)
        factory_row = QHBoxLayout()
        factory_row.setContentsMargins(0, 0, 0, 0)
        factory_row.setSpacing(6)
        factory_row.addWidget(self.factory, 1)
        factory_row.addWidget(self.btn_factory_partner, 0)
        grid.addLayout(factory_row, 1, 1)
        root.addLayout(grid)

        mg = QGridLayout()
        mg.setHorizontalSpacing(8)
        mg.setVerticalSpacing(5)
        mg.setContentsMargins(0, 2, 0, 0)

        self.cost = _MoneyLineEdit(self)
        self.labor = _MoneyLineEdit(self)
        self.loss = _MoneyLineEdit(self)
        self.sale_price = _MoneyLineEdit(self)
        for widget in (self.cost, self.labor, self.loss, self.sale_price):
            widget.setStyleSheet(input_line_edit_style())
        self.cost.set_edit_enabled(False)
        self.cost.setFocusPolicy(Qt.NoFocus)
        self._syncing_prices = False

        mg.addWidget(mk_label("재료비"), 0, 0)
        mg.addWidget(self.cost, 0, 1)
        mg.addWidget(mk_label("공  임"), 0, 2)
        mg.addWidget(self.labor, 0, 3)
        mg.addWidget(mk_label("로  스"), 1, 0)
        mg.addWidget(self.loss, 1, 1)
        mg.addWidget(mk_label("원  가"), 1, 2)
        mg.addWidget(self.sale_price, 1, 3)
        root.addLayout(mg)

        self.style_no.committed.connect(lambda _v: self._emit_basic_fields())
        self.factory.committed.connect(self._on_factory_committed)
        self.labor.textChanged.connect(self._on_price_component_changed)
        self.loss.textChanged.connect(self._on_price_component_changed)
        self.sale_price.textChanged.connect(self._on_sale_price_changed)

        self.setTabOrder(self.btn_calendar, self.style_no)
        self.setTabOrder(self.style_no, self.factory)
        self.setTabOrder(self.factory, self.labor)
        self.setTabOrder(self.labor, self.loss)
        self.setTabOrder(self.loss, self.sale_price)

        self.labor._pending_prev_widget = self.factory
        self.labor._pending_next_widget = self.loss
        self.loss._pending_prev_widget = self.labor
        self.loss._pending_next_widget = self.sale_price
        self.sale_price._pending_prev_widget = self.loss

    def _emit_basic_fields(self):
        self.data_changed.emit({
            "date": self._date_value.toString("yyyy-MM-dd"),
            "style_no": self.style_no.text(),
            "factory": self.factory.text(),
            "factory_partner_id": str(self.factory.property('factory_partner_id') or ''),
        })

    def _emit_price_fields(self):
        self.data_changed.emit({
            "cost_display": self.cost.text(),
            "labor_display": self.labor.text(),
            "loss_display": self.loss.text(),
            "sale_price_display": self.sale_price.text(),
            "cost": self.cost.digits(),
            "labor": self.labor.digits(),
            "loss": self.loss.digits(),
            "sale_price": self.sale_price.digits(),
        })

    def _recompute_prices(self):
        material_total = int(self.cost.digits() or '0')
        labor = int(self.labor.digits() or '0')
        loss = int(self.loss.digits() or '0')
        sale_total = material_total + labor + loss
        self._syncing_prices = True
        try:
            self.sale_price.setText(f"{sale_total:,}" if sale_total else "")
        finally:
            self._syncing_prices = False

    def _on_price_component_changed(self, _text: str):
        self._recompute_prices()
        self._emit_price_fields()

    def _on_sale_price_changed(self, _text: str):
        if self._syncing_prices:
            return
        self._emit_price_fields()

    def _adjust_style_width(self, text: str):
        metrics = QFontMetrics(self.style_no.font())
        width = metrics.horizontalAdvance(text or "") + 28
        width = max(self._style_no_min, min(self._style_no_max, width))
        self.style_no.setMinimumWidth(width)


    def _on_factory_committed(self, value: str):
        self.factory.setProperty('factory_partner_id', '')
        self._emit_basic_fields()

    def _open_factory_picker(self):
        def _apply(partner):
            self.factory.set_text_silent(partner.name)
            self.factory.setProperty('factory_partner_id', partner.id)
            self._emit_basic_fields()

        show_partner_picker(self.btn_factory_partner, partner_type=PARTNER_PICKER_TYPE_FACTORY, on_selected=_apply)

    def _open_calendar(self):
        popup = InlineCalendarPopup(self._date_value, parent=self)
        popup.datePicked.connect(self._on_date_picked)
        popup.moveNextRequested.connect(self.style_no.activate_for_input)
        anchor = self.btn_calendar.mapToGlobal(QPoint(0, self.btn_calendar.height() + 4))
        popup.move(anchor)
        popup.show()
        popup.cal.setFocus(Qt.PopupFocusReason)

    def _on_date_picked(self, date: QDate):
        self._date_value = date
        self.date_text.setText(date.toString("yyyy-MM-dd"))
        self._emit_basic_fields()

    def set_header_data(self, header: Dict[str, str]):
        header = header or {}
        date = QDate.fromString(header.get("date", ""), "yyyy-MM-dd")
        if not date.isValid():
            date = QDate.currentDate()
        self._date_value = date
        self.date_text.setText(date.toString("yyyy-MM-dd"))
        blockers = [
            QSignalBlocker(self.style_no),
            QSignalBlocker(self.factory),
            QSignalBlocker(self.cost),
            QSignalBlocker(self.labor),
            QSignalBlocker(self.loss),
            QSignalBlocker(self.sale_price),
        ]
        try:
            self.style_no.set_text_silent(header.get("style_no", ""))
            self.factory.set_text_silent(header.get("factory", ""))
            self.factory.setProperty('factory_partner_id', header.get("factory_partner_id", ""))
            self._adjust_style_width(self.style_no.text())
            self.cost.setText(header.get("cost_display", header.get("cost", "")) or "")
            self.labor.setText(header.get("labor_display", header.get("labor", "")) or "")
            self.loss.setText(header.get("loss_display", header.get("loss", "")) or "")
            self.sale_price.setText(header.get("sale_price_display", header.get("sale_price", "")) or "")
        finally:
            del blockers

