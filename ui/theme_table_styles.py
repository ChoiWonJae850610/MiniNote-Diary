from __future__ import annotations

from ui.theme_tokens import THEME
from ui.theme_input_styles import table_line_edit_style


def table_widget_style() -> str:
    t = THEME
    return (
        "QTableWidget{"
        f"background:{t.color_window};"
        f"border:1px solid {t.color_border};"
        "border-radius:12px;"
        "gridline-color:transparent;"
        "selection-background-color:transparent;"
        f"selection-color:{t.color_text};"
        "padding:4px;"
        "}"
        "QHeaderView::section{"
        f"background:{t.color_surface};"
        f"color:{t.color_text_soft};"
        "border:none;"
        f"border-bottom:1px solid {t.color_border_soft};"
        "padding:8px;"
        "font-weight:600;"
        "}"
        "QTableWidget::item{"
        "border:1px solid transparent;"
        "padding:4px;"
        "}"
        "QTableWidget::item:selected{"
        f"background:{t.color_surface_alt};"
        f"color:{t.color_text};"
        f"border:1px solid {t.color_border_soft};"
        "}"
        + table_line_edit_style(prefix="QTableWidget ")
    )
