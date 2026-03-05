# ui/postit_widgets.py
from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, QRectF, Signal, QSize, QDate, QPoint, QRegularExpression
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QFont,
    QFontMetrics,
    QRegularExpressionValidator,
    QIcon,
    QPixmap,
)
from PySide6.QtWidgets import (
    QWidget,
    QToolButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QDialog,
    QCalendarWidget,
    QGraphicsDropShadowEffect,
    QPlainTextEdit,
    QSizePolicy,
)

try:
    from PySide6.QtSvg import QSvgRenderer  # type: ignore
    from PySide6.QtCore import QByteArray
except Exception:
    QSvgRenderer = None
    QByteArray = None


# ---------- Visual constants ----------
FIELD_H = 26
CARD_RADIUS = 16
SHADOW_BLUR = 18
SHADOW_OFFSET_Y = 6

# highlight accents
H_DATE = QColor("#7CFF65")     # neon lime
H_PRODUCT = QColor("#4DD9FF")  # neon cyan
H_MONEY = QColor("#FF4D6D")    # neon hot pink/red

# card base colors
def _card_bg(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#FFF4A3")
    if kind == "fabric":
        return QColor("#CFF4FF")
    if kind == "trim":
        return QColor("#E6D7FF")
    if kind == "change":
        return QColor("#DFF6E3")
    return QColor("#FFF4A3")


def _card_border(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#D8C86A")
    if kind == "fabric":
        return QColor("#9AD7E8")
    if kind == "trim":
        return QColor("#C0A6FF")
    if kind == "change":
        return QColor("#A5D6A7")
    return QColor("#D8C86A")


def _safe(v: str) -> str:
    return (v or "").strip()


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
    d = _digits_only(digits)
    return int(d) if d else 0


CALENDAR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
<rect x="3" y="4" width="18" height="17" rx="2" stroke="#222" stroke-width="1.6"/>
<path d="M8 2v4M16 2v4" stroke="#222" stroke-width="1.6" stroke-linecap="round"/>
<path d="M3 9h18" stroke="#222" stroke-width="1.6"/>
<rect x="7" y="12" width="3" height="3" rx="0.6" fill="#222"/>
<rect x="12" y="12" width="3" height="3" rx="0.6" fill="#222" opacity="0.55"/>
</svg>"""


def _calendar_icon(size: int = 16) -> QIcon:
    # Prefer SVG rendering if QtSvg is available, else fall back to theme icon.
    if QSvgRenderer is not None and QByteArray is not None:
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
    if icon.isNull():
        icon = QIcon.fromTheme("office-calendar")
    return icon


# ---------- Small popup calendar ----------
class _InlineCalendarPopup(QDialog):
    datePicked = Signal(QDate)

    def __init__(self, initial: QDate, parent=None):
        super().__init__(parent, Qt.Popup)
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        cal = QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        if initial and initial.isValid():
            cal.setSelectedDate(initial)
        root.addWidget(cal)

        cal.activated.connect(self._on_activated)
        self._cal = cal

    def _on_activated(self, d: QDate):
        if d and d.isValid():
            self.datePicked.emit(d)
        self.close()


# ---------- Inline editors ----------
class _MoneyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9,]*"), self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setFixedHeight(FIELD_H)
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


class _ClickToEditLineEdit(QLineEdit):
    committed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(FIELD_H)
        self.setReadOnly(True)
        self._block = False

        # default: looks like label
        self._apply_readonly_style(True)

    def _apply_readonly_style(self, ro: bool):
        if ro:
            self.setStyleSheet(
                'QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;}'
                'QLineEdit:hover{background:rgba(255,255,255,0.18);border-radius:6px;}'
            )
        else:
            self.setStyleSheet(
                'QLineEdit{background:rgba(255,255,255,0.70);border:1px solid rgba(0,0,0,0.22);'
                'border-radius:8px;padding:3px 8px;color:#111;}'
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isReadOnly():
                self.setReadOnly(False)
                self._apply_readonly_style(False)
                self.setFocus()
                self.selectAll()
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._commit_and_lock()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._commit_and_lock()
            event.accept()
            return
        if event.key() == Qt.Key_Escape:
            # cancel edit (just lock)
            self.setReadOnly(True)
            self._apply_readonly_style(True)
            event.accept()
            return
        super().keyPressEvent(event)

    def _commit_and_lock(self):
        if self._block:
            return
        if not self.isReadOnly():
            self.setReadOnly(True)
            self._apply_readonly_style(True)
            self.committed.emit(self.text())

    def set_text_silent(self, text: str):
        self._block = True
        try:
            self.setText(text)
        finally:
            self._block = False


# ---------- Base card widget ----------
class _PostItCardBase(QWidget):
    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self._bg = _card_bg(kind)
        self._bd = _card_border(kind)
        self._active = False

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(SHADOW_BLUR)
        shadow.setOffset(0, SHADOW_OFFSET_Y)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self.setAttribute(Qt.WA_StyledBackground, True)

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        r = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)

        pen = QPen(self._bd, 2)
        if self._active:
            pen = QPen(QColor(self._bd).darker(140), 3)

        p.setPen(pen)
        p.setBrush(self._bg)
        p.drawRoundedRect(r, CARD_RADIUS, CARD_RADIUS)


# ---------- Basic info (yellow) ----------
class BasicInfoPostIt(_PostItCardBase):
    edit_requested = Signal()     # compatibility (unused)
    data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(kind="basic", parent=parent)
        self.setMinimumSize(QSize(320, 175))

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("기본정보", self)
        title.setStyleSheet("QLabel{font-weight:700;color:#222;}")
        root.addWidget(title)

        # date row
        date_row = QHBoxLayout()
        date_row.setContentsMargins(0, 0, 0, 0)
        date_row.setSpacing(6)

        lbl_date = QLabel("날짜:", self)
        lbl_date.setFixedWidth(44)
        lbl_date.setStyleSheet("QLabel{font-weight:600;color:#222;}")
        date_row.addWidget(lbl_date)

        self.date_text = QLabel(self)
        self.date_text.setFixedHeight(FIELD_H)
        self.date_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_text.setStyleSheet(
            "QLabel{background:rgba(255,255,255,0.65);border:1px solid rgba(0,0,0,0.18);"
            "border-radius:8px;padding:0 8px;color:#111;}"
        )
        self.date_text.setMinimumWidth(118)

        self.btn_calendar = QToolButton(self)
        self.btn_calendar.setIcon(_calendar_icon(16))
        self.btn_calendar.setIconSize(QSize(16, 16))
        self.btn_calendar.setFixedSize(FIELD_H, FIELD_H)
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.setStyleSheet(
            "QToolButton{border:1px solid rgba(0,0,0,0.18);border-radius:8px;background:rgba(255,255,255,0.55);}"
            "QToolButton:hover{background:rgba(255,255,255,0.75);}"
        )
        self.btn_calendar.clicked.connect(self._open_calendar)

        date_row.addWidget(self.date_text, 1)
        date_row.addWidget(self.btn_calendar)
        root.addLayout(date_row)

        # simple text fields
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        def mk_label(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setStyleSheet("QLabel{font-weight:600;color:#222;}")
            return l

        self.style_no = _ClickToEditLineEdit(self)
        self.style_no.setPlaceholderText("클릭해서 입력")
        self.factory = _ClickToEditLineEdit(self)
        self.factory.setPlaceholderText("클릭해서 입력")

        # auto width for style_no
        self.style_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._style_no_min = 140
        self._style_no_max = 320
        self.style_no.textChanged.connect(self._adjust_style_no_width)
        self._adjust_style_no_width(self.style_no.text())

        grid.addWidget(mk_label("제품명:"), 0, 0)
        grid.addWidget(self.style_no, 0, 1)
        grid.addWidget(mk_label("공장:"), 1, 0)
        grid.addWidget(self.factory, 1, 1)

        root.addLayout(grid)

        # money grid (2x2)
        mg = QGridLayout()
        mg.setContentsMargins(0, 0, 0, 0)
        mg.setHorizontalSpacing(8)
        mg.setVerticalSpacing(8)

        def mk_money_label(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setStyleSheet("QLabel{font-weight:600;color:#222;}")
            return l

        self.cost = _MoneyLineEdit(self)
        self.labor = _MoneyLineEdit(self)
        self.loss = _MoneyLineEdit(self)
        self.sale_price = _MoneyLineEdit(self)

        # Make them look "postit-like" (not heavy field)
        for w in (self.cost, self.labor, self.loss, self.sale_price):
            w.setStyleSheet(
                "QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;}"
                "QLineEdit:hover{background:rgba(255,255,255,0.18);border-radius:6px;}"
                "QLineEdit:focus{background:rgba(255,255,255,0.70);border:1px solid rgba(0,0,0,0.22);"
                "border-radius:8px;padding:3px 8px;}"
            )

        mg.addWidget(mk_money_label("원가:"), 0, 0)
        mg.addWidget(self.cost, 0, 1)
        mg.addWidget(mk_money_label("공임:"), 0, 2)
        mg.addWidget(self.labor, 0, 3)

        mg.addWidget(mk_money_label("로스:"), 1, 0)
        mg.addWidget(self.loss, 1, 1)
        mg.addWidget(mk_money_label("판매가:"), 1, 2)
        mg.addWidget(self.sale_price, 1, 3)

        root.addLayout(mg)

        # sync: cost+labor+loss -> sale_price (on change)
        self.cost.textChanged.connect(self._sync_sale_price)
        self.labor.textChanged.connect(self._sync_sale_price)
        self.loss.textChanged.connect(self._sync_sale_price)

        # commit signals for header_data
        self.style_no.committed.connect(lambda v: self._emit_patch({"style_no": _safe(v)}))
        self.factory.committed.connect(lambda v: self._emit_patch({"factory": _safe(v)}))

        self.cost.textChanged.connect(lambda _t: self._emit_money_patch())
        self.labor.textChanged.connect(lambda _t: self._emit_money_patch())
        self.loss.textChanged.connect(lambda _t: self._emit_money_patch())
        self.sale_price.textChanged.connect(lambda _t: self._emit_money_patch())

        # init date
        self._date_value = QDate.currentDate()
        self.date_text.setText(self._date_value.toString("yyyy-MM-dd"))

    def _adjust_style_no_width(self, text: str):
        fm = QFontMetrics(self.style_no.font())
        w = fm.horizontalAdvance(text or "") + 28
        w = max(self._style_no_min, min(self._style_no_max, w))
        self.style_no.setMinimumWidth(w)

    def set_header_data(self, header: Dict[str, str]):
        header = header or {}

        # date
        d = QDate.fromString(header.get("date", ""), "yyyy-MM-dd")
        if not d.isValid():
            d = QDate.currentDate()
        self._date_value = d
        self.date_text.setText(d.toString("yyyy-MM-dd"))

        # text
        self.style_no.set_text_silent(header.get("style_no", ""))
        self.factory.set_text_silent(header.get("factory", ""))

        # money (display fields preferred)
        self.cost.setText(header.get("cost_display", header.get("cost", "")) or "")
        self.labor.setText(header.get("labor_display", header.get("labor", "")) or "")
        self.loss.setText(header.get("loss_display", header.get("loss", "")) or "")
        self.sale_price.setText(header.get("sale_price_display", header.get("sale_price", "")) or "")

        self._adjust_style_no_width(self.style_no.text())

    def _emit_patch(self, patch: dict):
        if "date" not in patch:
            patch["date"] = self._date_value.toString("yyyy-MM-dd")
        self.data_changed.emit(patch)

    def _emit_money_patch(self):
        patch = {
            "cost_display": self.cost.text(),
            "labor_display": self.labor.text(),
            "loss_display": self.loss.text(),
            "sale_price_display": self.sale_price.text(),
            "cost": self.cost.value_digits(),
            "labor": self.labor.value_digits(),
            "loss": self.loss.value_digits(),
            "sale_price": self.sale_price.value_digits(),
            "date": self._date_value.toString("yyyy-MM-dd"),
            "style_no": self.style_no.text(),
            "factory": self.factory.text(),
        }
        self.data_changed.emit(patch)

    def _sync_sale_price(self):
        # always override when any of the 3 changes
        total = _safe_int_from_digits(self.cost.text()) + _safe_int_from_digits(self.labor.text()) + _safe_int_from_digits(self.loss.text())
        self.sale_price.setText(_format_commas_from_digits(str(total)))

    def _open_calendar(self):
        popup = _InlineCalendarPopup(self._date_value, parent=self)
        popup.datePicked.connect(self._on_date_picked)

        # position below date row
        anchor = self.btn_calendar.mapToGlobal(QPoint(0, self.btn_calendar.height() + 4))
        # keep on screen
        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            popup.adjustSize()
            x = min(max(anchor.x(), screen.left() + 6), screen.right() - popup.width() - 6)
            y = anchor.y()
            if y + popup.height() > screen.bottom():
                y = max(screen.top() + 6, anchor.y() - popup.height() - self.btn_calendar.height() - 10)
            popup.move(x, y)
        else:
            popup.move(anchor)
        popup.show()

    def _on_date_picked(self, d: QDate):
        self._date_value = d
        self.date_text.setText(d.toString("yyyy-MM-dd"))
        self._emit_patch({"date": d.toString("yyyy-MM-dd")})


# ---------- Change note (green) ----------
class ChangeNotePostIt(_PostItCardBase):
    text_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(kind="change", parent=parent)
        self.setMinimumSize(QSize(320, 220))
        self._block = False

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)

        title = QLabel("수정사항", self)
        title.setStyleSheet("QLabel{font-weight:700;color:#1B5E20;}")
        root.addWidget(title)

        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("클릭해서 수정사항을 입력하세요")
        self.editor.setStyleSheet(
            "QPlainTextEdit{background:transparent;border:none;color:#222;font-size:12px;}"
            "QPlainTextEdit:focus{background:rgba(255,255,255,0.55);border:1px solid rgba(0,0,0,0.18);"
            "border-radius:12px;padding:8px;}"
        )
        root.addWidget(self.editor, 1)

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


# ---------- Fabric/Trim card ----------
class PostItCard(_PostItCardBase):
    delete_clicked = Signal(int)
    selected = Signal(int)
    data_changed = Signal(int, dict)   # index, patch
    item_created = Signal(dict)        # placeholder -> new item dict

    def __init__(self, kind: str, index: int, data: Dict[str, str], placeholder: bool = False, parent=None):
        super().__init__(kind=kind, parent=parent)
        self.index = index
        self.data = dict(data or {})
        self.is_placeholder = placeholder

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)

        # delete button (top-right)
        self.btn_delete = QToolButton(self)
        self.btn_delete.setText("×")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setFixedSize(20, 20)
        self.btn_delete.setStyleSheet(
            "QToolButton{border:none;border-radius:10px;background:rgba(0,0,0,0.12);font-weight:bold;}"
            "QToolButton:hover{background:rgba(0,0,0,0.22);}"
        )
        self.btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.index))
        self.btn_delete.setVisible(not self.is_placeholder)

        # placeholder label
        self.placeholder_label = QLabel("클릭해서 원단/부자재 입력", self)
        self.placeholder_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.placeholder_label.setStyleSheet("QLabel{color:rgba(0,0,0,0.55);font-weight:600;}")

        # editable fields
        self.vendor = _ClickToEditLineEdit(self)
        self.vendor.setPlaceholderText("거래처")
        self.item = _ClickToEditLineEdit(self)
        self.item.setPlaceholderText("품목")

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        def mk_lbl(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setStyleSheet("QLabel{font-weight:600;color:#222;}")
            return l

        self.qty = _ClickToEditLineEdit(self)
        self.qty.setPlaceholderText("")
        self.qty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.unit = _ClickToEditLineEdit(self)
        self.unit.setPlaceholderText("")

        self.price = _MoneyLineEdit(self)
        self.total = _MoneyLineEdit(self)

        # Make money edits postit-like
        for w in (self.price, self.total):
            w.setStyleSheet(
                "QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;}"
                "QLineEdit:hover{background:rgba(255,255,255,0.18);border-radius:6px;}"
                "QLineEdit:focus{background:rgba(255,255,255,0.70);border:1px solid rgba(0,0,0,0.22);"
                "border-radius:8px;padding:3px 8px;}"
            )

        grid.addWidget(mk_lbl("수량"), 0, 0)
        grid.addWidget(self.qty, 0, 1)
        grid.addWidget(mk_lbl("단위"), 0, 2)
        grid.addWidget(self.unit, 0, 3)

        grid.addWidget(mk_lbl("단가"), 1, 0)
        grid.addWidget(self.price, 1, 1, 1, 3)

        grid.addWidget(mk_lbl("총액"), 2, 0)
        grid.addWidget(self.total, 2, 1, 1, 3)

        self._grid_widget = QWidget(self)
        self._grid_widget.setLayout(grid)

        root.addWidget(self.placeholder_label)
        root.addWidget(self.vendor)
        root.addWidget(self.item)
        root.addWidget(self._grid_widget)

        # data fill
        self.vendor.set_text_silent(_safe(self.data.get("거래처", "")))
        self.item.set_text_silent(_safe(self.data.get("품목", "")))
        self.qty.set_text_silent(_safe(self.data.get("수량", "")))
        self.unit.set_text_silent(_safe(self.data.get("단위", "")))
        self.price.setText(_safe(self.data.get("단가", "")))
        self.total.setText(_safe(self.data.get("총액", "")))

        # placeholder mode
        self._apply_placeholder_mode(self.is_placeholder)

        # connections
        self.vendor.committed.connect(lambda v: self._commit_field("거래처", v))
        self.item.committed.connect(lambda v: self._commit_field("품목", v))
        self.qty.committed.connect(lambda v: self._commit_field("수량", v))
        self.unit.committed.connect(lambda v: self._commit_field("단위", v))

        self.price.textChanged.connect(lambda _t: self._commit_field("단가", self.price.text()))
        self.total.textChanged.connect(lambda _t: self._commit_field("총액", self.total.text()))

    def _apply_placeholder_mode(self, placeholder: bool):
        self.is_placeholder = placeholder
        self.btn_delete.setVisible(not placeholder)
        self.vendor.setVisible(not placeholder)
        self.item.setVisible(not placeholder)
        self._grid_widget.setVisible(not placeholder)
        self.placeholder_label.setVisible(True)
        if placeholder:
            self.placeholder_label.setText("클릭해서 원단/부자재 입력")
        else:
            self.placeholder_label.setText("")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.index)
            # If placeholder: activate first field to start creating
            if self.is_placeholder:
                self._apply_placeholder_mode(False)
                self.vendor.setReadOnly(False)
                self.vendor.setFocus()
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        self.btn_delete.move(self.width() - 28, 10)
        super().resizeEvent(event)

    def _commit_field(self, key: str, value: str):
        value = (value or "").strip()
        self.data[key] = value

        # If this was placeholder-origin, create when any value is entered
        if (self.index < 0) or ("__placeholder__" in self.data):
            pass

        if self.is_placeholder:
            # When placeholder was clicked, we turned it off; create if something exists
            if any((self.data.get(k, "") or "").strip() for k in ["거래처", "품목", "수량", "단위", "단가", "총액"]):
                self.item_created.emit(dict(self.data))
                return

        self.data_changed.emit(self.index, {key: value})


# ---------- Stack (fabric/trim) ----------
class PostItStack(QWidget):
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
        self.setMinimumHeight(175)

    def sizeHint(self) -> QSize:
        return QSize(330, 175)

    def set_items(self, items: List[Dict[str, str]]):
        self.items = list(items or [])
        # always include a placeholder card at the end for quick add
        self._rebuild()

    def _rebuild(self):
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        self.cards = []

        # create cards for items
        for idx, it in enumerate(self.items):
            card = PostItCard(self.kind, idx, it, placeholder=False, parent=self)
            card.delete_clicked.connect(self.item_deleted.emit)
            card.selected.connect(self.set_active_card)
            card.data_changed.connect(self.item_changed.emit)
            card.show()
            self.cards.append(card)

        # placeholder card (index == len(items))
        ph = PostItCard(self.kind, len(self.items), {}, placeholder=True, parent=self)
        ph.selected.connect(self.set_active_card)
        ph.item_created.connect(self._on_item_created)
        ph.show()
        self.cards.append(ph)

        # active index
        if self.items:
            if self.active_index < 0 or self.active_index >= len(self.items):
                self.active_index = len(self.items) - 1
        else:
            self.active_index = len(self.cards) - 1  # placeholder

        self._layout_cards()
        self._apply_active_state()
        self.update()

    def _on_item_created(self, data: Dict[str, str]):
        self.item_created.emit(data)

    def set_active_card(self, idx: int):
        if idx < 0 or idx >= len(self.cards):
            return
        self.active_index = idx
        self._apply_active_state()
        self.cards[idx].raise_()
        self.update()

    def _apply_active_state(self):
        for i, c in enumerate(self.cards):
            c.set_active(i == self.active_index)

    def resizeEvent(self, event):
        self._layout_cards()
        super().resizeEvent(event)

    def _layout_cards(self):
        base_w = self.width()
        card_w = max(280, min(340, base_w - 20))
        card_h = 150
        x0 = int((base_w - card_w) / 2)
        y0 = 10
        dx = 10
        dy = 16

        for i, card in enumerate(self.cards):
            card.setFixedSize(card_w, card_h)
            card.move(x0 + dx * i, y0 + dy * i)
            card.raise_()

        if 0 <= self.active_index < len(self.cards):
            self.cards[self.active_index].raise_()

        total_h = y0 + card_h + dy * max(0, (len(self.cards) - 1)) + 14
        self.setMinimumHeight(max(175, total_h))

    def paintEvent(self, event):
        # no extra title painting (kept clean)
        return


# ---------- Bar (basic + fabric + trim) ----------
class PostItBar(QWidget):
    fabric_deleted = Signal(int)
    trim_deleted = Signal(int)

    fabric_item_changed = Signal(int, dict)
    trim_item_changed = Signal(int, dict)
    fabric_item_created = Signal(dict)
    trim_item_created = Signal(dict)

    basic_edit_requested = Signal()  # compatibility
    basic_data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.basic = BasicInfoPostIt(self)
        self.basic.edit_requested.connect(self.basic_edit_requested.emit)
        self.basic.data_changed.connect(self.basic_data_changed.emit)

        self.fabric = PostItStack(kind="fabric", title="원단정보", parent=self)
        self.trim = PostItStack(kind="trim", title="부자재정보", parent=self)

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
