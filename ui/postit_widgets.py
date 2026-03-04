# ui/postit_widgets.py
from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, QRectF, Signal, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QFontMetrics
from PySide6.QtWidgets import QWidget, QToolButton, QHBoxLayout


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


class BasicInfoPostIt(QWidget):
    """기본정보 요약 1장 (없으면 숨김)"""

    edit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kind = "basic"
        self.header: Dict[str, str] = {}
        self.setMinimumHeight(160)

        self.btn_edit = QToolButton(self)
        self.btn_edit.setText("편집")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setStyleSheet(
            "QToolButton{border:none;background:rgba(0,0,0,0.10);padding:4px 8px;border-radius:10px;}"
            "QToolButton:hover{background:rgba(0,0,0,0.18);}"
        )
        self.btn_edit.clicked.connect(self.edit_requested.emit)
        self.btn_edit.hide()
        self.setMouseTracking(True)

    def sizeHint(self) -> QSize:
        return QSize(330, 175)

    def set_header_data(self, header: Dict[str, str]):
        self.header = header or {}
        has = any((v or "").strip() for v in self.header.values())
        self.setVisible(has)
        self.update()

    def enterEvent(self, e):
        self.btn_edit.setVisible(True)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.btn_edit.setVisible(False)
        super().leaveEvent(e)

    def resizeEvent(self, e):
        self.btn_edit.move(self.width() - 60, 10)
        super().resizeEvent(e)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        bg = _color(self.kind)
        bd = _border(self.kind)
        r = QRectF(8, 8, self.width() - 16, self.height() - 16)

        p.setPen(QPen(bd, 2))
        p.setBrush(bg)
        p.drawRoundedRect(r, 14, 14)

        # ===== data
        date = _safe(self.header.get("date", ""))
        style_no = _safe(self.header.get("style_no", ""))
        factory = _safe(self.header.get("factory", ""))

        cost = _safe(self.header.get("cost_display", ""))
        labor = _safe(self.header.get("labor_display", ""))
        loss = _safe(self.header.get("loss_display", ""))
        sale = _safe(self.header.get("sale_price_display", ""))

        x = 20
        y = 34
        w = self.width() - 40

        # ===== Fonts
        f_top = QFont()
        f_top.setPointSize(10)
        f_top.setBold(True)

        f_small = QFont()
        f_small.setPointSize(9)
        f_small.setBold(False)

        f_big = QFont()
        f_big.setPointSize(11)
        f_big.setBold(True)

        # ===== Top lines (하이라이트는 텍스트 길이만)
        # 날짜
        line1 = f"날짜: {date}"
        _hi_text(p, x, y, line1, f_top, H_DATE)
        p.setFont(f_top)
        p.setPen(QColor("#1F1F1F"))
        p.drawText(x, y, line1)
        y += 22

        # 제품명
        line2 = f"제품명: {style_no}"
        _hi_text(p, x, y, line2, f_top, H_PRODUCT)
        p.setFont(f_top)
        p.setPen(QColor("#1F1F1F"))
        p.drawText(x, y, line2)
        y += 22

        # 공장(하이라이트 없음)
        p.setFont(f_top)
        p.setPen(QColor("#2A2A2A"))
        p.drawText(x, y, f"공장: {factory}")
        y += 18

        # ===== Money block (테이블 느낌 최소화: 판매가만 하이라이트)
        col_gap = 10
        col_w = int((w - col_gap) / 2)
        rx = x + col_w + col_gap

        # row1: 원가 / 공임
        y += 10
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x, y, "원가")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 52, y + 1, _krw(cost))

        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(rx, y, "공임")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(rx + 52, y + 1, _krw(labor))
        y += 26

        # row2: 로스 / 판매가 (판매가만 텍스트 길이만큼 하이라이트)
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x, y, "로스")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 52, y + 1, _krw(loss))

        sale_label = "판매가"
        sale_value = _krw(sale)
        # 판매가 라벨+값을 한 덩어리로 하이라이트 (텍스트 길이만)
        sale_line = f"{sale_label}  {sale_value}".strip()
        _hi_text(p, rx, y, sale_line, f_big, H_MONEY, pad_x=14)

        # 실제 출력은 라벨/값 분리해서 기존 레이아웃 유지
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(rx, y, sale_label)
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(rx + 52, y + 1, sale_value)


class PostItCard(QWidget):
    """원단/부자재 1장. 클릭하면 앞으로(활성화). hover 시 X 표시 → 삭제"""

    delete_clicked = Signal(int)
    selected = Signal(int)

    def __init__(self, kind: str, index: int, data: Dict[str, str], parent=None):
        super().__init__(parent)
        self.kind = kind
        self.index = index
        self.data = data
        self.is_active = False
        self.setMouseTracking(True)
        self.setMinimumHeight(135)

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

    def set_active(self, active: bool):
        self.is_active = active
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.index)
        super().mousePressEvent(event)

    def enterEvent(self, event):
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

        bg = _color(self.kind)
        bd = _border(self.kind)
        r = QRectF(8, 8, self.width() - 16, self.height() - 16)

        # 활성 카드면 테두리 더 진하고 두껍게(선택된 느낌)
        if self.is_active:
            pen = QPen(QColor(bd).darker(140), 3)
        else:
            pen = QPen(bd, 2)

        p.setPen(pen)
        p.setBrush(bg)
        p.drawRoundedRect(r, 14, 14)

        vendor = _safe(self.data.get("거래처", ""))
        item = _safe(self.data.get("품목", ""))
        qty = _safe(self.data.get("수량", ""))
        unit = _safe(self.data.get("단위", ""))
        price = _safe(self.data.get("단가", ""))
        total = _safe(self.data.get("총액", ""))

        x = 18
        y = 32
        w = self.width() - 36

        f_head = QFont()
        f_head.setPointSize(11)
        f_head.setBold(True)

        f_small = QFont()
        f_small.setPointSize(9)
        f_small.setBold(False)

        f_big = QFont()
        f_big.setPointSize(11)
        f_big.setBold(True)

        # 거래처/품목
        p.setFont(f_head)
        p.setPen(QColor("#1F1F1F"))
        p.drawText(x, y, vendor)
        y += 20
        p.drawText(x, y, item)
        y += 18

        # 수량/단가 (강조 없음)
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x, y, "수량")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 50, y + 1, f"{qty} {unit}".strip())
        y += 22

        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x, y, "단가")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 50, y + 1, _krw(price))

        # 총액만 하이라이트 (판매가와 같은 색, 텍스트 길이만)
        total_line = f"총액  {_krw(total)}".strip()
        # 오른쪽 하단쪽으로 배치
        by = y
        bx = x + int(w * 0.50)
        p.setFont(f_big)
        _hi_text(p, bx, by + 1, total_line, f_big, H_MONEY, pad_x=16)

        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(bx, by, "총액")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(bx + 44, by + 1, _krw(total))


class PostItStack(QWidget):
    """여러 장을 겹쳐 스택처럼 보이게. 클릭으로 앞으로 가져오기."""

    item_deleted = Signal(int)

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
            card = PostItCard(self.kind, idx, it, parent=self)
            card.delete_clicked.connect(self.item_deleted.emit)
            card.selected.connect(self.set_active_card)
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
    basic_edit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.basic = BasicInfoPostIt()
        self.basic.edit_requested.connect(self.basic_edit_requested.emit)

        self.fabric = PostItStack(kind="fabric", title="원단정보")
        self.trim = PostItStack(kind="trim", title="부자재정보")

        self.fabric.item_deleted.connect(self.fabric_deleted.emit)
        self.trim.item_deleted.connect(self.trim_deleted.emit)

        layout.addWidget(self.basic, 1)
        layout.addWidget(self.fabric, 1)
        layout.addWidget(self.trim, 1)

        self.basic.setVisible(False)

    def set_data(self, header: Dict[str, str], fabrics: List[Dict[str, str]], trims: List[Dict[str, str]]):
        self.basic.set_header_data(header or {})
        self.fabric.set_items(fabrics or [])
        self.trim.set_items(trims or [])