from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QDate, QPoint, QSize, Qt, Signal, QSignalBlocker
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QLabel, QSizePolicy, QToolButton

from ui.icon_factory import make_calendar_icon, make_partner_link_icon
from ui.layout_metrics import PostItLayout
from ui.messages import Labels, Tooltips
from ui.partner_ui_utils import PARTNER_PICKER_TYPE_FACTORY, show_partner_picker
from ui.postit.base import _PostItCardBase
from ui.postit.common import FIELD_H, InlineCalendarPopup
from ui.postit.editors import _ClickToEditLineEdit, _MoneyLineEdit
from ui.postit.forms import PostItBodyLayout, make_field_label, make_form_row
from ui.postit.layout import POSTIT_BODY_HEIGHT
from ui.theme import THEME, display_field_style, input_line_edit_style, tool_button_style
from ui.widget_factory import set_widget_tooltip


class BasicInfoPostIt(_PostItCardBase):
    data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("basic", parent=parent)
        self.setMinimumSize(QSize(320, POSTIT_BODY_HEIGHT))
        self.setFixedHeight(POSTIT_BODY_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        root = PostItBodyLayout(self)

        self._date_value = QDate.currentDate()
        self.date_text = QLabel(self._date_value.toString("yyyy-MM-dd"), self)
        self.date_text.setFixedHeight(FIELD_H)
        self.date_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_text.setStyleSheet(display_field_style())
        self.date_text.setMinimumWidth(THEME.calendar_display_width + PostItLayout.DATE_MIN_WIDTH_EXTRA)

        self.btn_calendar = QToolButton(self)
        self.btn_calendar.setIcon(make_calendar_icon(PostItLayout.CALENDAR_ICON_SIZE))
        self.btn_calendar.setIconSize(QSize(PostItLayout.CALENDAR_ICON_SIZE, PostItLayout.CALENDAR_ICON_SIZE))
        self.btn_calendar.setFixedSize(FIELD_H, FIELD_H)
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        set_widget_tooltip(self.btn_calendar, Tooltips.OPEN_CALENDAR)
        self.btn_calendar.setStyleSheet(tool_button_style())
        self.btn_calendar.clicked.connect(self._open_calendar)

        date_row = make_form_row(make_field_label(Labels.DATE, self), self.date_text, self.btn_calendar)
        date_row.addStretch(1)
        root.addLayout(date_row)

        self.style_no = _ClickToEditLineEdit(self)
        self.factory = _ClickToEditLineEdit(self)
        self.btn_factory_partner = QToolButton(self)
        self.btn_factory_partner.setIcon(make_partner_link_icon(PostItLayout.PARTNER_LINK_ICON_SIZE))
        self.btn_factory_partner.setIconSize(QSize(PostItLayout.PARTNER_LINK_ICON_SIZE, PostItLayout.PARTNER_LINK_ICON_SIZE))
        self.btn_factory_partner.setFixedSize(FIELD_H, FIELD_H)
        self.btn_factory_partner.setCursor(Qt.PointingHandCursor)
        set_widget_tooltip(self.btn_factory_partner, Tooltips.PARTNER_MANAGE)
        self.btn_factory_partner.setStyleSheet(tool_button_style())
        self.btn_factory_partner.clicked.connect(self._open_factory_picker)
        self.factory.set_edit_enabled(False)
        self.factory.setFocusPolicy(Qt.NoFocus)
        self.style_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._style_no_min = 140
        self._style_no_max = 320
        self.style_no.textChanged.connect(self._adjust_style_width)
        self._adjust_style_width(self.style_no.text())

        root.addLayout(make_form_row(make_field_label(Labels.STYLE_NO, self), (self.style_no, 1)))
        root.addLayout(make_form_row(make_field_label(Labels.FACTORY, self), (self.factory, 1), self.btn_factory_partner))

        self.cost = _MoneyLineEdit(self)
        self.labor = _MoneyLineEdit(self)
        self.loss = _MoneyLineEdit(self)
        self.sale_price = _MoneyLineEdit(self)
        for widget in (self.cost, self.labor, self.loss, self.sale_price):
            widget.setStyleSheet(input_line_edit_style())
        self.cost.set_edit_enabled(False)
        self.cost.setFocusPolicy(Qt.NoFocus)
        self.sale_price.set_edit_enabled(False)
        self.sale_price.setFocusPolicy(Qt.NoFocus)
        self._syncing_prices = False

        root.addLayout(
            make_form_row(
                make_field_label(Labels.COST, self),
                (self.cost, 1),
                make_field_label(Labels.LABOR, self),
                (self.labor, 1),
            )
        )
        root.addLayout(
            make_form_row(
                make_field_label(Labels.LOSS, self),
                (self.loss, 1),
                make_field_label(Labels.SALE_PRICE, self),
                (self.sale_price, 1),
            )
        )

        self.style_no.committed.connect(lambda _v: self._emit_basic_fields())
        self.labor.textChanged.connect(self._on_price_component_changed)
        self.loss.textChanged.connect(self._on_price_component_changed)
        self.sale_price.textChanged.connect(self._on_sale_price_changed)

        self.setTabOrder(self.btn_calendar, self.style_no)
        self.setTabOrder(self.style_no, self.btn_factory_partner)
        self.setTabOrder(self.btn_factory_partner, self.labor)
        self.setTabOrder(self.labor, self.loss)
        self.setTabOrder(self.loss, self.sale_price)

        self.labor._pending_prev_widget = self.btn_factory_partner
        self.labor._pending_next_widget = self.loss
        self.loss._pending_prev_widget = self.labor

    def _emit_basic_fields(self):
        self.data_changed.emit({
            "date": self._date_value.toString("yyyy-MM-dd"),
            "style_no": self.style_no.text(),
            "factory": self.factory.text(),
            "factory_partner_id": str(self.factory.property("factory_partner_id") or ""),
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
        material_total = int(self.cost.digits() or "0")
        labor = int(self.labor.digits() or "0")
        loss = int(self.loss.digits() or "0")
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
        self.factory.setProperty("factory_partner_id", "")
        self._emit_basic_fields()

    def _open_factory_picker(self):
        def _apply(partner):
            self.factory.set_text_silent(partner.name)
            self.factory.setProperty("factory_partner_id", partner.id)
            self._emit_basic_fields()

        show_partner_picker(self.btn_factory_partner, partner_type=PARTNER_PICKER_TYPE_FACTORY, on_selected=_apply)

    def _open_calendar(self):
        popup = InlineCalendarPopup(self._date_value, parent=self)
        popup.datePicked.connect(self._on_date_picked)
        popup.moveNextRequested.connect(self.style_no.activate_for_input)
        anchor = self.btn_calendar.mapToGlobal(QPoint(0, self.btn_calendar.height() + PostItLayout.CALENDAR_POPUP_OFFSET_Y))
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
            self.factory.setProperty("factory_partner_id", header.get("factory_partner_id", ""))
            self._adjust_style_width(self.style_no.text())
            self.cost.setText(header.get("cost_display", header.get("cost", "")) or "")
            self.labor.setText(header.get("labor_display", header.get("labor", "")) or "")
            self.loss.setText(header.get("loss_display", header.get("loss", "")) or "")
            self.sale_price.setText(header.get("sale_price_display", header.get("sale_price", "")) or "")
        finally:
            del blockers
