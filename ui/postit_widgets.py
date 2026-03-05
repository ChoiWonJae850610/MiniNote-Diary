# ui/postit_widgets.py
from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, QRectF, Signal, QSize, QDate, QPoint, QRegularExpression
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
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

# Optional QtSvg (for calendar SVG icon)
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


def _bg(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#FFF4A3")
    if kind == "fabric":
        return QColor("#CFF4FF")
    if kind == "trim":
        return QColor("#E6D7FF")
    if kind == "change":
        return QColor("#DFF6E3")
    return QColor("#FFF4A3")


def _bd(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#D8C86A")
    if kind == "fabric":
        return QColor("#9AD7E8")
    if kind == "trim":
        return QColor("#C0A6FF")
    if kind == "change":
        return QColor("#A5D6A7")
    return QColor("#D8C86A")


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def _format_commas(digits: str) -> str:
    if not digits:
        return ""
    try:
        return f"{int(digits):,}"
    except Exception:
        return digits


def _int_from_any(s: str) -> int:
    d = _digits_only(s)
    return int(d) if d else 0


CALENDAR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
<rect x="3" y="4" width="18" height="17" rx="2" stroke="#222" stroke-width="1.6"/>
<path d="M8 2v4M16 2v4" stroke="#222" stroke-width="1.6" stroke-linecap="round"/>
<path d="M3 9h18" stroke="#222" stroke-width="1.6"/>
<rect x="7" y="12" width="3" height="3" rx="0.6" fill="#222"/>
<rect x="12" y="12" width="3" height="3" rx="0.6" fill="#222" opacity="0.55"/>
</svg>"""


def _calendar_icon(size: int = 16) -> QIcon:
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
    return icon


# ---------- Popup calendar ----------
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
        self._fmt = False
        self.textChanged.connect(self._on_text)

    def _on_text(self, t: str):
        if self._fmt:
            return
        digits = _digits_only(t)
        formatted = _format_commas(digits)
        if formatted == t:
            return
        self._fmt = True
        try:
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
        finally:
            self._fmt = False

    def digits(self) -> str:
        return _digits_only(self.text())


class _ClickToEditLineEdit(QLineEdit):
    committed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFixedHeight(FIELD_H)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setTextMargins(0, 0, 0, 0)
        self._apply_style(editing=False)

    def _apply_style(self, editing: bool):
        if not editing:
            self.setStyleSheet(
                "QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;}"
                "QLineEdit:hover{background:rgba(255,255,255,0.18);border-radius:6px;}"
            )
        else:
            # IMPORTANT: focus padding fixed to keep perceived height identical
            self.setStyleSheet(
                "QLineEdit{background:rgba(255,255,255,0.70);border:1px solid rgba(0,0,0,0.22);"
                "border-radius:8px;padding:0 2px;color:#111;}"
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isReadOnly():
            self.setReadOnly(False)
            self._apply_style(editing=True)
            self.setFocus()
            self.selectAll()
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._commit_lock()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._commit_lock()
            event.accept()
            return
        if event.key() == Qt.Key_Escape:
            self.setReadOnly(True)
            self._apply_style(editing=False)
            event.accept()
            return
        super().keyPressEvent(event)

    def _commit_lock(self):
        if not self.isReadOnly():
            self.setReadOnly(True)
            self._apply_style(editing=False)
            self.committed.emit(self.text())

    def set_text_silent(self, text: str):
        old = self.blockSignals(True)
        try:
            self.setText(text or "")
        finally:
            self.blockSignals(old)


# ---------- Base card ----------
class _PostItCardBase(QWidget):
    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self._active = False
        self._bg = _bg(kind)
        self._bd = _bd(kind)

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


# ---------- Basic info ----------
class BasicInfoPostIt(_PostItCardBase):
    edit_requested = Signal()  # compatibility
    data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(kind="basic", parent=parent)
        self.setMinimumSize(QSize(320, 175))

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("기본정보", self)
        title.setStyleSheet("QLabel{font-weight:700;color:#222;background:transparent;}")
        root.addWidget(title)

        # date row
        date_row = QHBoxLayout()
        date_row.setContentsMargins(0, 0, 0, 0)
        date_row.setSpacing(6)

        lbl_date = QLabel("날짜:", self)
        lbl_date.setFixedWidth(44)
        lbl_date.setFixedHeight(FIELD_H)
        lbl_date.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_date.setStyleSheet("QLabel{font-weight:600;color:#222;background:transparent;}")
        date_row.addWidget(lbl_date)

        self._date_value = QDate.currentDate()
        self.date_text = QLabel(self)
        self.date_text.setFixedHeight(FIELD_H)
        self.date_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_text.setStyleSheet(
            "QLabel{background:rgba(255,255,255,0.65);border:1px solid rgba(0,0,0,0.18);"
            "border-radius:8px;padding:0 8px;color:#111;}"
        )
        self.date_text.setMinimumWidth(118)
        self.date_text.setText(self._date_value.toString("yyyy-MM-dd"))

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

        # text fields
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        def mk_label(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet("QLabel{font-weight:600;color:#222;background:transparent;}")
            return l

        self.style_no = _ClickToEditLineEdit(self)
        self.factory = _ClickToEditLineEdit(self)

        # product width auto
        self.style_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._style_no_min = 140
        self._style_no_max = 320
        self.style_no.textChanged.connect(self._adjust_style_width)
        self._adjust_style_width(self.style_no.text())

        grid.addWidget(mk_label("제품명:"), 0, 0)
        grid.addWidget(self.style_no, 0, 1)
        grid.addWidget(mk_label("공장:"), 1, 0)
        grid.addWidget(self.factory, 1, 1)

        root.addLayout(grid)

        # money grid
        mg = QGridLayout()
        mg.setContentsMargins(0, 0, 0, 0)
        mg.setHorizontalSpacing(8)
        mg.setVerticalSpacing(6)

        def mk_money_label(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet("QLabel{font-weight:600;color:#222;background:transparent;}")
            return l

        self.cost = _MoneyLineEdit(self)
        self.labor = _MoneyLineEdit(self)
        self.loss = _MoneyLineEdit(self)
        self.sale_price = _MoneyLineEdit(self)

        # money fields should also look like post-it fields
        for w in (self.cost, self.labor, self.loss, self.sale_price):
            w.setStyleSheet(
                "QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;}"
                "QLineEdit:hover{background:rgba(255,255,255,0.18);border-radius:6px;}"
                "QLineEdit:focus{background:rgba(255,255,255,0.70);border:1px solid rgba(0,0,0,0.22);"
                "border-radius:8px;padding:0 2px;}"
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

        # sync total -> sale
        self.cost.textChanged.connect(self._sync_sale_price)
        self.labor.textChanged.connect(self._sync_sale_price)
        self.loss.textChanged.connect(self._sync_sale_price)

        # commit signals
        self.style_no.committed.connect(lambda v: self._emit_patch({"style_no": v.strip()}))
        self.factory.committed.connect(lambda v: self._emit_patch({"factory": v.strip()}))

        for w in (self.cost, self.labor, self.loss, self.sale_price):
            w.textChanged.connect(lambda _t: self._emit_money_patch())

    def _adjust_style_width(self, text: str):
        fm = QFontMetrics(self.style_no.font())
        w = fm.horizontalAdvance(text or "") + 28
        w = max(self._style_no_min, min(self._style_no_max, w))
        self.style_no.setMinimumWidth(w)

    def set_header_data(self, header: Dict[str, str]):
        header = header or {}

        d = QDate.fromString(header.get("date", ""), "yyyy-MM-dd")
        if not d.isValid():
            d = QDate.currentDate()
        self._date_value = d
        self.date_text.setText(d.toString("yyyy-MM-dd"))

        self.style_no.set_text_silent(header.get("style_no", ""))
        self.factory.set_text_silent(header.get("factory", ""))
        self._adjust_style_width(self.style_no.text())

        self.cost.setText(header.get("cost_display", header.get("cost", "")) or "")
        self.labor.setText(header.get("labor_display", header.get("labor", "")) or "")
        self.loss.setText(header.get("loss_display", header.get("loss", "")) or "")
        self.sale_price.setText(header.get("sale_price_display", header.get("sale_price", "")) or "")

    def _emit_patch(self, patch: dict):
        patch = dict(patch or {})
        patch["date"] = self._date_value.toString("yyyy-MM-dd")
        patch["style_no"] = self.style_no.text()
        patch["factory"] = self.factory.text()
        self.data_changed.emit(patch)

    def _emit_money_patch(self):
        patch = {
            "date": self._date_value.toString("yyyy-MM-dd"),
            "style_no": self.style_no.text(),
            "factory": self.factory.text(),
            "cost_display": self.cost.text(),
            "labor_display": self.labor.text(),
            "loss_display": self.loss.text(),
            "sale_price_display": self.sale_price.text(),
            "cost": self.cost.digits(),
            "labor": self.labor.digits(),
            "loss": self.loss.digits(),
            "sale_price": self.sale_price.digits(),
        }
        self.data_changed.emit(patch)

    def _sync_sale_price(self):
        total = _int_from_any(self.cost.text()) + _int_from_any(self.labor.text()) + _int_from_any(self.loss.text())
        self.sale_price.setText(_format_commas(str(total)))

    def _open_calendar(self):
        popup = _InlineCalendarPopup(self._date_value, parent=self)
        popup.datePicked.connect(self._on_date_picked)

        anchor = self.btn_calendar.mapToGlobal(QPoint(0, self.btn_calendar.height() + 4))
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


# ---------- Change note ----------
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
        title.setStyleSheet("QLabel{font-weight:700;color:#1B5E20;background:transparent;}")
        root.addWidget(title)

        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("")
        self.editor.setStyleSheet(
            "QPlainTextEdit{background:transparent;border:none;color:#222;font-size:12px;}"
            "QPlainTextEdit:focus{background:rgba(255,255,255,0.55);border:1px solid rgba(0,0,0,0.18);"
            "border-radius:12px;padding:8px;}"
        )
        root.addWidget(self.editor, 1)
        self.editor.textChanged.connect(self._on_text)

    def _on_text(self):
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
    data_changed = Signal(int, dict)
    new_item_changed = Signal(dict)   # for "new item" card

    def __init__(self, kind: str, index: int, data: Dict[str, str], is_new_card: bool, parent=None):
        super().__init__(kind=kind, parent=parent)
        self.index = index
        self.data = dict(data or {})
        self.is_new_card = is_new_card

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)

        # delete button (top-right) - hide for new card
        self.btn_delete = QToolButton(self)
        self.btn_delete.setText("×")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setFixedSize(20, 20)
        self.btn_delete.setStyleSheet(
            "QToolButton{border:none;border-radius:10px;background:rgba(0,0,0,0.12);font-weight:bold;}"
            "QToolButton:hover{background:rgba(0,0,0,0.22);}"
        )
        self.btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.index))
        self.btn_delete.setVisible(not self.is_new_card)

        # vendor/item rows (match basic style with labels)
        vi = QGridLayout()
        vi.setContentsMargins(0, 0, 0, 0)
        vi.setHorizontalSpacing(8)
        vi.setVerticalSpacing(6)

        def mk_lbl(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet("QLabel{font-weight:600;color:#222;background:transparent;}")
            return l

        self.vendor = _ClickToEditLineEdit(self)
        self.item = _ClickToEditLineEdit(self)

        vi.addWidget(mk_lbl("거래처:"), 0, 0)
        vi.addWidget(self.vendor, 0, 1)
        vi.addWidget(mk_lbl("품목:"), 1, 0)
        vi.addWidget(self.item, 1, 1)

        root.addLayout(vi)

        # qty/unit/price/total grid
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        def mk_lbl2(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet("QLabel{font-weight:600;color:#222;background:transparent;}")
            return l

        self.qty = _ClickToEditLineEdit(self)
        self.qty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.unit = _ClickToEditLineEdit(self)

        self.price = _MoneyLineEdit(self)
        self.total = _MoneyLineEdit(self)

        # match money style to basic
        for w in (self.price, self.total):
            w.setStyleSheet(
                "QLineEdit{background:transparent;border:none;color:#111;padding:0 2px;}"
                "QLineEdit:hover{background:rgba(255,255,255,0.18);border-radius:6px;}"
                "QLineEdit:focus{background:rgba(255,255,255,0.70);border:1px solid rgba(0,0,0,0.22);"
                "border-radius:8px;padding:0 2px;}"
            )

        grid.addWidget(mk_lbl2("수량"), 0, 0)
        grid.addWidget(self.qty, 0, 1)
        grid.addWidget(mk_lbl2("단위"), 0, 2)
        grid.addWidget(self.unit, 0, 3)

        grid.addWidget(mk_lbl2("단가"), 1, 0)
        grid.addWidget(self.price, 1, 1, 1, 3)

        grid.addWidget(mk_lbl2("총액"), 2, 0)
        grid.addWidget(self.total, 2, 1, 1, 3)

        root.addLayout(grid)

        # fill initial data
        self.vendor.set_text_silent(self.data.get("거래처", ""))
        self.item.set_text_silent(self.data.get("품목", ""))
        self.qty.set_text_silent(self.data.get("수량", ""))
        self.unit.set_text_silent(self.data.get("단위", ""))
        self.price.setText(self.data.get("단가", ""))
        self.total.setText(self.data.get("총액", ""))

        # connections
        self.vendor.committed.connect(lambda v: self._commit("거래처", v))
        self.item.committed.connect(lambda v: self._commit("품목", v))
        self.qty.committed.connect(lambda v: self._commit("수량", v))
        self.unit.committed.connect(lambda v: self._commit("단위", v))
        self.price.textChanged.connect(lambda _t: self._commit("단가", self.price.text()))
        self.total.textChanged.connect(lambda _t: self._commit("총액", self.total.text()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.index)
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        self.btn_delete.move(self.width() - 28, 10)
        super().resizeEvent(event)

    def _commit(self, key: str, value: str):
        value = (value or "").strip()
        self.data[key] = value
        if self.is_new_card:
            self.new_item_changed.emit(dict(self.data))
            return
        self.data_changed.emit(self.index, {key: value})



class PostItStack(QWidget):
    item_deleted = Signal(int)
    item_changed = Signal(int, dict)
    item_created = Signal(dict)

    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.items: List[Dict[str, str]] = []
        self.cards: List[PostItCard] = []
        self.active_index = -1
        self._emitting_create = False
        self.setMinimumHeight(175)

    def set_items(self, items: List[Dict[str, str]]):
        self.items = list(items or [])
        self._rebuild()

    def _rebuild(self):
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        self.cards = []

        # existing items
        for idx, it in enumerate(self.items):
            card = PostItCard(self.kind, idx, it, is_new_card=False, parent=self)
            card.delete_clicked.connect(self.item_deleted.emit)
            card.selected.connect(self.set_active_card)
            card.data_changed.connect(self.item_changed.emit)
            card.show()
            self.cards.append(card)

        # new item card (always visible, no 안내문)
        new_card = PostItCard(self.kind, len(self.items), {}, is_new_card=True, parent=self)
        new_card.selected.connect(self.set_active_card)
        new_card.new_item_changed.connect(self._on_new_item_changed)
        new_card.show()
        self.cards.append(new_card)

        self.active_index = max(0, len(self.cards) - 1)
        self._layout_cards()
        self._apply_active()

    def _on_new_item_changed(self, data: Dict[str, str]):
        if self._emitting_create:
            return
        payload = {
            "거래처": (data.get("거래처") or "").strip(),
            "품목": (data.get("품목") or "").strip(),
            "수량": (data.get("수량") or "").strip(),
            "단위": (data.get("단위") or "").strip(),
            "단가": (data.get("단가") or "").strip(),
            "총액": (data.get("총액") or "").strip(),
        }
        if not any(payload.values()):
            return
        self._emitting_create = True
        try:
            self.item_created.emit(payload)
        finally:
            self._emitting_create = False

    def set_active_card(self, idx: int):
        if idx < 0 or idx >= len(self.cards):
            return
        self.active_index = idx
        self._apply_active()
        self.cards[idx].raise_()

    def _apply_active(self):
        for i, c in enumerate(self.cards):
            c.set_active(i == self.active_index)

    def resizeEvent(self, event):
        self._layout_cards()
        super().resizeEvent(event)

    def _layout_cards(self):
        base_w = self.width()
        card_w = max(280, min(340, base_w - 20))
        card_h = 170
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

        self.fabric = PostItStack(kind="fabric", parent=self)
        self.trim = PostItStack(kind="trim", parent=self)

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
