# ui/postit_widgets.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from PySide6.QtCore import Qt, QPoint, QRectF, QSize, Signal, QDate, QEvent
from PySide6.QtGui import QColor, QFontMetrics, QIcon, QPainter, QPen, QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QToolButton,
    QCalendarWidget,
    QDialog,
    QMenu,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QStackedLayout,
)


# ---------- constants ----------
FIELD_H = 28
CARD_RADIUS = 20
MAX_POSTIT_CARDS = 9


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


def _bg(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#F8EDAE")
    if kind == "fabric":
        return QColor("#D7EEF5")
    if kind == "trim":
        return QColor("#E8DDF8")
    if kind == "change":
        return QColor("#DDEEDC")
    return QColor("#FFF4A3")


def _bd(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#C9B96C")
    if kind == "fabric":
        return QColor("#98C7D1")
    if kind == "trim":
        return QColor("#B7A3E8")
    if kind == "change":
        return QColor("#9BBF99")
    return QColor("#C9B96C")


def _title_color(kind: str) -> str:
    if kind == "basic":
        return "#5D4B1E"
    if kind == "fabric":
        return "#295A67"
    if kind == "trim":
        return "#5F4A8A"
    if kind == "change":
        return "#47664A"
    return "#2E2A24"


def _field_style(editable: bool = True, align_right: bool = False) -> str:
    align = "right" if align_right else "left"
    if editable:
        return (
            "QLineEdit{background:rgba(255,255,255,0.48);border:1px solid rgba(92,77,61,0.10);"
            "border-radius:10px;color:#2F2923;padding:0 8px;text-align:%s;}"
            "QLineEdit:hover{background:rgba(255,255,255,0.65);border-color:rgba(92,77,61,0.18);}"
            "QLineEdit:focus{background:rgba(255,255,255,0.88);border:1px solid rgba(92,77,61,0.28);"
            "border-radius:10px;padding:0 8px;color:#201B16;}"
        ) % align
    return (
        "QLineEdit{background:rgba(255,255,255,0.38);border:1px solid transparent;color:#2F2923;"
        "padding:0 8px;text-align:%s;border-radius:10px;}"
        "QLineEdit:hover{background:rgba(255,255,255,0.56);border-color:rgba(92,77,61,0.10);}"
    ) % align


def _pill_button_style(active: bool = False, disabled: bool = False) -> str:
    if disabled:
        return (
            "QToolButton{border:1px solid rgba(92,77,61,0.10);border-radius:9px;"
            "background:rgba(255,255,255,0.30);color:rgba(47,41,35,0.36);font-weight:700;}"
        )
    if active:
        return (
            "QToolButton{border:1px solid rgba(92,77,61,0.22);border-radius:9px;"
            "background:rgba(255,255,255,0.92);color:#2F2923;font-weight:800;}"
            "QToolButton:hover{background:#FFFFFF;}"
        )
    return (
        "QToolButton{border:1px solid rgba(92,77,61,0.14);border-radius:9px;"
        "background:rgba(255,255,255,0.58);color:#4B4138;font-weight:700;}"
        "QToolButton:hover{background:rgba(255,255,255,0.82);}"
    )


def _make_calendar_icon(size: int = 16) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setPen(QPen(QColor("#222"), 2))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(1, 2, size - 2, size - 3, 3, 3)
    p.drawLine(2, 6, size - 3, 6)
    p.setPen(QPen(QColor("#222"), 2))
    p.drawLine(5, 1, 5, 5)
    p.drawLine(size - 6, 1, size - 6, 5)
    p.end()
    return QIcon(pm)


def _make_down_icon(size: int = 12) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    pen = QPen(QColor("#222"), 2)
    p.setPen(pen)
    # v shape
    p.drawLine(2, 4, size // 2, size - 4)
    p.drawLine(size // 2, size - 4, size - 2, 4)
    p.end()
    return QIcon(pm)


def _load_units() -> List[Tuple[str, str]]:
    """Load units from db/units.json.

    Expected format:
      {"units": [{"unit": "EA", "label": "EA (개)"}, ...]}
    """
    try:
        base = Path(__file__).resolve().parent.parent  # repo root
        path = base / "db" / "units.json"
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))

        if isinstance(data, dict):
            units = data.get("units", [])
        elif isinstance(data, list):
            # legacy format
            units = data
        else:
            units = []

        out: List[Tuple[str, str]] = []
        if isinstance(units, list):
            for it in units:
                if not isinstance(it, dict):
                    continue
                unit = str(it.get("unit", "") or "").strip()
                label = str(it.get("label", "") or "").strip()
                if unit or label:
                    out.append((unit, label or unit))
        return out
    except Exception:
        return []


# ---------- popup calendar ----------
class _InlineCalendarPopup(QDialog):
    datePicked = Signal(QDate)

    def __init__(self, initial: QDate, parent=None):
        super().__init__(parent, Qt.Popup)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        self.cal = QCalendarWidget(self)
        self.cal.setGridVisible(True)
        self.cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        if initial and initial.isValid():
            self.cal.setSelectedDate(initial)
        self.cal.activated.connect(self._on_activated)
        lay.addWidget(self.cal)

    def _on_activated(self, d: QDate):
        if d and d.isValid():
            self.datePicked.emit(d)
        self.close()


# ---------- inline editors ----------
class _MoneyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(r"[0-9,]*", self))
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
        # Keep border/padding consistent to avoid layout jitter when toggling edit mode.
        if not editing:
            self.setStyleSheet(_field_style(editable=False, align_right=False))
        else:
            self.setStyleSheet(_field_style(editable=True, align_right=False))
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


class _QtyClickToEditLineEdit(_ClickToEditLineEdit):
    """Click-to-edit integer-only field (no commas)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(r"[0-9]*", self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def _commit_lock(self):
        if not self.isReadOnly():
            # keep digits only
            digits = _digits_only(self.text())
            self.set_text_silent(digits)
            self.setReadOnly(True)
            self._apply_style(editing=False)
            self.committed.emit(digits)



# ---------- base card ----------
class _PostItCardBase(QWidget):
    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self._active = False
        self._bg = _bg(kind)
        self._bd = _bd(kind)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(96, 76, 56, 34))
        self.setGraphicsEffect(shadow)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = QRectF(2.0, 2.0, self.width() - 4.0, self.height() - 4.0)
        pen = QPen(self._bd, 1.6)
        if self._active:
            pen = QPen(QColor(self._bd).darker(122), 2.2)
        p.setPen(pen)
        p.setBrush(self._bg)
        p.drawRoundedRect(r, CARD_RADIUS, CARD_RADIUS)

        header_h = min(30.0, max(24.0, self.height() * 0.16))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 42))
        p.drawRoundedRect(QRectF(r.x() + 1.5, r.y() + 1.5, r.width() - 3.0, header_h), CARD_RADIUS - 3, CARD_RADIUS - 3)


# ---------- basic info ----------
class BasicInfoPostIt(_PostItCardBase):
    data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("basic", parent=parent)
        self.setMinimumSize(QSize(336, 192))

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("기본정보", self)
        title.setStyleSheet(f"QLabel{{font-size:14px;font-weight:800;color:{_title_color('basic')};background:transparent;letter-spacing:0.2px;}}")
        root.addWidget(title)

        # date row
        date_row = QHBoxLayout()
        date_row.setSpacing(6)

        lbl_date = QLabel("날짜:", self)
        lbl_date.setFixedWidth(44)
        lbl_date.setFixedHeight(FIELD_H)
        lbl_date.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_date.setStyleSheet("QLabel{font-weight:600;color:#222;background:transparent;}")
        date_row.addWidget(lbl_date)

        self._date_value = QDate.currentDate()
        self.date_text = QLabel(self._date_value.toString("yyyy-MM-dd"), self)
        self.date_text.setFixedHeight(FIELD_H)
        self.date_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_text.setStyleSheet(
            "QLabel{background:rgba(255,255,255,0.72);border:1px solid rgba(92,77,61,0.16);"
            "border-radius:10px;padding:0 10px;color:#2F2923;}"
        )
        self.date_text.setMinimumWidth(118)

        self.btn_calendar = QToolButton(self)
        self.btn_calendar.setIcon(_make_calendar_icon(16))
        self.btn_calendar.setIconSize(QSize(16, 16))
        self.btn_calendar.setFixedSize(FIELD_H, FIELD_H)
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.setStyleSheet(
            "QToolButton{border:1px solid rgba(92,77,61,0.14);border-radius:9px;background:rgba(255,255,255,0.68);}"
            "QToolButton:hover{background:rgba(255,255,255,0.88);border-color:rgba(92,77,61,0.20);}"
        )
        self.btn_calendar.clicked.connect(self._open_calendar)

        date_row.addWidget(self.date_text, 1)
        date_row.addWidget(self.btn_calendar)
        root.addLayout(date_row)

        # labels + fields grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        def mk_label(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet("QLabel{font-weight:700;color:#4B4138;background:transparent;}")
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

        mg = QGridLayout()
        mg.setHorizontalSpacing(8)
        mg.setVerticalSpacing(6)

        self.cost = _MoneyLineEdit(self)
        self.labor = _MoneyLineEdit(self)
        self.loss = _MoneyLineEdit(self)
        self.sale_price = _MoneyLineEdit(self)

        for w in (self.cost, self.labor, self.loss, self.sale_price):
            w.setStyleSheet(_field_style(editable=True, align_right=True))

        mg.addWidget(mk_label("원가:"), 0, 0)
        mg.addWidget(self.cost, 0, 1)
        mg.addWidget(mk_label("공임:"), 0, 2)
        mg.addWidget(self.labor, 0, 3)
        mg.addWidget(mk_label("로스:"), 1, 0)
        mg.addWidget(self.loss, 1, 1)
        mg.addWidget(mk_label("판매가:"), 1, 2)
        mg.addWidget(self.sale_price, 1, 3)

        root.addLayout(mg)

        self.cost.textChanged.connect(self._sync_sale_price)
        self.labor.textChanged.connect(self._sync_sale_price)
        self.loss.textChanged.connect(self._sync_sale_price)

        self.style_no.committed.connect(lambda _v: self._emit_all())
        self.factory.committed.connect(lambda _v: self._emit_all())
        for w in (self.cost, self.labor, self.loss, self.sale_price):
            w.textChanged.connect(lambda _t: self._emit_all())

    def _adjust_style_width(self, text: str):
        fm = QFontMetrics(self.style_no.font())
        w = fm.horizontalAdvance(text or "") + 28
        w = max(self._style_no_min, min(self._style_no_max, w))
        self.style_no.setMinimumWidth(w)

    def _sync_sale_price(self):
        total = _int_from_any(self.cost.text()) + _int_from_any(self.labor.text()) + _int_from_any(self.loss.text())
        self.sale_price.setText(_format_commas(str(total)) if total else "")

    def _open_calendar(self):
        popup = _InlineCalendarPopup(self._date_value, parent=self)
        popup.datePicked.connect(self._on_date_picked)

        anchor = self.btn_calendar.mapToGlobal(QPoint(0, self.btn_calendar.height() + 4))
        popup.move(anchor)
        popup.show()

    def _on_date_picked(self, d: QDate):
        self._date_value = d
        self.date_text.setText(d.toString("yyyy-MM-dd"))
        self._emit_all()

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

    def _emit_all(self):
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


# ---------- change note ----------
class ChangeNotePostIt(_PostItCardBase):
    text_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__("change", parent=parent)
        self.setMinimumSize(QSize(312, 240))
        self._block = False

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("수정사항", self)
        title.setStyleSheet(f"QLabel{{font-size:14px;font-weight:800;color:{_title_color('change')};background:transparent;letter-spacing:0.2px;}}")
        root.addWidget(title)

        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("")
        self.editor.setStyleSheet(
            "QPlainTextEdit{background:rgba(255,255,255,0.34);border:1px solid rgba(92,77,61,0.10);"
            "border-radius:14px;color:#2F2923;font-size:12px;padding:10px;selection-background-color:rgba(125,164,126,0.28);}"
            "QPlainTextEdit:hover{background:rgba(255,255,255,0.46);border-color:rgba(92,77,61,0.16);}"
            "QPlainTextEdit:focus{background:rgba(255,255,255,0.82);border:1px solid rgba(92,77,61,0.24);"
            "border-radius:14px;padding:10px;color:#201B16;}"
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


# ---------- fabric/trim card ----------
class PostItCard(_PostItCardBase):
    delete_clicked = Signal(int)
    selected = Signal(int)
    data_changed = Signal(int, dict)

    def __init__(self, kind: str, index: int, data: Dict[str, str], parent=None):
        super().__init__(kind, parent=parent)
        self.index = index
        self.data = dict(data or {})
        self._block_total = False
        self._units = _load_units()
        self._unit_value = (self.data.get("단위") or "").strip()
        self._unit_label = self._label_for_unit(self._unit_value)
        self._suppress_unit_menu_once = False

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        self.btn_delete = QToolButton(self)
        self.btn_delete.setText("×")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setFixedSize(20, 20)
        self.btn_delete.setStyleSheet(
            "QToolButton{border:1px solid rgba(92,77,61,0.12);border-radius:10px;background:rgba(255,255,255,0.56);"
            "color:#5B4E43;font-weight:800;}"
            "QToolButton:hover{background:rgba(255,255,255,0.86);border-color:rgba(92,77,61,0.20);}"
        )
        self.btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.index))

        vi = QGridLayout()
        vi.setHorizontalSpacing(8)
        vi.setVerticalSpacing(6)

        def mk_label(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet("QLabel{font-weight:700;color:#4B4138;background:transparent;}")
            return l

        self.vendor = _ClickToEditLineEdit(self)
        self.item = _ClickToEditLineEdit(self)
        self.vendor.set_text_silent(self.data.get("거래처", ""))
        self.item.set_text_silent(self.data.get("품목", ""))

        vi.addWidget(mk_label("거래처:"), 0, 0)
        vi.addWidget(self.vendor, 0, 1)
        vi.addWidget(mk_label("품목:"), 1, 0)
        vi.addWidget(self.item, 1, 1)
        root.addLayout(vi)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        def mk_label2(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet("QLabel{font-weight:700;color:#4B4138;background:transparent;}")
            return l

        self.qty = _QtyClickToEditLineEdit(self)
        self.qty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.qty.set_text_silent(self.data.get("수량", ""))

        self.unit_btn = QToolButton(self)
        self.unit_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.unit_btn.setIcon(_make_down_icon(12))
        self.unit_btn.setIconSize(QSize(12, 12))
        self.unit_btn.setCursor(Qt.PointingHandCursor)
        self.unit_btn.setFixedHeight(FIELD_H)
        self.unit_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.unit_btn.setStyleSheet(
            "QToolButton{background:rgba(255,255,255,0.40);border:1px solid rgba(92,77,61,0.10);color:#2F2923;"
            "padding:0 10px;text-align:left;border-radius:10px;}"
            "QToolButton:hover{background:rgba(255,255,255,0.66);border-color:rgba(92,77,61,0.18);}"
            "QToolButton:pressed{background:rgba(255,255,255,0.84);}"
            "QToolButton:focus{background:rgba(255,255,255,0.86);border-color:rgba(92,77,61,0.24);}"
        )
        self._apply_unit_button_text()
        self._unit_menu = QMenu(self.unit_btn)
        self._unit_menu.setStyleSheet(
            "QMenu{background:#FFFDF8;border:1px solid rgba(92,77,61,0.14);padding:8px;border-radius:12px;color:#2F2923;}"
            "QMenu::item{padding:6px 14px;border-radius:8px;margin:2px 4px;}"
            "QMenu::item:selected{background:rgba(205,191,136,0.22);}"
            "QMenu::separator{height:1px;background:rgba(92,77,61,0.08);margin:6px 8px;}"
        )
        self._unit_actions: Dict[str, object] = {}

        self._act_clear_unit = self._unit_menu.addAction("(비움)")
        self._act_clear_unit.setCheckable(True)
        self._act_clear_unit.triggered.connect(lambda: self._set_unit("", ""))
        if self._units:
            self._unit_menu.addSeparator()
        else:
            hint = self._unit_menu.addAction("(단위 목록 없음)")
            hint.setEnabled(False)

        for unit, label in self._units:
            act = self._unit_menu.addAction(label)
            act.setCheckable(True)
            act.triggered.connect(lambda _=False, u=unit, lb=label: self._set_unit(u, lb))
            self._unit_actions[unit] = act

        self._unit_menu.aboutToShow.connect(self._sync_unit_menu_checks)
        self.unit_btn.setMenu(self._unit_menu)
        self.unit_btn.setPopupMode(QToolButton.InstantPopup)
        self.unit_btn.installEventFilter(self)

        self.price = _MoneyLineEdit(self)
        self.total = _MoneyLineEdit(self)
        for w in (self.price, self.total):
            w.setStyleSheet(_field_style(editable=True, align_right=True))

        self.price.setText(self.data.get("단가", ""))
        self.total.setText(self.data.get("총액", ""))

        grid.addWidget(mk_label2("수량"), 0, 0)
        grid.addWidget(self.qty, 0, 1)
        grid.addWidget(mk_label2("단위"), 0, 2)
        grid.addWidget(self.unit_btn, 0, 3)
        grid.addWidget(mk_label2("단가"), 1, 0)
        grid.addWidget(self.price, 1, 1, 1, 3)
        grid.addWidget(mk_label2("총액"), 2, 0)
        grid.addWidget(self.total, 2, 1, 1, 3)
        root.addLayout(grid)

        # connections
        self.vendor.committed.connect(lambda v: self._commit("거래처", v))
        self.item.committed.connect(lambda v: self._commit("품목", v))
        self.qty.committed.connect(lambda v: self._on_qty_committed(v))
        self.qty.textChanged.connect(lambda _t: self._recalc_total())
        self.price.textChanged.connect(lambda _t: self._on_price_changed())
        self.total.textChanged.connect(lambda _t: (None if self._block_total else self._commit("총액", self.total.text())))

        self.setMinimumSize(QSize(336, 188))
        self.setMaximumHeight(188)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _label_for_unit(self, unit: str) -> str:
        for u, lb in self._units:
            if u == unit:
                return lb
        return unit or ""

    def _apply_unit_button_text(self):
        self.unit_btn.setText(self._unit_label or "")

    def _sync_unit_menu_checks(self):
        current = (self._unit_value or "").strip()
        try:
            self._act_clear_unit.setChecked(not bool(current))
        except Exception:
            pass
        for unit, act in self._unit_actions.items():
            try:
                act.setChecked(bool(current) and unit == current)
            except Exception:
                pass

    def _set_unit(self, unit: str, label: str):
        self._unit_value = unit or ""
        self._unit_label = label or ""
        self._apply_unit_button_text()
        self._commit("단위", self._unit_value)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.unit_btn.hasFocus():
            self._set_unit("", "")
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.index)
        super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        if obj is self.unit_btn and self._suppress_unit_menu_once:
            if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick):
                self._suppress_unit_menu_once = False
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def suppress_unit_menu_once(self):
        self._suppress_unit_menu_once = True

    def resizeEvent(self, event):
        self.btn_delete.move(self.width() - 28, 10)
        super().resizeEvent(event)


    def update_data(self, data: Dict[str, str]):
        """Refresh card UI from external data without emitting change signals."""
        self.data = dict(data or {})
        self._unit_value = (self.data.get("단위") or "").strip()
        self._unit_label = self._label_for_unit(self._unit_value)

        widgets = (
            self.vendor,
            self.item,
            self.qty,
            self.price,
            self.total,
        )
        blocked = [(w, w.blockSignals(True)) for w in widgets]
        try:
            self.vendor.set_text_silent(self.data.get("거래처", ""))
            self.item.set_text_silent(self.data.get("품목", ""))
            self.qty.set_text_silent(_digits_only(self.data.get("수량", "")))
            self.price.setText(self.data.get("단가", ""))
            self.total.setText(self.data.get("총액", ""))
            self._apply_unit_button_text()
        finally:
            for w, old in blocked:
                w.blockSignals(old)

        # Keep total field consistent when one side is blank.
        self._recalc_total()

    def _commit(self, key: str, value: str):
        value = (value or "").strip()
        self.data[key] = value
        self.data_changed.emit(self.index, {key: value})

    def _on_qty_committed(self, v: str):
        self._commit("수량", v)
        self._recalc_total()

    def _on_price_changed(self):
        self._commit("단가", self.price.text())
        self._recalc_total()

    def _recalc_total(self):
        if self._block_total:
            return

        qty_digits = _digits_only(self.qty.text())
        price_digits = _digits_only(self.price.text())

        # 빈칸이면 총액도 빈칸이어야 함
        if not qty_digits or not price_digits:
            self._block_total = True
            try:
                self.total.setText("")
            finally:
                self._block_total = False
            self._commit("총액", "")
            return

        try:
            total = int(qty_digits) * int(price_digits)
        except Exception:
            total = 0

        self._block_total = True
        try:
            self.total.setText(_format_commas(str(total)))
        finally:
            self._block_total = False
        self._commit("총액", self.total.text())


# ---------- stack (index + plus) ----------
class PostItStack(QWidget):
    item_deleted = Signal(int)
    item_changed = Signal(int, dict)
    item_added = Signal()

    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.items: List[Dict[str, str]] = []
        self.cards: List[PostItCard] = []
        self.index_buttons: List[QToolButton] = []
        self.plus_button: QToolButton | None = None
        self.active_index = 0
        self._suppress_next_new_card_menu = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        self.index_row = QHBoxLayout()
        self.index_row.setSpacing(8)
        root.addLayout(self.index_row)

        self.stack = QStackedLayout()
        root.addLayout(self.stack)

        self._rebuild_index_buttons()

    def set_items(self, items: List[Dict[str, str]]):
        items = list(items or [])
        if not items:
            items = [{"거래처": "", "품목": "", "수량": "", "단위": "", "단가": "", "총액": ""}]

        if not self.cards:
            self.items = items
            if self.active_index >= len(self.items):
                self.active_index = max(0, len(self.items) - 1)
            self._rebuild()
            return

        if len(items) == len(self.items) == len(self.cards):
            self.items = items
            for idx, (card, it) in enumerate(zip(self.cards, self.items)):
                card.index = idx
                card.update_data(it)
            if self.active_index >= len(self.items):
                self.active_index = max(0, len(self.items) - 1)
            self.stack.setCurrentIndex(self.active_index)
            self._apply_active()
            self._rebuild_index_buttons()
            return

        if len(items) == len(self.items) + 1 and items[:-1] == self.items:
            self.items = items
            self._append_card(items[-1], len(items) - 1)
            self._refresh_delete_buttons()
            self._rebuild_index_buttons()
            return

        removed_idx = self._find_single_removed_index(self.items, items)
        if removed_idx is not None:
            self.items = items
            self._remove_card_at(removed_idx)
            for idx in range(removed_idx, len(self.cards)):
                self.cards[idx].index = idx
                self.cards[idx].update_data(self.items[idx])
            if self.active_index >= len(self.items):
                self.active_index = max(0, len(self.items) - 1)
            self.stack.setCurrentIndex(self.active_index)
            self._refresh_delete_buttons()
            self._apply_active()
            self._rebuild_index_buttons()
            return

        self.items = items
        if self.active_index >= len(self.items):
            self.active_index = max(0, len(self.items) - 1)
        self._rebuild()

    def _find_single_removed_index(self, old_items, new_items):
        if len(old_items) != len(new_items) + 1:
            return None
        for idx in range(len(old_items)):
            if old_items[:idx] + old_items[idx + 1:] == new_items:
                return idx
        return None

    def _create_card(self, idx: int, it: Dict[str, str]) -> PostItCard:
        card = PostItCard(self.kind, idx, it, parent=self)
        card.delete_clicked.connect(self.item_deleted.emit)
        card.selected.connect(self.set_active_card)
        card.data_changed.connect(self.item_changed.emit)
        return card

    def _append_card(self, it: Dict[str, str], idx: int):
        card = self._create_card(idx, it)
        if self._suppress_next_new_card_menu:
            card.suppress_unit_menu_once()
            self._suppress_next_new_card_menu = False
        self.stack.addWidget(card)
        self.cards.append(card)
        self._apply_active()

    def _remove_card_at(self, idx: int):
        if idx < 0 or idx >= len(self.cards):
            return
        card = self.cards.pop(idx)
        self.stack.removeWidget(card)
        card.setParent(None)
        card.deleteLater()

    def _refresh_delete_buttons(self):
        single = len(self.cards) == 1
        for c in self.cards:
            c.btn_delete.setVisible(not single)

    def _rebuild(self):
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.setParent(None)
            w.deleteLater()
        self.cards = []

        for idx, it in enumerate(self.items):
            self._append_card(it, idx)

        self.stack.setCurrentIndex(self.active_index)
        self._refresh_delete_buttons()
        self._rebuild_index_buttons()
        self._apply_active()

    def _button_style(self, active: bool) -> str:
        return _pill_button_style(active=active)

    def _make_index_button(self, txt: str) -> QToolButton:
        b = QToolButton(self)
        b.setText(txt)
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedSize(28, 28)
        b.setFocusPolicy(Qt.NoFocus)
        return b

    def _rebuild_index_buttons(self):
        while self.index_row.count():
            it = self.index_row.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        self.index_buttons = []
        for i in range(len(self.items)):
            b = self._make_index_button(str(i + 1))
            b.clicked.connect(lambda _=False, idx=i: self.set_active_card(idx))
            self.index_buttons.append(b)
            self.index_row.addWidget(b)

        self.plus_button = self._make_index_button('+')
        self.plus_button.clicked.connect(self._on_add_clicked)
        self.index_row.addWidget(self.plus_button)
        self.index_row.addStretch(1)
        self._update_index_button_states()

    def _update_index_button_states(self):
        for i, b in enumerate(self.index_buttons):
            b.setStyleSheet(self._button_style(i == self.active_index))
        if self.plus_button is not None:
            enabled = len(self.items) < MAX_POSTIT_CARDS
            self.plus_button.setEnabled(enabled)
            if enabled:
                self.plus_button.setStyleSheet(self._button_style(False))
            else:
                self.plus_button.setStyleSheet(_pill_button_style(disabled=True))

    def _on_add_clicked(self):
        if len(self.items) >= MAX_POSTIT_CARDS:
            return
        self._suppress_next_new_card_menu = True
        self.item_added.emit()


    def set_active_card(self, idx: int):
        if idx < 0 or idx >= len(self.items):
            return
        self.active_index = idx
        self.stack.setCurrentIndex(idx)
        self._apply_active()
        self._update_index_button_states()

    def _apply_active(self):
        for i, c in enumerate(self.cards):
            c.set_active(i == self.active_index)
        self._update_index_button_states()


class PostItBar(QWidget):
    fabric_deleted = Signal(int)
    trim_deleted = Signal(int)

    fabric_item_changed = Signal(int, dict)
    trim_item_changed = Signal(int, dict)

    fabric_item_added = Signal()
    trim_item_added = Signal()

    basic_data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        self.basic = BasicInfoPostIt(self)
        self.basic.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.basic.data_changed.connect(self.basic_data_changed.emit)

        self.fabric = PostItStack("fabric", self)
        self.trim = PostItStack("trim", self)
        self.fabric.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.trim.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.fabric.item_deleted.connect(self.fabric_deleted.emit)
        self.trim.item_deleted.connect(self.trim_deleted.emit)

        self.fabric.item_changed.connect(self.fabric_item_changed.emit)
        self.trim.item_changed.connect(self.trim_item_changed.emit)

        self.fabric.item_added.connect(self.fabric_item_added.emit)
        self.trim.item_added.connect(self.trim_item_added.emit)

        lay.addWidget(self.basic, 1)
        lay.addWidget(self.fabric, 1)
        lay.addWidget(self.trim, 1)

    def set_data(self, header: Dict[str, str], fabrics: List[Dict[str, str]], trims: List[Dict[str, str]]):
        self.basic.set_header_data(header or {})
        self.fabric.set_items(fabrics or [])
        self.trim.set_items(trims or [])
