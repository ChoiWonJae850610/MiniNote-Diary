from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.layout_metrics import OrderPageLayout
from ui.theme import THEME
from ui.widget_factory import make_hint_label, make_meta_label, make_panel_frame, make_section_title_label, make_value_label


def create_order_panel(parent: QWidget, *, spacing: int) -> tuple[QWidget, QVBoxLayout]:
    panel = make_panel_frame(parent)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(
        THEME.page_section_padding,
        THEME.page_section_padding,
        THEME.page_section_padding,
        THEME.page_section_padding,
    )
    layout.setSpacing(spacing)
    return panel, layout



def add_panel_title(layout: QVBoxLayout, parent: QWidget, title: str) -> None:
    layout.addWidget(make_section_title_label(title, parent))



def make_order_value_label(text: str) -> QLabel:
    label = make_value_label(text, min_height=THEME.order_input_height - 2)
    label.setWordWrap(True)
    return label


class TemplateListCard(QWidget):
    def __init__(self, *, title: str, subtitle: str, meta_lines: list[str], parent=None):
        super().__init__(parent)
        self.setObjectName('listCard')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            OrderPageLayout.TEMPLATE_CARD_MARGIN,
            OrderPageLayout.TEMPLATE_CARD_MARGIN,
            OrderPageLayout.TEMPLATE_CARD_MARGIN,
            OrderPageLayout.TEMPLATE_CARD_MARGIN,
        )
        layout.setSpacing(OrderPageLayout.TEMPLATE_CARD_SPACING)
        layout.addWidget(make_section_title_label(title, self))
        layout.addWidget(make_hint_label(subtitle, self))
        for line in meta_lines:
            layout.addWidget(make_meta_label(line, self))


__all__ = [
    'TemplateListCard',
    'add_panel_title',
    'create_order_panel',
    'make_order_value_label',
]
