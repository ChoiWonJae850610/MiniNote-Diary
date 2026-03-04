# ui/postit_widgets.py
from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, QRectF, Signal, QSize, QDate, QRegularExpression, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QFontMetrics, QRegularExpressionValidator, QIcon, QPixmap
try:
    from PySide6.QtSvg import QSvgRenderer
except Exception:  # QtSvg might be unavailable
    QSvgRenderer = None
from PySide6.QtCore import QByteArray
from PySide6.QtWidgets import QWidget, QToolButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QDialog, QCalendarWidget, QGraphicsDropShadowEffect, QPlainTextEdit, QSizePolicy


def _color(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#FFF2A8")  # 노랑
    if kind == "fabric":
        return QColor("#CFF4FF")  # 하늘
    return QColor("#E6D7FF")  # 보라


def _border(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#E4D27D")
    if kind == "fabric":
        return QColor("#9AD7E8")
    return QColor("#C0A6FF")


def _krw(v: str) -> str:
    """원화 표기: '원' 접미사."""
    v = (v or "").strip()
    if not v:
        return ""
    if v.endswith("원"):
        return v
    return f"{v}원"


def _safe(v: str) -> str:
    return (v or "").strip()


def _hi_rect(p: QPainter, x: int, y: int, w: int, h: int, color: QColor, radius: int = 8, alpha: int = 150):
    """형광펜 하이라이트(반투명 배경)."""
    c = QColor(color)
    c.setAlpha(alpha)
    p.setPen(Qt.NoPen)
    p.setBrush(c)
    p.drawRoundedRect(QRectF(x, y, w, h), radius, radius)


def _hi_text(p: QPainter, x: int, baseline_y: int, text: str, font: QFont, color: QColor, pad_x: int = 10):
    """
    요청 반영:
    - 한 줄 전체가 아니라 "글씨가 있는 길이까지만" 하이라이트.
    - baseline_y 기준으로 폰트 metrics로 박스 높이/위치 계산.
    """
    if not text:
        return

    fm = QFontMetrics(font)
    text_w = fm.horizontalAdvance(text)
    box_h = fm.height() + 6

    # baseline_y -> box_y: ascent를 이용해 텍스트 위쪽으로 올림
    box_y = baseline_y - fm.ascent() - 3
    box_x = x - 6
    box_w = text_w + pad_x

    _hi_rect(p, box_x, box_y, box_w, box_h, color)


# ===== 강조 색상(요청 반영: 더 밝고 톡톡 튀는 형광 느낌)
# - 날짜: 형광 라임
# - 제품명: 형광 시안/블루
# - 판매가/총액(같은색): 형광 핫핑크(레드 계열)
H_DATE = QColor("#7CFF65")     # neon lime
H_PRODUCT = QColor("#4DD9FF")  # neon cyan
H_MONEY = QColor("#FF4D6D")    # neon hot pink/red

CALENDAR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
<rect x="3" y="4" width="18" height="17" rx="2" stroke="#222" stroke-width="1.6"/>
<path d="M8 2v4M16 2v4" stroke="#222" stroke-width="1.6" stroke-linecap="round"/>
<path d="M3 9h18" stroke="#222" stroke-width="1.6"/>
<rect x="7" y="12" width="3" height="3" rx="0.6" fill="#222"/>
<rect x="12" y="12" width="3" height="3" rx="0.6" fill="#222" opacity="0.55"/>
<rect x="17" y="12" width="0" height="0" fill="none"/>
</svg>"""

def _calendar_icon(size: int = 16) -> QIcon:
    # Prefer SVG rendering if QtSvg is available, else fall back to theme icon.
    if QSvgRenderer is not None:
        data = QByteArray(CALENDAR_SVG.encode("utf-8"))
        renderer = QSvgRenderer(data)
        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        renderer.render(p)
        p.end()
        return QIcon(pm)
    icon = QIcon.fromTheme("x-office-calendar")
    if icon.isNull():
        icon = QIcon.fromTheme("view-calendar")
    return icon



class _InlineCalendarPopup(QDialog):
    datePicked = Signal(QDate)

    def __init__(self, initial: QDate, parent=None):
        super().__init__(parent, Qt.Popup)
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(0)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        if initial and initial.isValid():
            self.calendar.setSelectedDate(initial)
        root.addWidget(self.calendar)

        self.calendar.activated.connect(self._on_activated)

    def _on_activated(self, d: QDate):
        if d and d.isValid():
            self.datePicked.emit(d)
        self.close()


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def _format_commas_from_digits(digits: str) -> str:
    if not digits:
        return ""
    try:
        return f"{int(digits):,}"
    except Exception:
        return digits


class _MoneyLineEdit(QLineEdit):
    """숫자/콤마 입력 + 자동 콤마 포맷."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrame(False)
        self.setReadOnly(True)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9,]*"), self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
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

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.isReadOnly():
            self.setReadOnly(False)
            self.setFocus(Qt.MouseFocusReason)
            self.selectAll()

    def focusOutEvent(self, event):
        if not self.isReadOnly():
            self.setReadOnly(True)
        super().focusOutEvent(event)

    def value_digits(self) -> str:
        return _digits_only(self.text())


class _ClickToEditLineEdit(QLineEdit):
    """기본은 readOnly. 클릭하면 편집, Enter/포커스 아웃 시 저장(=editingFinished)."""

    committed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrame(False)
        self.setReadOnly(True)
        self.setCursor(Qt.IBeamCursor)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.isReadOnly():
            self.setReadOnly(False)
            self.setFocus(Qt.MouseFocusReason)
            self.selectAll()

    def focusOutEvent(self, event):
        # 편집 종료 시 readOnly로 복귀
        if not self.isReadOnly():
            self.setReadOnly(True)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        # Enter/Return -> commit
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not self.isReadOnly():
                self.setReadOnly(True)
                self.committed.emit(self.text().strip())
            event.accept()
            return
        super().keyPressEvent(event)

class BasicInfoPostIt(QWidget):
    edit_requested = Signal()
    """기본정보 포스트잇 (인라인 편집)"""

    data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kind = "basic"
        self.header: Dict[str, str] = {}
        self._loading = False
        self._date_value = QDate.currentDate()

        self.setMinimumHeight(175)
        self.setObjectName("BasicInfoPostIt")
        self.setStyleSheet(
            "#BasicInfoPostIt{background:%s;border:1px solid %s;border-radius:12px;}"
            % (_color("basic").name(), _border("basic").name())
        )
        # 포스트잇 느낌: 약한 그림자
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)
        # paper-like look
        self.setStyleSheet(
            'QWidget#BasicInfoPostIt{background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FFF7C4, stop:1 #FFEFA3);'
            'border: 1px solid rgba(0,0,0,0.18); border-radius: 16px;}'
        )


        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        # 상단: 제목
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(6)
        title = QLabel("기본정보", self)
        title.setStyleSheet("QLabel{font-weight:700;}")
        top.addWidget(title)
        top.addStretch(1)

        outer.addLayout(top)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        # 날짜 (표시 라벨 + 달력 버튼)
        lbl_date = QLabel("날짜:", self)
        lbl_date.setStyleSheet("QLabel{font-weight:600;}")
        self.date_text = QLabel(self)
        self.date_text.setMinimumHeight(28)
        self.date_text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.date_text.setStyleSheet(
            "QLabel{color:#111;background:rgba(255,255,255,0.55);border:1px solid rgba(0,0,0,0.22);border-radius:8px;padding:3px 8px;}"
        )

        self.btn_calendar = QToolButton(self)
        self.btn_calendar.setFixedSize(26, 26)
        self.btn_calendar.setToolTip("날짜 변경")
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.setAutoRaise(True)
        self.btn_calendar.setStyleSheet("QToolButton{border:none;background:transparent;}QToolButton:hover{background:rgba(0,0,0,0.08);border-radius:6px;}")
        icon = QIcon.fromTheme("x-office-calendar")
        if icon.isNull():
            icon = QIcon.fromTheme("view-calendar")
        if not icon.isNull():
            self.btn_calendar.setIcon(icon)
            self.btn_calendar.setIconSize(QSize(16, 16))
            self.btn_calendar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        else:
            self.btn_calendar.setIcon(_calendar_icon(16))
        self.btn_calendar.setIconSize(QSize(16,16))
        self.btn_calendar.clicked.connect(self._open_calendar_popup)

        date_row = QHBoxLayout()
        date_row.setContentsMargins(0, 0, 0, 0)
        date_row.setSpacing(6)
        date_row.addWidget(self.date_text, 1)
        date_row.addWidget(self.btn_calendar)

        date_wrap = QWidget(self)
        date_wrap.setLayout(date_row)

        grid.addWidget(lbl_date, 0, 0)
        grid.addWidget(date_wrap, 0, 1, 1, 3)

        # 제품명 / 공장 (클릭해서 편집)
        self.style_no = _ClickToEditLineEdit(self)
        self.factory = _ClickToEditLineEdit(self)
        for w in (self.style_no, self.factory):
            w.setMinimumHeight(24)
            w.setStyleSheet("QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;}QLineEdit[readOnly=\"true\"]{background:transparent;color:#111;}QLineEdit:focus{background:rgba(255,255,255,0.65);border:1px solid rgba(0,0,0,0.25);border-radius:6px;padding:3px 6px;}")

        lbl_style = QLabel("제품명:", self)
        lbl_style.setStyleSheet("QLabel{font-weight:600;}")
        lbl_factory = QLabel("공장:", self)
        lbl_factory.setStyleSheet("QLabel{font-weight:600;}")

        grid.addWidget(lbl_style, 1, 0)
        grid.addWidget(self.style_no, 1, 1, 1, 3)
        grid.addWidget(lbl_factory, 2, 0)
        grid.addWidget(self.factory, 2, 1, 1, 3)

        # 금액 (원가/공임/로스/판매가)
        self.cost = _MoneyLineEdit(self)
        self.labor = _MoneyLineEdit(self)
        self.loss = _MoneyLineEdit(self)
        self.sale_price = _MoneyLineEdit(self)
        for w in (self.cost, self.labor, self.loss, self.sale_price):
            w.setMinimumHeight(24)
            w.setStyleSheet("QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;}QLineEdit[readOnly=\"true\"]{background:transparent;color:#111;}QLineEdit:focus{background:rgba(255,255,255,0.65);border:1px solid rgba(0,0,0,0.25);border-radius:6px;padding:3px 6px;}")

        grid.addWidget(QLabel("원가:", self), 3, 0)
        grid.addWidget(self.cost, 3, 1)
        grid.addWidget(QLabel("공임:", self), 3, 2)
        grid.addWidget(self.labor, 3, 3)

        grid.addWidget(QLabel("로스:", self), 4, 0)
        grid.addWidget(self.loss, 4, 1)
        grid.addWidget(QLabel("판매가:", self), 4, 2)
        grid.addWidget(self.sale_price, 4, 3)

        outer.addLayout(grid)

        # 이벤트 연결
        self.style_no.editingFinished.connect(self._commit_text_fields)
        self.factory.editingFinished.connect(self._commit_text_fields)

        self.cost.textChanged.connect(self._sync_sale_price_from_parts)
        self.labor.textChanged.connect(self._sync_sale_price_from_parts)
        self.loss.textChanged.connect(self._sync_sale_price_from_parts)

        self.cost.editingFinished.connect(self._commit_money_fields)
        self.labor.editingFinished.connect(self._commit_money_fields)
        self.loss.editingFinished.connect(self._commit_money_fields)
        self.sale_price.editingFinished.connect(self._commit_money_fields)

        self.setVisible(False)

    def sizeHint(self) -> QSize:
        return QSize(360, 190)

    def set_header_data(self, header: Dict[str, str]):
        self._loading = True
        try:
            self.header = header or {}

            # 날짜
            d = QDate.fromString(self.header.get("date", ""), "yyyy-MM-dd")
            if not d.isValid():
                d = QDate.currentDate()
            self._date_value = d
            self.date_text.setText(self._date_value.toString("yyyy-MM-dd"))

            # 텍스트
            self.style_no.setText(self.header.get("style_no", "") or "")
            self.factory.setText(self.header.get("factory", "") or "")

            # 금액(표시값 우선)
            self.cost.setText(self.header.get("cost_display", "") or "")
            self.labor.setText(self.header.get("labor_display", "") or "")
            self.loss.setText(self.header.get("loss_display", "") or "")
            self.sale_price.setText(self.header.get("sale_price_display", "") or "")

            # visibility: change_note 제외
            basic_keys = [
                "date", "style_no", "factory",
                "cost_display", "labor_display", "loss_display", "sale_price_display",
                "cost", "labor", "loss", "sale_price",
            ]
            has = any((self.header.get(k, "") or "").strip() for k in basic_keys)
            self.setVisible(True)
        finally:
            self._loading = False

    def _open_calendar_popup(self):
        popup = _InlineCalendarPopup(self._date_value, self)
        popup.datePicked.connect(self._set_date)

        # date field 아래에 띄우기 (화면 밖이면 위로)
        anchor = self.date_text
        global_pos = anchor.mapToGlobal(QPoint(0, anchor.height()))
        popup.adjustSize()

        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = max(geo.left(), min(global_pos.x(), geo.right() - popup.width()))
            y = global_pos.y()
            if y + popup.height() > geo.bottom():
                y = anchor.mapToGlobal(QPoint(0, 0)).y() - popup.height()
            popup.move(x, y)

        popup.show()

    def _set_date(self, d: QDate):
        if not d or not d.isValid():
            return
        self._date_value = d
        self.date_text.setText(self._date_value.toString("yyyy-MM-dd"))
        self.header["date"] = self._date_value.toString("yyyy-MM-dd")
        if not self._loading:
            self.data_changed.emit({"date": self.header["date"]})

    def _commit_text_fields(self):
        if self._loading:
            return
        self.header["style_no"] = (self.style_no.text() or "").strip()
        self.header["factory"] = (self.factory.text() or "").strip()
        self.data_changed.emit({"style_no": self.header["style_no"], "factory": self.header["factory"]})

    def _sync_sale_price_from_parts(self):
        if self._loading:
            return
        # 원가/공임/로스가 모두 비면 강제로 판매가를 비우지 않음
        if not self.cost.value_digits() and not self.labor.value_digits() and not self.loss.value_digits():
            return
        total = 0
        for w in (self.cost, self.labor, self.loss):
            digits = w.value_digits()
            total += int(digits) if digits else 0
        self.sale_price.blockSignals(True)
        try:
            self.sale_price.setText(f"{total:,}" if total else "")
        finally:
            self.sale_price.blockSignals(False)

    def _commit_money_fields(self):
        if self._loading:
            return
        # display
        self.header["cost_display"] = self.cost.text()
        self.header["labor_display"] = self.labor.text()
        self.header["loss_display"] = self.loss.text()
        self.header["sale_price_display"] = self.sale_price.text()
        # digits
        self.header["cost"] = self.cost.value_digits()
        self.header["labor"] = self.labor.value_digits()
        self.header["loss"] = self.loss.value_digits()
        self.header["sale_price"] = self.sale_price.value_digits()

        self.data_changed.emit({
            "cost_display": self.header["cost_display"],
            "labor_display": self.header["labor_display"],
            "loss_display": self.header["loss_display"],
            "sale_price_display": self.header["sale_price_display"],
            "cost": self.header["cost"],
            "labor": self.header["labor"],
            "loss": self.header["loss"],
            "sale_price": self.header["sale_price"],
        })



class PostItCard(QWidget):
    """원단/부자재 1장: 인라인 편집 가능."""

    delete_clicked = Signal(int)
    selected = Signal(int)
    data_changed = Signal(int, dict)   # (index, patch)
    item_created = Signal(dict)        # placeholder -> real item

    def __init__(self, kind: str, index: int, data: Dict[str, str], placeholder: bool = False, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.index = index
        self.data = dict(data or {})
        self.is_active = False
        self.is_placeholder = placeholder

        self.setMouseTracking(True)
        self.setMinimumHeight(135)

        # paper style + shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self._bg = _color(kind)
        self._bd = _border(kind)

        # delete button
        self.btn_delete = QToolButton(self)
        self.btn_delete.setText("×")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setVisible(False)
        self.btn_delete.setFixedSize(20, 20)
        self.btn_delete.setStyleSheet(
            "QToolButton{border:none;border-radius:10px;background:rgba(0,0,0,0.12);font-weight:bold;}"
            "QToolButton:hover{background:rgba(0,0,0,0.22);}"
        )
        self.btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.index))

        # content layout
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(6)

        self.vendor = _ClickToEditLineEdit(self)
        self.vendor.setPlaceholderText("거래처")
        self.vendor.setText(_safe(self.data.get("거래처", "")))

        self.item = _ClickToEditLineEdit(self)
        self.item.setPlaceholderText("품목")
        self.item.setText(_safe(self.data.get("품목", "")))

        row = QGridLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setHorizontalSpacing(8)
        row.setVerticalSpacing(6)

        self.qty = _ClickToEditLineEdit(self)
        self.qty.setPlaceholderText("수량")
        self.qty.setText(_safe(self.data.get("수량", "")))
        self.qty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.unit = _ClickToEditLineEdit(self)
        self.unit.setPlaceholderText("단위")
        self.unit.setText(_safe(self.data.get("단위", "")))

        self.price = _MoneyLineEdit(self)
        self.price.setPlaceholderText("단가")
        self.price.setText(_safe(self.data.get("단가", "")))

        self.total = _MoneyLineEdit(self)
        self.total.setPlaceholderText("총액")
        self.total.setText(_safe(self.data.get("총액", "")))

        row.addWidget(QLabel("수량", self), 0, 0)
        row.addWidget(self.qty, 0, 1)
        row.addWidget(self.unit, 0, 2)

        row.addWidget(QLabel("단가", self), 1, 0)
        row.addWidget(self.price, 1, 1, 1, 2)

        row.addWidget(QLabel("총액", self), 2, 0)
        row.addWidget(self.total, 2, 1, 1, 2)

        lay.addWidget(self.vendor)
        lay.addWidget(self.item)
        lay.addLayout(row)

        # style to look like post-it (not textbox)
        for w in (self.vendor, self.item, self.qty, self.unit, self.price, self.total):
            w.setStyleSheet(
                'QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;} '
                'QLineEdit[readOnly="true"]{background:transparent;color:#111;} '
                'QLineEdit:focus{background:rgba(255,255,255,0.65);border:1px solid rgba(0,0,0,0.25);'
                'border-radius:6px;padding:3px 6px;}'
            )

        # placeholder visual hint
        if self.is_placeholder:
            self.vendor.setPlaceholderText("클릭해서 원단/부자재 입력")
            self.item.setPlaceholderText("")
            self.btn_delete.setEnabled(False)

        # signals
        self.vendor.committed.connect(lambda v: self._commit_field("거래처", v))
        self.item.committed.connect(lambda v: self._commit_field("품목", v))
        self.qty.committed.connect(lambda v: self._commit_field("수량", v))
        self.unit.committed.connect(lambda v: self._commit_field("단위", v))
        self.price.textChanged.connect(lambda _t: self._commit_money("단가", self.price.text()))
        self.total.textChanged.connect(lambda _t: self._commit_money("총액", self.total.text()))

        self._apply_placeholder_delete()

    def _apply_placeholder_delete(self):
        if self.is_placeholder:
            self.btn_delete.setVisible(False)

    def set_active(self, active: bool):
        self.is_active = active
        self.update()

    def _commit_money(self, key: str, display: str):
        # only emit on user edits; MoneyLineEdit will normalize
        self._commit_field(key, display)

    def _commit_field(self, key: str, value: str):
        value = (value or "").strip()
        self.data[key] = value

        # If placeholder and user started typing something, create real item
        if self.is_placeholder and any((self.data.get(k, "") or "").strip() for k in ["거래처", "품목", "수량", "단위", "단가", "총액"]):
            self.is_placeholder = False
            self.item_created.emit(dict(self.data))
            return

        self.data_changed.emit(self.index, {key: value})

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.index)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        if not self.is_placeholder:
            self.btn_delete.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_delete.setVisible(False)
        super().leaveEvent(event)

    def resizeEvent(self, event):
        self.btn_delete.move(self.width() - 28, 10)
        super().resizeEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        bg = QColor(self._bg)
        bd = QColor(self._bd)

        # Slight paper tint gradient
        r = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        if self.is_active:
            pen = QPen(QColor(bd).darker(140), 3)
        else:
            pen = QPen(bd, 2)
        p.setPen(pen)
        p.setBrush(bg)
        p.drawRoundedRect(r, 16, 16)


class PostItStack(QWidget):
    """여러 장을 겹쳐 스택처럼 보이게. 클릭으로 앞으로 가져오기."""

    item_deleted = Signal(int)
    item_changed = Signal(int, dict)
    item_created = Signal(dict)

    def __init__(self, kind: str, title: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.title = title
        self.items: List[Dict[str, str]] = []
        self.cards: List[PostItCard] = []
        self.active_index: int = -1
        self.setMinimumHeight(170)

    def sizeHint(self) -> QSize:
        return QSize(330, 175)

    def set_items(self, items: List[Dict[str, str]]):
        self.items = list(items or [])
        self._placeholder = False
        if not self.items:
            self.items = [{}]
            self.active_index = 0
            self._placeholder = True
        # 새로 세팅될 때, 활성 인덱스는 가능한 범위로 보정
        if not self.items:
            self.active_index = -1
        else:
            if self.active_index < 0 or self.active_index >= len(self.items):
                self.active_index = len(self.items) - 1  # 기본은 최신(맨 위) 카드
        self._rebuild()

    def _rebuild(self):
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        self.cards = []

        for idx, it in enumerate(self.items):
            card = PostItCard(self.kind, idx, it, placeholder=getattr(self, '_placeholder', False) and idx == 0, parent=self)
            card.delete_clicked.connect(self._on_delete_clicked)
            card.selected.connect(self.set_active_card)
            card.data_changed.connect(self.item_changed.emit)
            card.item_created.connect(self._on_item_created)
            card.show()
            self.cards.append(card)

        self._layout_cards()
        self._apply_active_state()
        self.update()

    def set_active_card(self, idx: int):
        if idx < 0 or idx >= len(self.cards):
            return
        self.active_index = idx
        self._apply_active_state()
        # 활성 카드가 앞으로 오도록 raise
        self.cards[idx].raise_()
        self.update()

    def _apply_active_state(self):
        for i, c in enumerate(self.cards):
            c.set_active(i == self.active_index)

    
    def _on_delete_clicked(self, idx: int):
        # placeholder는 삭제 불가
        if getattr(self, '_placeholder', False):
            return
        self.item_deleted.emit(idx)

    def _on_item_created(self, data: Dict[str, str]):
        # placeholder에서 실제 아이템 생성
        self._placeholder = False
        self.item_created.emit(data)

    def resizeEvent(self, event):
        self._layout_cards()
        super().resizeEvent(event)

    def _layout_cards(self):
        base_w = self.width()
        card_w = max(280, min(330, base_w - 20))
        card_h = 135
        x0 = int((base_w - card_w) / 2)
        y0 = 10  # 라벨 제거했으니 위로
        dx = 10
        dy = 16

        for i, card in enumerate(self.cards):
            card.setFixedSize(card_w, card_h)
            card.move(x0 + dx * i, y0 + dy * i)
            card.raise_()

        # 활성 카드가 있으면 마지막에 한 번 더 raise해서 확실히 맨 위로
        if 0 <= self.active_index < len(self.cards):
            self.cards[self.active_index].raise_()

        total_h = y0 + card_h + dy * max(0, (len(self.cards) - 1)) + 14
        self.setMinimumHeight(max(155, total_h))

    def paintEvent(self, event):
        # 포스트잇 위 "원단정보/부자재정보" 라벨 제거
        return


class PostItBar(QWidget):
    """기본정보-원단정보-부자재정보 가로 1열"""

    fabric_deleted = Signal(int)
    trim_deleted = Signal(int)
    fabric_item_changed = Signal(int, dict)
    trim_item_changed = Signal(int, dict)
    fabric_item_created = Signal(dict)
    trim_item_created = Signal(dict)
    basic_edit_requested = Signal()
    basic_data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.basic = BasicInfoPostIt()
        self.basic.edit_requested.connect(self.basic_edit_requested.emit)
        self.basic.data_changed.connect(self.basic_data_changed.emit)

        self.fabric = PostItStack(kind="fabric", title="원단정보")
        self.trim = PostItStack(kind="trim", title="부자재정보")

        self.fabric.item_deleted.connect(self.fabric_deleted.emit)
        self.trim.item_deleted.connect(self.trim_deleted.emit)
        self.fabric.item_changed.connect(self.fabric_item_changed.emit)
        self.trim.item_changed.connect(self.trim_item_changed.emit)
        self.fabric.item_created.connect(self.fabric_item_created.emit)
        self.trim.item_created.connect(self.trim_item_created.emit)

        layout.addWidget(self.basic, 1)
        layout.addWidget(self.fabric, 1)
        layout.addWidget(self.trim, 1)


    def set_data(self, header: Dict[str, str], fabrics: List[Dict[str, str]], trims: List[Dict[str, str]]):
        self.basic.set_header_data(header or {})
        self.fabric.set_items(fabrics or [])
        self.trim.set_items(trims or [])

class ChangeNotePostIt(QWidget):
    """수정사항 메모 포스트잇: 항상 자리 차지 + 인라인 편집."""

    text_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._block = False
        self.setMinimumHeight(220)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self.setStyleSheet(
            "ChangeNotePostIt {"
            "  background: #DFF6E3;"
            "  border: 1px solid #A5D6A7;"
            "  border-radius: 16px;"
            "}"
            "QLabel { color:#1B5E20; font-weight:600; }"
        )

        title = QLabel("수정사항", self)
        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("클릭해서 수정사항을 입력하세요")
        self.editor.setTabChangesFocus(True)
        self.editor.setStyleSheet(
            "QPlainTextEdit{background:transparent;border:none;color:#222;font-size:12px;}"
            "QPlainTextEdit:focus{background:rgba(255,255,255,0.55);border:1px solid rgba(0,0,0,0.18);border-radius:10px;padding:6px;}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(8)
        lay.addWidget(title)
        lay.addWidget(self.editor, 1)

        self.editor.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        if self._block:
            return
        self.text_changed.emit(self.text())

    def set_text(self, text: str):
        self._block = True
        try:
            self.editor.setPlainText(text or "")
        finally:
            self._block = False

    def text(self) -> str:
        return self.editor.toPlainText().rstrip()
