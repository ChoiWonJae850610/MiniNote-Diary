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


from ui.theme import (
    THEME,
    card_colors,
    delete_button_style,
    disabled_index_button_style,
    display_field_style,
    editing_line_edit_style,
    field_label_style,
    hex_to_rgba,
    index_button_style,
    input_line_edit_style,
    menu_style,
    plain_text_edit_style,
    read_only_line_edit_style,
    title_badge_style,
    tool_button_style,
    unit_button_style,
)

# ---------- constants ----------
FIELD_H = THEME.field_height
CARD_RADIUS = THEME.card_radius
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


class SectionContainer(QWidget):
    """Shared section layout: top label/index row + card body."""

    def __init__(self, header_widget: QWidget, body_widget: QWidget, *,
                 parent=None, spacing: int = 6, header_alignment=Qt.AlignLeft):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(spacing)
        self.header_widget = header_widget
        self.body_widget = body_widget

        if header_alignment is None:
            root.addWidget(header_widget)
        else:
            root.addWidget(header_widget, 0, header_alignment)
        root.addWidget(body_widget, 1)


class SectionTitleBadge(QLabel):
    def __init__(self, text: str, parent=None, **style_kwargs):
        super().__init__(text, parent)
        self.setFixedHeight(28)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet(title_badge_style(**style_kwargs))


def _make_calendar_icon(size: int = 16) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setPen(QPen(QColor(THEME.color_icon), 2))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(1, 2, size - 2, size - 3, 3, 3)
    p.drawLine(2, 6, size - 3, 6)
    p.setPen(QPen(QColor(THEME.color_icon), 2))
    p.drawLine(5, 1, 5, 5)
    p.drawLine(size - 6, 1, size - 6, 5)
    p.end()
    return QIcon(pm)


def _make_down_icon(size: int = 12) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    pen = QPen(QColor(THEME.color_icon), 2)
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

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            _move_focus(self)
            event.accept()
            return
        if event.key() == Qt.Key_Backtab:
            _move_focus(self, backward=True)
            event.accept()
            return
        super().keyPressEvent(event)


class _ClickToEditLineEdit(QLineEdit):
    committed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFixedHeight(FIELD_H)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setTextMargins(0, 0, 0, 0)
        self._edit_start_text=""
        self._apply_style(editing=False)

    def _apply_style(self, editing: bool):
        # Keep border/padding consistent to avoid layout jitter when toggling edit mode.
        if not editing:
            self.setStyleSheet(read_only_line_edit_style())
        else:
            self.setStyleSheet(editing_line_edit_style())
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isReadOnly():
            self._edit_start_text=self.text()
            self.setReadOnly(False)
            self._apply_style(editing=True)
            self.setFocus()
            self.selectAll()
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._commit_lock()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
            self._commit_lock()
            _move_focus(self)
            event.accept()
            return
        if event.key() == Qt.Key_Backtab:
            self._commit_lock()
            _move_focus(self, backward=True)
            event.accept()
            return
        if event.key() == Qt.Key_Escape:
            self.setReadOnly(True)
            self._apply_style(editing=False)
            self.clearFocus()
            event.accept()
            return
        super().keyPressEvent(event)

    def _commit_lock(self):
        if not self.isReadOnly():
            changed = self.text() != self._edit_start_text
            self.setReadOnly(True)
            self._apply_style(editing=False)
            if changed:
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
        bg_hex, bd_hex = card_colors(kind)
        self._bg = QColor(bg_hex)
        self._bd = QColor(bd_hex)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(THEME.card_shadow_blur)
        shadow.setOffset(0, THEME.card_shadow_offset_y)
        shadow_color = QColor(THEME.color_shadow)
        shadow_color.setAlpha(28)
        shadow.setColor(shadow_color)
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
            pen = QPen(QColor(self._bd).darker(118), 2)
        p.setPen(pen)
        p.setBrush(self._bg)
        p.drawRoundedRect(r, CARD_RADIUS, CARD_RADIUS)


# ---------- basic info ----------
class BasicInfoPostIt(_PostItCardBase):
    data_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("basic", parent=parent)
        self.setMinimumSize(QSize(320, 198))
        self.setMaximumHeight(198)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 10)
        root.setSpacing(8)

        # date row
        date_row = QHBoxLayout()
        date_row.setSpacing(6)

        lbl_date = QLabel("날  짜", self)
        lbl_date.setFixedWidth(44)
        lbl_date.setFixedHeight(FIELD_H)
        lbl_date.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_date.setStyleSheet(field_label_style())
        date_row.addWidget(lbl_date)

        self._date_value = QDate.currentDate()
        self.date_text = QLabel(self._date_value.toString("yyyy-MM-dd"), self)
        self.date_text.setFixedHeight(FIELD_H)
        self.date_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_text.setStyleSheet(display_field_style())
        self.date_text.setMinimumWidth(118)

        self.btn_calendar = QToolButton(self)
        self.btn_calendar.setIcon(_make_calendar_icon(16))
        self.btn_calendar.setIconSize(QSize(16, 16))
        self.btn_calendar.setFixedSize(FIELD_H, FIELD_H)
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.setStyleSheet(tool_button_style())
        self.btn_calendar.clicked.connect(self._open_calendar)

        date_row.addWidget(self.date_text, 1)
        date_row.addWidget(self.btn_calendar)
        root.addLayout(date_row)

        # labels + fields grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        def mk_label(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet(field_label_style())
            return l

        self.style_no = _ClickToEditLineEdit(self)
        self.factory = _ClickToEditLineEdit(self)

        # product width auto
        self.style_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._style_no_min = 140
        self._style_no_max = 320
        self.style_no.textChanged.connect(self._adjust_style_width)
        self._adjust_style_width(self.style_no.text())

        grid.addWidget(mk_label("제품명"), 0, 0)
        grid.addWidget(self.style_no, 0, 1)
        grid.addWidget(mk_label("공  장"), 1, 0)
        grid.addWidget(self.factory, 1, 1)
        root.addLayout(grid)

        mg = QGridLayout()
        mg.setHorizontalSpacing(8)
        mg.setVerticalSpacing(5)
        mg.setContentsMargins(0, 2, 0, 0)

        self.cost = _MoneyLineEdit(self)
        self.labor = _MoneyLineEdit(self)
        self.loss = _MoneyLineEdit(self)
        self.sale_price = _MoneyLineEdit(self)

        for w in (self.cost, self.labor, self.loss, self.sale_price):
            w.setStyleSheet(input_line_edit_style())

        mg.addWidget(mk_label("원  가"), 0, 0)
        mg.addWidget(self.cost, 0, 1)
        mg.addWidget(mk_label("공  임"), 0, 2)
        mg.addWidget(self.labor, 0, 3)
        mg.addWidget(mk_label("로  스"), 1, 0)
        mg.addWidget(self.loss, 1, 1)
        mg.addWidget(mk_label("판매가"), 1, 2)
        mg.addWidget(self.sale_price, 1, 3)

        root.addLayout(mg)

        self.cost.textChanged.connect(self._sync_sale_price)
        self.labor.textChanged.connect(self._sync_sale_price)
        self.loss.textChanged.connect(self._sync_sale_price)

        self.style_no.committed.connect(lambda _v: self._emit_all())
        self.factory.committed.connect(lambda _v: self._emit_all())
        for w in (self.cost, self.labor, self.loss, self.sale_price):
            w.textChanged.connect(lambda _t: self._emit_all())

        self.setTabOrder(self.btn_calendar, self.style_no)
        self.setTabOrder(self.style_no, self.factory)
        self.setTabOrder(self.factory, self.cost)
        self.setTabOrder(self.cost, self.labor)
        self.setTabOrder(self.labor, self.loss)
        self.setTabOrder(self.loss, self.sale_price)

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
    save_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("change", parent=parent)
        self.setMinimumSize(QSize(340, 220))
        self._block = False

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 14)
        root.setSpacing(0)

        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("")
        self.editor.setStyleSheet(plain_text_edit_style())
        self.editor.installEventFilter(self)
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

    def eventFilter(self, obj, event):
        if obj is self.editor and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ControlModifier:
                self.save_requested.emit()
                event.accept()
                return True
        return super().eventFilter(obj, event)


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
        root.setContentsMargins(14, 16, 14, 12)
        root.setSpacing(8)

        self.btn_delete = QToolButton(self)
        self.btn_delete.setText("×")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setFixedSize(14, 14)
        self.btn_delete.setStyleSheet(delete_button_style())
        self.btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.index))

        vi = QGridLayout()
        vi.setHorizontalSpacing(8)
        vi.setVerticalSpacing(8)

        def mk_label(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet(field_label_style())
            return l

        self.vendor = _ClickToEditLineEdit(self)
        self.item = _ClickToEditLineEdit(self)
        self.vendor.set_text_silent(self.data.get("거래처", ""))
        self.item.set_text_silent(self.data.get("품목", ""))

        vi.addWidget(mk_label("원단처" if self.kind == "fabric" else "거래처"), 0, 0)
        vi.addWidget(self.vendor, 0, 1)
        vi.addWidget(mk_label("품  목"), 1, 0)
        vi.addWidget(self.item, 1, 1)
        root.addLayout(vi)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        def mk_label2(t: str) -> QLabel:
            l = QLabel(t, self)
            l.setFixedWidth(44)
            l.setFixedHeight(FIELD_H)
            l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            l.setStyleSheet(field_label_style())
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
        self.unit_btn.setStyleSheet(unit_button_style())
        self._apply_unit_button_text()
        self._unit_menu = QMenu(self.unit_btn)
        self._unit_menu.setStyleSheet(menu_style())
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
            w.setStyleSheet(input_line_edit_style())

        self.price.setText(self.data.get("단가", ""))
        self.total.setText(self.data.get("총액", ""))

        grid.addWidget(mk_label2("수  량"), 0, 0)
        grid.addWidget(self.qty, 0, 1)
        grid.addWidget(mk_label2("단위"), 0, 2)
        grid.addWidget(self.unit_btn, 0, 3)
        grid.addWidget(mk_label2("단  가"), 1, 0)
        grid.addWidget(self.price, 1, 1, 1, 3)
        grid.addWidget(mk_label2("총  액"), 2, 0)
        grid.addWidget(self.total, 2, 1, 1, 3)
        root.addLayout(grid)

        # connections
        self.vendor.committed.connect(lambda v: self._commit("거래처", v))
        self.item.committed.connect(lambda v: self._commit("품목", v))
        self.qty.committed.connect(lambda v: self._on_qty_committed(v))
        self.qty.textChanged.connect(lambda _t: self._recalc_total())
        self.price.textChanged.connect(lambda _t: self._on_price_changed())
        self.total.textChanged.connect(lambda _t: (None if self._block_total else self._commit("총액", self.total.text())))

        self.setTabOrder(self.vendor, self.item)
        self.setTabOrder(self.item, self.qty)
        self.setTabOrder(self.qty, self.unit_btn)
        self.setTabOrder(self.unit_btn, self.price)
        self.setTabOrder(self.price, self.total)

        self.setMinimumSize(QSize(320, 198))
        self.setMaximumHeight(198)
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
        self.btn_delete.move(self.width() - 18, 6)
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

        self.index_row_wrap = QWidget(self)
        self.index_row_wrap.setFixedHeight(28)
        self.index_row = QHBoxLayout(self.index_row_wrap)
        self.index_row.setContentsMargins(0, 0, 0, 0)
        self.index_row.setSpacing(6)

        self.stack_host = QWidget(self)
        self.stack = QStackedLayout(self.stack_host)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.section = SectionContainer(
            self.index_row_wrap,
            self.stack_host,
            parent=self,
            spacing=6,
            header_alignment=None,
        )
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.section)

        self._rebuild_index_buttons()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(232)

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
        if active:
            return index_button_style(True)
        return index_button_style(False)

    def _make_index_button(self, txt: str) -> QToolButton:
        b = QToolButton(self)
        b.setText(txt)
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedSize(24, 24)
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
                self.plus_button.setStyleSheet(disabled_index_button_style())

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
        lay.setSpacing(14)

        self.basic = BasicInfoPostIt(self)
        self.basic.data_changed.connect(self.basic_data_changed.emit)

        self.basic_title = SectionTitleBadge("기본정보", self, horizontal_padding=12)
        self.basic_wrap = SectionContainer(self.basic_title, self.basic, parent=self, spacing=6)

        self.fabric = PostItStack("fabric", self)
        self.trim = PostItStack("trim", self)

        self.fabric.item_deleted.connect(self.fabric_deleted.emit)
        self.trim.item_deleted.connect(self.trim_deleted.emit)

        self.fabric.item_changed.connect(self.fabric_item_changed.emit)
        self.trim.item_changed.connect(self.trim_item_changed.emit)

        self.fabric.item_added.connect(self.fabric_item_added.emit)
        self.trim.item_added.connect(self.trim_item_added.emit)

        lay.addWidget(self.basic_wrap, 1)
        lay.addWidget(self.fabric, 1)
        lay.addWidget(self.trim, 1)

    def set_data(self, header: Dict[str, str], fabrics: List[Dict[str, str]], trims: List[Dict[str, str]]):
        self.basic.set_header_data(header or {})
        self.fabric.set_items(fabrics or [])
        self.trim.set_items(trims or [])
