# ui/postit_widgets.py
from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, QRectF, Signal, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QFont
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
    """원화 표시: '\' 대신 '원' 접미사."""
    v = (v or "").strip()
    if not v:
        return ""
    if v.endswith("원"):
        return v
    return f"{v}원"


def _safe(v: str) -> str:
    return (v or "").strip()


def _hi(p: QPainter, x: int, y: int, w: int, h: int, color: QColor, radius: int = 7, alpha: int = 105):
    """형광펜 같은 하이라이트 (반투명 배경)"""
    c = QColor(color)
    c.setAlpha(alpha)
    p.setPen(Qt.NoPen)
    p.setBrush(c)
    p.drawRoundedRect(QRectF(x, y, w, h), radius, radius)


# ===== 강조 색상 규칙 (요청 반영)
# - 기본정보: 날짜 / 제품명 / 판매가
# - 원단/부자재: 총액
# - 판매가 + (원단/부자재)총액 = 같은 색
# - 날짜, 제품명은 서로 다른 색
H_DATE = QColor("#A7F3D0")      # 민트
H_PRODUCT = QColor("#BFDBFE")   # 연파랑
H_MONEY = QColor("#FDE68A")     # 연노랑 (판매가/총액 공통)


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
        y = 32
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

        # ===== Top lines (날짜/제품명만 강조)
        # 날짜 (강조)
        _hi(p, x, y - 16, min(230, w), 22, H_DATE)
        p.setFont(f_top)
        p.setPen(QColor("#1F1F1F"))
        p.drawText(x + 6, y, f"날짜: {date}")
        y += 22

        # 제품명 (강조)
        _hi(p, x, y - 16, min(280, w), 22, H_PRODUCT)
        p.setFont(f_top)
        p.setPen(QColor("#1F1F1F"))
        p.drawText(x + 6, y, f"제품명: {style_no}")
        y += 22

        # 공장 (강조 없음)
        p.setFont(f_top)
        p.setPen(QColor("#2A2A2A"))
        p.drawText(x, y, f"공장: {factory}")
        y += 16

        # ===== Money block (테이블 느낌 최소화: 강조는 '판매가'만)
        col_gap = 10
        col_w = int((w - col_gap) / 2)
        row_h = 26
        rx = x + col_w + col_gap

        # row1: 원가 / 공임 (강조 없음)
        y += 12
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x + 6, y, "원가")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 58, y + 1, _krw(cost))

        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(rx + 6, y, "공임")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(rx + 58, y + 1, _krw(labor))
        y += row_h

        # row2: 로스 / 판매가 (판매가만 강조 + 판매가/총액 공통색)
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x + 6, y, "로스")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 58, y + 1, _krw(loss))

        # 판매가 강조 (오른쪽 칸만 하이라이트)
        _hi(p, rx, y - 16, col_w, 22, H_MONEY)
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(rx + 6, y, "판매가")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(rx + 58, y + 1, _krw(sale))


class PostItCard(QWidget):
    """원단/부자재 1장. hover 시 X 표시 → 삭제"""

    delete_clicked = Signal(int)

    def __init__(self, kind: str, index: int, data: Dict[str, str], parent=None):
        super().__init__(parent)
        self.kind = kind
        self.index = index
        self.data = data
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

        p.setPen(QPen(bd, 2))
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
        y += 16

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

        # 총액만 강조 (판매가와 같은 색)
        # 오른쪽 하단 영역에 크게
        box_w = int(w * 0.52)
        bx = x + (w - box_w)
        by = y - 16
        _hi(p, bx, by, box_w, 24, H_MONEY)

        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(bx + 6, y, "총액")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(bx + 44, y + 1, _krw(total))


class PostItStack(QWidget):
    """여러 장을 겹쳐 스택처럼 보이게"""

    item_deleted = Signal(int)

    def __init__(self, kind: str, title: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.title = title
        self.items: List[Dict[str, str]] = []
        self.cards: List[PostItCard] = []
        self.setMinimumHeight(170)

    def sizeHint(self) -> QSize:
        return QSize(330, 175)

    def set_items(self, items: List[Dict[str, str]]):
        self.items = list(items or [])
        self._rebuild()

    def _rebuild(self):
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        self.cards = []

        for idx, it in enumerate(self.items):
            card = PostItCard(self.kind, idx, it, parent=self)
            card.delete_clicked.connect(self.item_deleted.emit)
            card.show()
            self.cards.append(card)

        self._layout_cards()
        self.update()

    def resizeEvent(self, event):
        self._layout_cards()
        super().resizeEvent(event)

    def _layout_cards(self):
        base_w = self.width()
        card_w = max(280, min(330, base_w - 20))
        card_h = 135
        x0 = int((base_w - card_w) / 2)
        y0 = 10  # ✅ 위의 "원단정보/부자재정보" 라벨 제거했으니 더 위로 올림
        dx = 10
        dy = 16

        for i, card in enumerate(self.cards):
            card.setFixedSize(card_w, card_h)
            card.move(x0 + dx * i, y0 + dy * i)
            card.raise_()

        total_h = y0 + card_h + dy * max(0, (len(self.cards) - 1)) + 14
        self.setMinimumHeight(max(155, total_h))

    def paintEvent(self, event):
        # ✅ 요청: 포스트잇 위 "원단정보/부자재정보" 라벨 제거
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