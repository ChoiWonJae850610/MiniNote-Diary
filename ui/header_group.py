from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QDateEdit, QSizePolicy
from PySide6.QtCore import QDate


class HeaderGroup(QGroupBox):
    def __init__(self):
        super().__init__("제품 정보")

        layout = QFormLayout(self)
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setFixedHeight(26)
        self.date.setDate(QDate.currentDate())  # ✅ 오늘 날짜로

        self.style_no = QLineEdit()
        self.factory = QLineEdit()
        self.store = QLineEdit()

        for w in (self.style_no, self.factory, self.store):
            w.setFixedHeight(26)

        layout.addRow("날   짜", self.date)
        layout.addRow("제품명", self.style_no)
        layout.addRow("공   장", self.factory)
        layout.addRow("매   장", self.store)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def get_data(self):
        return {
            "date": self.date.date().toString("yyyy-MM-dd"),
            "style_no": self.style_no.text(),
            "factory": self.factory.text(),
            "store": self.store.text(),
        }