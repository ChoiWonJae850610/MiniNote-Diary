from __future__ import annotations

from typing import Dict

from PySide6.QtCore import Qt, QDate, QRegularExpression, QSize, QPoint, Signal
from PySide6.QtGui import QRegularExpressionValidator, QGuiApplication
from PySide6.QtWidgets import QCalendarWidget, QDialog, QGridLayout, QLabel, QLineEdit, QToolButton, QVBoxLayout, QWidget

from services.formatters import digits_only, format_commas_from_digits
from ui.dialog_form_fields import build_dialog_actions, configure_text_field
from ui.icon_factory import make_calendar_icon, make_partner_link_icon
from ui.messages import Buttons, DialogTitles, Labels, Tooltips
from ui.theme import THEME, compact_popup_margins, display_field_style, field_label_style, input_line_edit_style, tool_button_style
from ui.widget_factory import make_inline_icon_button, set_widget_tooltip
from ui.dialog_layout_utils import make_dialog_form_layout, make_dialog_inline_row, make_dialog_root_layout
from ui.partner_ui_utils import PARTNER_PICKER_TYPE_FACTORY, set_partner_line_edit, show_partner_picker
from ui.layout_metrics import DialogLayout


class MoneyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9,]*"), self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setFixedHeight(THEME.dialog_field_height)
        self.setStyleSheet(input_line_edit_style())
        self._in_format = False
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        if self._in_format:
            return
        formatted = format_commas_from_digits(text)
        if formatted == text:
            return
        self._in_format = True
        try:
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
        finally:
            self._in_format = False

    def value_digits(self) -> str:
        return digits_only(self.text())


class _CalendarPopup(QDialog):
    datePicked = Signal(QDate)

    def __init__(self, initial: QDate, parent=None):
        super().__init__(parent, Qt.Popup)
        self.setObjectName("CalendarPopup")
        root = QVBoxLayout(self)
        root.setContentsMargins(*compact_popup_margins())
        root.setSpacing(0)
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        if initial and initial.isValid():
            self.calendar.setSelectedDate(initial)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        root.addWidget(self.calendar)
        self.calendar.activated.connect(self._on_activated)

    def _on_activated(self, date: QDate):
        if date and date.isValid():
            self.datePicked.emit(date)
        self.close()


class BasicInfoDialog(QDialog):
    def __init__(self, initial: Dict[str, str] | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(DialogTitles.BASIC_INFO_INPUT)
        self.setModal(True)
        self.setMinimumWidth(DialogLayout.MIN_WIDTH_STANDARD)
        initial = initial or {}
        root = make_dialog_root_layout(self)
        form = make_dialog_form_layout()

        initial_date = QDate.fromString(initial.get("date", ""), "yyyy-MM-dd")
        if not initial_date.isValid():
            initial_date = QDate.currentDate()
        self._date_value = initial_date

        self.date_text = QLabel(self._date_value.toString("yyyy-MM-dd"), self)
        self.date_text.setMinimumHeight(THEME.dialog_field_height)
        self.date_text.setFixedWidth(THEME.calendar_display_width)
        self.date_text.setStyleSheet(display_field_style(8))

        self.btn_calendar = QToolButton(self)
        self.btn_calendar.setFixedSize(THEME.dialog_field_height, THEME.dialog_field_height)
        set_widget_tooltip(self.btn_calendar, Tooltips.OPEN_CALENDAR)
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.setAutoRaise(True)
        self.btn_calendar.setIcon(make_calendar_icon(THEME.icon_size_md))
        self.btn_calendar.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        self.btn_calendar.setStyleSheet(tool_button_style())
        self.btn_calendar.clicked.connect(self._open_calendar)
        date_row = make_dialog_inline_row(self, self.date_text, self.btn_calendar)

        self.style_no = configure_text_field(QLineEdit(self))
        self.factory = configure_text_field(QLineEdit(self))
        for widget in (self.style_no, self.factory):
            widget.setFixedHeight(THEME.dialog_field_height)
        self.style_no.setText(initial.get("style_no", ""))
        self.factory.setText(initial.get("factory", ""))
        self.factory.setProperty("factory_partner_id", initial.get("factory_partner_id", ""))
        self.factory.textEdited.connect(lambda _text: self.factory.setProperty("factory_partner_id", ""))

        self.btn_factory_partner = make_inline_icon_button(
            parent=self,
            tooltip=Tooltips.PARTNER_MANAGE,
            icon=make_partner_link_icon(DialogLayout.BUTTON_ICON_SIZE),
            size=THEME.dialog_field_height,
        )
        self.btn_factory_partner.clicked.connect(self._open_factory_picker)
        factory_row = make_dialog_inline_row(self, self.factory, self.btn_factory_partner, stretch=False)

        price_row = QWidget(self)
        grid = QGridLayout(price_row)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(DialogLayout.PRICE_GRID_SPACING)

        self.cost = MoneyLineEdit(self)
        self.labor = MoneyLineEdit(self)
        self.loss = MoneyLineEdit(self)
        self.sale_price = MoneyLineEdit(self)
        self.cost.setText(initial.get("cost_display", ""))
        self.labor.setText(initial.get("labor_display", ""))
        self.loss.setText(initial.get("loss_display", ""))
        self.sale_price.setText(initial.get("sale_price_display", ""))
        self.cost.setReadOnly(True)
        self.cost.setFocusPolicy(Qt.NoFocus)

        for edit in (self.cost, self.labor, self.loss, self.sale_price):
            edit.setMinimumWidth(DialogLayout.PRICE_FIELD_MIN_WIDTH)
            edit.setMaximumWidth(DialogLayout.PRICE_FIELD_MAX_WIDTH)

        pairs = [(Labels.COST, self.cost), (Labels.LABOR, self.labor), (Labels.LOSS, self.loss), (Labels.SALE_PRICE, self.sale_price)]
        col = 0
        for label_text, edit in pairs:
            label = QLabel(label_text, self)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setStyleSheet(field_label_style())
            grid.addWidget(label, 0, col)
            grid.addWidget(edit, 0, col + 1)
            col += 2

        form.addRow(Labels.DATE, date_row)
        form.addRow(Labels.STYLE_NO, self.style_no)
        form.addRow(Labels.FACTORY, factory_row)
        form.addRow("", price_row)
        root.addLayout(form)

        btn_cancel, btn_ok, button_row = build_dialog_actions(self, confirm_text=Buttons.OK)
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        root.addLayout(button_row)

    def _open_calendar(self):
        if getattr(self, "_calendar_popup", None) is not None:
            self._calendar_popup.close()
            self._calendar_popup = None
        popup = _CalendarPopup(self._date_value, self)
        self._calendar_popup = popup

        def _apply_date(date: QDate):
            if date and date.isValid():
                self._date_value = date
                self.date_text.setText(self._date_value.toString("yyyy-MM-dd"))

        popup.datePicked.connect(_apply_date)
        anchor = self.date_text
        global_pos = anchor.mapToGlobal(QPoint(0, anchor.height() + DialogLayout.CALENDAR_POPUP_OFFSET_Y))
        screen = QGuiApplication.screenAt(global_pos) or QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        popup.adjustSize()
        width, height = popup.width(), popup.height()
        x, y = global_pos.x(), global_pos.y()
        if avail is not None:
            if x + width > avail.right():
                x = max(avail.left(), avail.right() - width)
            if y + height > avail.bottom():
                y = max(avail.top(), anchor.mapToGlobal(QPoint(0, 0)).y() - height - DialogLayout.CALENDAR_POPUP_OFFSET_Y)
        popup.move(x, y)
        popup.show()

    def _open_factory_picker(self):
        show_partner_picker(
            self.btn_factory_partner,
            partner_type=PARTNER_PICKER_TYPE_FACTORY,
            on_selected=lambda partner: set_partner_line_edit(self.factory, partner, id_property='factory_partner_id'),
        )

    def get_data(self) -> Dict[str, str]:
        return {
            "date": self._date_value.toString("yyyy-MM-dd"),
            "style_no": self.style_no.text().strip(),
            "factory": self.factory.text().strip(),
            "factory_partner_id": str(self.factory.property("factory_partner_id") or "").strip(),
            "cost_display": self.cost.text(),
            "labor_display": self.labor.text(),
            "loss_display": self.loss.text(),
            "sale_price_display": self.sale_price.text(),
            "cost": self.cost.value_digits(),
            "labor": self.labor.value_digits(),
            "loss": self.loss.value_digits(),
            "sale_price": self.sale_price.value_digits(),
        }
