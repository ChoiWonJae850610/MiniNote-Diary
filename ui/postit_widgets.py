# ui/postit_widgets.py
from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, QRectF, Signal, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget, QToolButton, QHBoxLayout, QVBoxLayout, QLabel, QPushButton


def _color(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#FFF2A8")  # 노랑
    if kind == "fabric":
        return QColor("#CFF4FF")  # 하늘
    return QColor("#E6D7FF")     # 보라


def _border(kind: str) -> QColor:
    if kind == "basic":
        return QColor("#E4D27D")
    if kind == "fabric":
        return QColor("#9AD7E8")
    return QColor("#C0A6FF")


class BasicInfoPostIt(QWidget):
    """기본정보 요약 1장 (없으면 숨김)"""
    edit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kind = "basic"
        self.header: Dict[str, str] = {}
        self.setMinimumHeight(140)

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
        return QSize(360, 150)

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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        bg = _color(self.kind)
        border = _border(self.kind)

        r = QRectF(8, 8, self.width() - 16, self.height() - 16)
        painter.setPen(QPen(border, 2))
        painter.setBrush(bg)
        painter.drawRoundedRect(r, 14, 14)

        painter.setPen(QPen(QColor("#222"), 1))
        f = QFont()
        f.setPointSize(10)
        painter.setFont(f)

        date = self.header.get("date", "")
        style_no = self.header.get("style_no", "")
        factory = self.header.get("factory", "")

        cost = self.header.get("cost_display", "")
        labor = self.header.get("labor_display", "")
        loss = self.header.get("loss_display", "")
        sale = self.header.get("sale_price_display", "")

        lines = [
            f"날짜: {date}",
            f"제품명: {style_no}",
            f"공장: {factory}",
            "",
            f"원가 {cost} / 공임 {labor}",
            f"로스 {loss} / 판매가 {sale}",
        ]

        x = 22
        y = 30
        for line in lines:
            painter.drawText(x, y, line)
            y += 18


class PostItCard(QWidget):
    """원단/부자재 1장(hover 시 삭제 버튼 노출)"""
    delete_clicked = Signal(int)

    def __init__(self, kind: str, index: int, data: Dict[str, str], parent=None):
        super().__init__(parent)
        self.kind = kind
        self.index = index
        self.data = data
        self.rotation_deg = 0.0
        self.setMouseTracking(True)

        self.btn_delete = QToolButton(self)
        self.btn_delete.setText("×")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setVisible(False)
        self.btn_delete.setFixedSize(20, 20)
        self.btn_delete.setStyleSheet(
            "QToolButton{border:none;border-radius:10px;background:rgba(0,0,0,0.12);font-weight:bold;}"
            "QToolButton:hover{background:rgba(0,0,0,0.22);}"
        )
        self.btn_delete.clicked.connect(self._on_delete)

        self.setMinimumHeight(110)

    def _on_delete(self):
        self.delete_clicked.emit(self.index)

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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        bg = _color(self.kind)
        border = _border(self.kind)

        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2

        painter.translate(cx, cy)
        painter.rotate(self.rotation_deg)

        rect_w = w - 24
        rect_h = h - 24
        r = QRectF(-rect_w / 2, -rect_h / 2, rect_w, rect_h)

        painter.setPen(QPen(border, 2))
        painter.setBrush(bg)
        painter.drawRoundedRect(r, 14, 14)

        painter.setPen(QPen(QColor("#222"), 1))
        f = QFont()
        f.setPointSize(10)
        painter.setFont(f)

        vendor = self.data.get("거래처", "")
        item = self.data.get("품목", "")
        qty = self.data.get("수량", "")
        unit = self.data.get("단위", "")
        price = self.data.get("단가", "")
        total = self.data.get("총액", "")

        lines = [
            f"거래처: {vendor}",
            f"품목: {item}",
            f"수량: {qty} {unit}",
            f"단가: {price}  /  총액: {total}",
        ]

        x = -rect_w / 2 + 16
        y = -rect_h / 2 + 26
        for line in lines:
            painter.drawText(int(x), int(y), line)
            y += 18


class PostItStack(QWidget):
    """여러 장을 겹쳐 스택처럼 보이게"""
    item_deleted = Signal(int)

    def __init__(self, kind: str, title: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.title = title
        self.items: List[Dict[str, str]] = []
        self.cards: List[PostItCard] = []
        self.setMinimumHeight(190)

    def sizeHint(self) -> QSize:
        return QSize(360, 200)

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
            rot_cycle = [-6.0, -2.0, 3.0, 7.0, -4.0]
            card.rotation_deg = rot_cycle[idx % len(rot_cycle)]
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
        card_w = max(300, min(360, base_w - 20))
        card_h = 120

        x0 = int((base_w - card_w) / 2)
        y0 = 26

        dx = 10
        dy = 16

        for i, card in enumerate(self.cards):
            card.setFixedSize(card_w, card_h)
            card.move(x0 + dx * i, y0 + dy * i)
            card.raise_()

        total_h = y0 + card_h + dy * max(0, (len(self.cards) - 1)) + 14
        self.setMinimumHeight(max(170, total_h))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(QColor("#555"), 1))
        f = QFont()
        f.setPointSize(10)
        f.setBold(True)
        painter.setFont(f)

        suffix = "" if self.items else " (없음)"
        painter.drawText(8, 18, f"{self.title}{suffix}")


class PostItBar(QWidget):
    """
    이미지 아래 '기본정보-원단정보-부자재정보' 가로 1열 배치
    """
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

        # 최초엔 기본정보 숨김
        self.basic.setVisible(False)

    def set_data(self, header: Dict[str, str], fabrics: List[Dict[str, str]], trims: List[Dict[str, str]]):
        self.basic.set_header_data(header or {})
        self.fabric.set_items(fabrics or [])
        self.trim.set_items(trims or [])