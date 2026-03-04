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


def _won(v: str) -> str:
    """원화 표시: 사용자가 요청한 '\' 단위."""
    v = (v or "").strip()
    if not v:
        return ""
    # 이미 사용자가 \를 넣는 경우 중복 방지
    if v.startswith("\\"):
        return v
    return f"\\{v}"


def _safe(v: str) -> str:
    return (v or "").strip()


def _hi(p: QPainter, x: int, y: int, w: int, h: int, color: QColor, radius: int = 6):
    """형광펜 같은 하이라이트 (반투명)"""
    c = QColor(color)
    c.setAlpha(90)
    p.setPen(Qt.NoPen)
    p.setBrush(c)
    p.drawRoundedRect(QRectF(x, y, w, h), radius, radius)


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
        y = 30
        w = self.width() - 40

        # ===== top 3 lines (읽기 쉬운 고정 구조)
        f_label = QFont()
        f_label.setPointSize(10)
        f_label.setBold(True)

        p.setPen(QPen(QColor("#2A2A2A"), 1))
        p.setFont(f_label)
        p.drawText(x, y, f"날짜: {date}")
        y += 20
        p.drawText(x, y, f"제품명: {style_no}")
        y += 20
        p.drawText(x, y, f"공장: {factory}")
        y += 12

        # ===== money block (형광펜 느낌 + 굵은 값)
        # 라벨은 작게, 값은 크게/굵게
        f_small = QFont()
        f_small.setPointSize(9)
        f_small.setBold(False)

        f_big = QFont()
        f_big.setPointSize(11)
        f_big.setBold(True)

        # 2열 배치
        col_gap = 10
        col_w = int((w - col_gap) / 2)
        row_h = 26

        # row1: 원가 / 공임
        y += 8
        _hi(p, x, y - 18, w, row_h + 8, QColor("#FFF08A"))  # 노랑 형광펜 느낌

        # left cell
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x + 6, y, "원가")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 58, y + 1, _won(cost))

        # right cell
        rx = x + col_w + col_gap
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(rx + 6, y, "공임")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(rx + 58, y + 1, _won(labor))

        y += row_h

        # row2: 로스 / 판매가 (판매가 강조 색감 조금 다르게)
        _hi(p, x, y - 18, w, row_h + 8, QColor("#CFFFD6"))  # 연두 형광펜 느낌

        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x + 6, y, "로스")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 58, y + 1, _won(loss))

        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(rx + 6, y, "판매가")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(rx + 58, y + 1, _won(sale))


class PostItCard(QWidget):
    """원단/부자재 1장(회전 없음). hover 시 X 표시 → 삭제"""

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

        # 거래처/품목: 크게, 눈에 띄게
        f_head = QFont()
        f_head.setPointSize(11)
        f_head.setBold(True)

        p.setFont(f_head)
        p.setPen(QColor("#1F1F1F"))
        p.drawText(x, y, f"{vendor}")
        y += 20
        p.drawText(x, y, f"{item}")
        y += 10

        # 아래 정보 블록: 수량/단가/총액
        f_small = QFont()
        f_small.setPointSize(9)
        f_small.setBold(False)

        f_big = QFont()
        f_big.setPointSize(11)
        f_big.setBold(True)

        # 수량 강조 (연노랑 형광펜)
        y += 10
        _hi(p, x, y - 16, w, 24, QColor("#FFF08A"))
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x + 6, y, "수량")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 56, y + 1, f"{qty} {unit}".strip())

        # 단가/총액: 총액은 더 강조 (연두 형광펜)
        y += 26
        _hi(p, x, y - 16, w, 24, QColor("#CFFFD6"))
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x + 6, y, "단가")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + 56, y + 1, _won(price))

        # 총액 (더 오른쪽에 배치 + 굵게)
        p.setFont(f_small)
        p.setPen(QColor("#444"))
        p.drawText(x + int(w * 0.52), y, "총액")
        p.setFont(f_big)
        p.setPen(QColor("#111"))
        p.drawText(x + int(w * 0.52) + 46, y + 1, _won(total))


class PostItStack(QWidget):
    """여러 장을 겹쳐 스택처럼 보이게(회전 없음)"""

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
        y0 = 26
        dx = 10
        dy = 16

        for i, card in enumerate(self.cards):
            card.setFixedSize(card_w, card_h)
            card.move(x0 + dx * i, y0 + dy * i)
            card.raise_()

        total_h = y0 + card_h + dy * max(0, (len(self.cards) - 1)) + 14
        self.setMinimumHeight(max(155, total_h))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        # 제목만 표시 (✅ "(없음)" 제거)
        p.setPen(QPen(QColor("#555"), 1))
        f = QFont()
        f.setPointSize(10)
        f.setBold(True)
        p.setFont(f)
        p.drawText(8, 18, f"{self.title}")


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