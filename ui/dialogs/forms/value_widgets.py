from __future__ import annotations

from PySide6.QtCore import Qt, QRegularExpression, QDate, QPoint, Signal, QSize, QEvent
from PySide6.QtGui import QRegularExpressionValidator, QGuiApplication
from PySide6.QtWidgets import QCalendarWidget, QComboBox, QDialog, QLineEdit, QLabel, QSizePolicy, QToolButton, QVBoxLayout

from services.common.formatters import digits_only, format_commas_from_digits
from ui.dialogs.forms.layout_utils import make_dialog_inline_row
from ui.icon_factory import make_calendar_icon, make_partner_link_icon
from ui.layout_metrics import DialogLayout
from ui.messages import Tooltips
from ui.theme import THEME, combo_box_style, compact_popup_margins, display_field_style, input_line_edit_style, tool_button_style
from ui.widget_factory import make_inline_icon_button, set_widget_tooltip


class MoneyLineEdit(QLineEdit):
    def __init__(self, parent=None, *, fixed_height: int | None = None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9,]*"), self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setMinimumHeight(fixed_height or THEME.dialog_field_height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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


class ClearableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(False)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.installEventFilter(self)
        self.setStyleSheet(combo_box_style())

    def eventFilter(self, obj, event):
        if obj is self and event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if self.count() > 0:
                self.setCurrentIndex(0)
                return True
        return super().eventFilter(obj, event)


class CalendarPopup(QDialog):
    datePicked = Signal(QDate)

    def __init__(self, initial: QDate, parent=None):
        super().__init__(parent, Qt.Popup)
        self.setObjectName('CalendarPopup')
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


def build_calendar_row(parent, date_value: QDate, on_click):
    date_text = QLabel(date_value.toString('yyyy-MM-dd'), parent)
    date_text.setMinimumHeight(THEME.dialog_field_height)
    date_text.setFixedWidth(THEME.calendar_display_width)
    date_text.setStyleSheet(display_field_style(8))

    btn_calendar = QToolButton(parent)
    btn_calendar.setFixedSize(THEME.dialog_field_height, THEME.dialog_field_height)
    set_widget_tooltip(btn_calendar, Tooltips.OPEN_CALENDAR)
    btn_calendar.setCursor(Qt.PointingHandCursor)
    btn_calendar.setAutoRaise(True)
    btn_calendar.setIcon(make_calendar_icon(THEME.icon_size_md))
    btn_calendar.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
    btn_calendar.setStyleSheet(tool_button_style())
    btn_calendar.clicked.connect(on_click)
    return date_text, btn_calendar, make_dialog_inline_row(parent, date_text, btn_calendar)


def show_calendar_popup(parent, anchor, current_date: QDate, on_selected):
    popup = CalendarPopup(current_date, parent)
    popup.datePicked.connect(on_selected)
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
    return popup


def build_partner_picker_row(parent, line_edit, *, tooltip: str, icon_size: int, button_size: int, on_click, stretch: bool = False):
    btn_partner = make_inline_icon_button(
        parent=parent,
        tooltip=tooltip,
        icon=make_partner_link_icon(icon_size),
        size=button_size,
    )
    btn_partner.clicked.connect(on_click)
    return btn_partner, make_dialog_inline_row(parent, line_edit, btn_partner, stretch=stretch)
