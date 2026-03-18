from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QDate, QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import QLabel, QSizePolicy

from ui.postit.base import _PostItCardBase
from ui.postit.basic_info_logic import (
    on_price_component_changed,
    on_sale_price_changed,
    recompute_basic_prices,
    set_basic_header_data,
)
from ui.postit.basic_info_sections import (
    build_date_row,
    build_partner_rows,
    build_price_rows,
    configure_basic_info_tab_order,
    connect_basic_info_signals,
    open_factory_picker,
)
from ui.postit.common import InlineCalendarPopup
from ui.postit.forms import PostItBodyLayout
from ui.postit.layout import (
    POSTIT_BASIC_CARD_MIN_WIDTH,
    POSTIT_BODY_HEIGHT,
    POSTIT_CALENDAR_POPUP_OFFSET_Y,
    PostItLayout,
)


class BasicInfoPostIt(_PostItCardBase):
    data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("basic", parent=parent)
        self.setMinimumSize(QSize(POSTIT_BASIC_CARD_MIN_WIDTH, POSTIT_BODY_HEIGHT))
        self.setFixedHeight(POSTIT_BODY_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        root = PostItBodyLayout(self)

        self._date_value = QDate.currentDate()
        self.date_text = QLabel(self._date_value.toString("yyyy-MM-dd"), self)
        build_date_row(self, root)
        build_partner_rows(self, root)
        build_price_rows(self, root)
        self._syncing_prices = False
        connect_basic_info_signals(self)
        configure_basic_info_tab_order(self)

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
        recompute_basic_prices(self)

    def _on_price_component_changed(self, _text: str):
        on_price_component_changed(self, _text)

    def _on_sale_price_changed(self, _text: str):
        on_sale_price_changed(self, _text)

    def _adjust_style_width(self, text: str):
        # 제품명 입력칸은 카드 폭 안에서만 동작해야 하므로,
        # 텍스트 길이에 따라 최소 폭을 키우지 않습니다.
        # 긴 텍스트는 QLineEdit의 기본 동작대로 내부 스크롤/클리핑 처리됩니다.
        self.style_no.setMinimumWidth(0)

    def _on_factory_committed(self, value: str):
        self.factory.setProperty("factory_partner_id", "")
        self._emit_basic_fields()

    def _open_factory_picker(self):
        open_factory_picker(self)

    def _open_calendar(self):
        popup = InlineCalendarPopup(self._date_value, parent=self)
        popup.datePicked.connect(self._on_date_picked)
        popup.moveNextRequested.connect(self.style_no.activate_for_input)
        anchor = self.btn_calendar.mapToGlobal(QPoint(0, self.btn_calendar.height() + POSTIT_CALENDAR_POPUP_OFFSET_Y))
        popup.move(anchor)
        popup.show()
        popup.cal.setFocus(Qt.PopupFocusReason)

    def _on_date_picked(self, date: QDate):
        self._date_value = date
        self.date_text.setText(date.toString("yyyy-MM-dd"))
        self._emit_basic_fields()

    def set_header_data(self, header: Dict[str, str]):
        set_basic_header_data(self, header)
