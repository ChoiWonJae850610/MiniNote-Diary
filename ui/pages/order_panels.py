from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

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


class TemplateListCard(QFrame):
    def __init__(self, *, title: str, subtitle: str, meta_lines: list[str], parent=None):
        super().__init__(parent)
        self.setObjectName('listCard')
        self._selected = False
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
        self._apply_selected_style(False)

    def set_selected(self, selected: bool) -> None:
        if self._selected == selected:
            return
        self._selected = selected
        self._apply_selected_style(selected)

    def _apply_selected_style(self, selected: bool) -> None:
        if selected:
            self.setStyleSheet(
                f"QFrame#listCard{{background:{THEME.color_window};border:1px solid {THEME.color_primary};border-radius:14px;}}"
            )
        else:
            self.setStyleSheet(
                f"QFrame#listCard{{background:{THEME.color_surface};border:1px solid {THEME.color_border_soft};border-radius:14px;}}"
            )


__all__ = [
    'TemplateListCard',
    'add_panel_title',
    'create_order_panel',
    'make_order_value_label',
]
