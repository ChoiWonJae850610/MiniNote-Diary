# ui/basic_info_dialog.py
from __future__ import annotations

from typing import Dict

from PySide6.QtCore import Qt, QDate, QRegularExpression, QSize, QPoint, Signal
from PySide6.QtGui import QRegularExpressionValidator, QIcon, QGuiApplication
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def _format_commas_from_digits(digits: str) -> str:
    if not digits:
        return ""
    try:
        return f"{int(digits):,}"
    except Exception:
        return digits


def _safe_int_from_digits(digits: str) -> int:
    digits = _digits_only(digits)
    return int(digits) if digits else 0


class MoneyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9,]*"), self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setFixedHeight(30)
        self._in_format = False
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        if self._in_format:
            return
        digits = _digits_only(text)
        formatted = _format_commas_from_digits(digits)
        if formatted == text:
            return
        self._in_format = True
        try:
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
        finally:
            self._in_format = False

    def value_digits(self) -> str:
        return _digits_only(self.text())


class _CalendarPopup(QDialog):
    datePicked = Signal(QDate)

    def __init__(self, initial: QDate, parent=None):
        super().__init__(parent, Qt.Popup)
        # Popup: no title bar, closes on outside click / Esc by default.
        self.setObjectName("CalendarPopup")

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(0)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        if initial and initial.isValid():
            self.calendar.setSelectedDate(initial)

        # Keep it compact
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        root.addWidget(self.calendar)

        self.calendar.activated.connect(self._on_activated)

    def _on_activated(self, d: QDate):
        if d and d.isValid():
            self.datePicked.emit(d)
        self.close()


class BasicInfoDialog(QDialog):
    def __init__(self, initial: Dict[str, str] | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("기본정보 입력")
        self.setModal(True)
        self.setMinimumWidth(460)

        initial = initial or {}

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        # 날짜: 텍스트 + 달력 버튼(팝업으로 선택)
        initial_date = QDate.fromString(initial.get("date", ""), "yyyy-MM-dd")
        if not initial_date.isValid():
            initial_date = QDate.currentDate()
        self._date_value = initial_date


        self.date_text = QLabel(self)
        self.date_text.setMinimumHeight(30)
        self.date_text.setText(self._date_value.toString("yyyy-MM-dd"))
        # Field-like look (label, not editable)
        self.date_text.setStyleSheet(
            "QLabel {"
            "  color: #666;"
            "  background: #f3f3f3;"
            "  border: 1px solid #c8c8c8;"
            "  border-radius: 6px;"
            "  padding: 4px 8px;"
            "}"
        )
        # 'yyyy-MM-dd' 길이(10자) 기준으로 과하게 넓지 않게
        self.date_text.setFixedWidth(110)

        self.btn_calendar = QToolButton(self)
        self.btn_calendar.setFixedSize(30, 30)
        self.btn_calendar.setToolTip("달력 열기")
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.setAutoRaise(True)

        # Icon-only calendar button (fallback: text if icon theme missing)
        icon = QIcon.fromTheme("x-office-calendar")
        if icon.isNull():
            icon = QIcon.fromTheme("view-calendar")
        if icon.isNull():
            icon = QIcon.fromTheme("office-calendar")

        if not icon.isNull():
            self.btn_calendar.setIcon(icon)
            self.btn_calendar.setIconSize(QSize(18, 18))
            self.btn_calendar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        else:
            # Fallback (some Windows setups may not provide theme icons)
            self.btn_calendar.setText("📅")

        # Subtle border so it reads as a button even with auto-raise
        self.btn_calendar.setStyleSheet(
            "QToolButton {"
            "  border: 1px solid #c8c8c8;"
            "  border-radius: 6px;"
            "  background: #f7f7f7;"
            "}"
            "QToolButton:hover {"
            "  background: #eeeeee;"
            "}"
            "QToolButton:pressed {"
            "  background: #e6e6e6;"
            "}"
        )

        self.btn_calendar.clicked.connect(self._open_calendar)

        date_row = QWidget(self)
        date_h = QHBoxLayout(date_row)
        date_h.setContentsMargins(0, 0, 0, 0)
        date_h.setSpacing(6)
        date_h.addWidget(self.date_text)
        date_h.addWidget(self.btn_calendar)
        date_h.addStretch(1)

        self.style_no = QLineEdit(self)
        self.factory = QLineEdit(self)
        for w in (self.style_no, self.factory):
            w.setFixedHeight(30)
        self.style_no.setText(initial.get("style_no", ""))
        self.factory.setText(initial.get("factory", ""))

        # 금액 4개 한줄
        price_row = QWidget(self)
        grid = QGridLayout(price_row)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)

        self.cost = MoneyLineEdit(self)
        self.labor = MoneyLineEdit(self)
        self.loss = MoneyLineEdit(self)
        self.sale_price = MoneyLineEdit(self)

        self.cost.setText(initial.get("cost_display", ""))
        self.labor.setText(initial.get("labor_display", ""))
        self.loss.setText(initial.get("loss_display", ""))
        self.sale_price.setText(initial.get("sale_price_display", ""))

        for e in (self.cost, self.labor, self.loss, self.sale_price):
            e.setMinimumWidth(90)
            e.setMaximumWidth(140)

        pairs = [
            ("원가", self.cost),
            ("공임", self.labor),
            ("로스", self.loss),
            ("판매가", self.sale_price),
        ]

        col = 0
        for label_text, edit in pairs:
            lbl = QLabel(label_text, self)
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            grid.addWidget(lbl, 0, col)
            grid.addWidget(edit, 0, col + 1)
            col += 2

        # 원가/공임/로스 변경 시 판매가 자동 합산 표시
        self.cost.textChanged.connect(self._sync_sale_price)
        self.labor.textChanged.connect(self._sync_sale_price)
        self.loss.textChanged.connect(self._sync_sale_price)

        form.addRow("날짜", date_row)
        form.addRow("제품명", self.style_no)
        form.addRow("공장", self.factory)
        form.addRow("", price_row)
        root.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_cancel = make_dialog_button("취소", self)
        btn_ok = make_dialog_button("확인", self)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        root.addLayout(btn_row)

        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)

        # 초기값이 있어도 합산 규칙 적용(원가/공임/로스가 채워져 있으면 판매가를 맞춤)
        self._sync_sale_price()

    def _open_calendar(self):
        # Close existing popup if open
        if getattr(self, "_calendar_popup", None) is not None:
            try:
                self._calendar_popup.close()
            except Exception:
                pass
            self._calendar_popup = None

        popup = _CalendarPopup(self._date_value, self)
        self._calendar_popup = popup

        def _apply_date(d: QDate):
            if d and d.isValid():
                self._date_value = d
                self.date_text.setText(self._date_value.toString("yyyy-MM-dd"))

        popup.datePicked.connect(_apply_date)

        # Position popup right below the date row (label/button)
        anchor = self.date_text
        global_pos = anchor.mapToGlobal(QPoint(0, anchor.height() + 2))

        screen = QGuiApplication.screenAt(global_pos) or QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None

        popup.adjustSize()
        w = popup.width()
        h = popup.height()

        x = global_pos.x()
        y = global_pos.y()

        if avail is not None:
            if x + w > avail.right():
                x = max(avail.left(), avail.right() - w)
            if y + h > avail.bottom():
                # If not enough space below, show above
                y = max(avail.top(), anchor.mapToGlobal(QPoint(0, 0)).y() - h - 2)

        popup.move(x, y)
        popup.show()

    def _sync_sale_price(self):
        total = (
            _safe_int_from_digits(self.cost.value_digits())
            + _safe_int_from_digits(self.labor.value_digits())
            + _safe_int_from_digits(self.loss.value_digits())
        )
        # 원가/공임/로스가 모두 비었으면 판매가를 강제로 비우지 않고 그대로 둠
        if (
            not self.cost.value_digits()
            and not self.labor.value_digits()
            and not self.loss.value_digits()
        ):
            return

        self.sale_price.blockSignals(True)
        try:
            self.sale_price.setText(f"{total:,}" if total else "")
        finally:
            self.sale_price.blockSignals(False)

    def get_data(self) -> Dict[str, str]:
        return {
            "date": self._date_value.toString("yyyy-MM-dd"),
            "style_no": self.style_no.text().strip(),
            "factory": self.factory.text().strip(),
            "cost_display": self.cost.text(),
            "labor_display": self.labor.text(),
            "loss_display": self.loss.text(),
            "sale_price_display": self.sale_price.text(),
            "cost": self.cost.value_digits(),
            "labor": self.labor.value_digits(),
            "loss": self.loss.value_digits(),
            "sale_price": self.sale_price.value_digits(),
        }
