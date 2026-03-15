from __future__ import annotations

from ui.theme_tokens import THEME, hex_to_rgba


def title_label_style(font_px: int | None = None, color: str | None = None, padding_left: int = 0) -> str:
    t = THEME
    return (
        f"QLabel{{font-weight:700;color:{color or t.color_text_soft};background:transparent;"
        f"font-size:{font_px or t.section_title_font_px}px;padding-left:{padding_left}px;}}"
    )


def page_title_style(font_px: int | None = None) -> str:
    return title_label_style(font_px=font_px or THEME.page_title_font_px, color=THEME.color_text)


def panel_title_style(font_px: int | None = None) -> str:
    return title_label_style(font_px=font_px or THEME.panel_title_font_px, color=THEME.color_text)


def title_badge_style(font_px: int | None = None, color: str | None = None,
                      border_color: str | None = None, background: str | None = None,
                      horizontal_padding: int = 12) -> str:
    t = THEME
    return (
        f"QLabel{{font-weight:700;color:{color or t.color_text_soft};"
        f"background:{background or t.color_window};"
        f"border:1px solid {border_color or t.color_border_hover};"
        f"border-radius:{t.control_radius + 4}px;"
        f"font-size:{font_px or t.section_title_font_px}px;"
        f"padding:2px {horizontal_padding}px;}}"
    )


def field_label_style() -> str:
    t = THEME
    return f"QLabel{{font-weight:600;color:{t.color_text_soft};background:transparent;}}"


def strong_field_label_style() -> str:
    t = THEME
    return f"QLabel{{font-weight:700;color:{t.color_text};background:transparent;}}"


def hint_label_style() -> str:
    t = THEME
    return f"QLabel{{background:transparent;color:{t.color_text_muted};padding:0 2px;}}"


def panel_frame_style(*, radius: int | None = None, background: str | None = None, border_color: str | None = None) -> str:
    t = THEME
    return (
        f"QFrame{{border:1px solid {border_color or t.color_border};"
        f"border-radius:{radius or t.panel_radius}px;"
        f"background:{background or t.color_surface};}}"
    )


def inner_panel_frame_style() -> str:
    return panel_frame_style(radius=THEME.panel_radius_sm, background=THEME.color_window, border_color=THEME.color_border_soft)


def list_widget_style() -> str:
    return (
        'QListWidget{border:none;background:transparent;outline:none;}'
        'QListWidget::item{border:none;padding:0px;}'
        'QListWidget::item:selected{background:transparent;}'
    )


def feedback_label_style() -> str:
    t = THEME
    return f'QLabel{{background:transparent;border:none;padding:0 {t.label_padding_x}px;color:{t.color_text};font-weight:700;}}'


def dialog_layout_margins() -> tuple[int, int, int, int]:
    return (14, 14, 14, 14)


def dialog_inner_margins() -> tuple[int, int, int, int]:
    return (20, 18, 20, 18)


def compact_popup_margins() -> tuple[int, int, int, int]:
    return (8, 8, 8, 8)


def status_row_margins() -> tuple[int, int, int, int]:
    return (14, 10, 14, 10)


def page_layout_margins(extra_x: int = 0, extra_y: int = 0) -> tuple[int, int, int, int]:
    t = THEME
    return (t.page_padding_x + extra_x, t.page_padding_y + extra_y, t.page_padding_x + extra_x, t.page_padding_y + extra_y)


def read_only_line_edit_style() -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_surface_alt, 0.90)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 8px;border-radius:{t.control_radius}px;}}"
        f"QLineEdit:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.10)};}}"
    )


def editing_line_edit_style() -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.28)};border-radius:{t.control_radius}px;"
        f"padding:0 8px;color:{t.color_text};}}"
    )


def input_line_edit_style(horizontal_padding: int = 6) -> str:
    t = THEME
    return (
        f"QLineEdit{{background:{hex_to_rgba(t.color_surface_alt, 0.98)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 {horizontal_padding}px;border-radius:{t.input_radius}px;}}"
        f"QLineEdit:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.10)};}}"
        f"QLineEdit:focus{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.28)};border-radius:{t.input_radius}px;"
        f"padding:0 {horizontal_padding}px;}}"
    )


def combo_box_style() -> str:
    t = THEME
    return (
        f"QComboBox{{background:{hex_to_rgba(t.color_surface_alt, 0.98)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 8px;border-radius:{t.input_radius}px;}}"
        f"QComboBox:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.10)};}}"
        f"QComboBox:focus{{background:{hex_to_rgba(t.color_window, 1.0)};border:1px solid {hex_to_rgba(t.color_primary, 0.28)};}}"
    )


def display_field_style(horizontal_padding: int = 10) -> str:
    t = THEME
    return (
        f"QLabel{{background:{hex_to_rgba(t.color_surface, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_text_soft, 0.12)};border-radius:{t.control_radius}px;"
        f"padding:0 {horizontal_padding}px;color:{t.color_text};}}"
    )


def tool_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba(t.color_text_soft, 0.14)};"
        f"border-radius:{t.control_radius}px;background:{hex_to_rgba(t.color_surface, 1.0)};}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_primary, 0.24)};}}"
    )


def unit_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{background:{hex_to_rgba(t.color_surface_alt, 0.98)};border:1px solid transparent;"
        f"color:{t.color_text};padding:0 8px;text-align:left;border-radius:{t.input_radius}px;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_text_soft, 0.10)};}}"
        f"QToolButton:pressed{{background:{hex_to_rgba(t.color_pressed, 1.0)};}}"
        f"QToolButton:focus{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border-color:{hex_to_rgba(t.color_primary, 0.28)};}}"
    )


def menu_style() -> str:
    t = THEME
    return f"""
        QMenu{{background:{t.color_surface};border:1px solid {t.color_border};border-radius:10px;padding:6px;color:{t.color_text};}}
        QMenu::item{{padding:8px 14px;border-radius:8px;}}
        QMenu::item:selected{{background:{hex_to_rgba(t.color_primary, 0.14)};color:{t.color_text};}}
        QMenu::separator{{height:1px;background:{t.color_border_soft};margin:6px 8px;}}
    """


def plain_text_edit_style() -> str:
    t = THEME
    return (
        f"QPlainTextEdit{{background:{hex_to_rgba(t.color_surface_alt, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_text_soft, 0.10)};color:{t.color_text};"
        f"font-size:{t.base_font_px}px;border-radius:{t.editor_radius}px;padding:10px;}}"
        f"QPlainTextEdit:focus{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.24)};}}"
    )


def delete_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:none;border-radius:7px;background:{hex_to_rgba(t.color_text_soft, 0.08)};"
        f"color:{t.color_text_soft};font-weight:700;font-size:{t.delete_button_font_px}px;padding:0px;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_text_soft, 0.14)};}}"
    )


def index_button_style(active: bool) -> str:
    t = THEME
    if active:
        return (
            f"QToolButton{{border:1px solid {hex_to_rgba(t.color_primary, 0.30)};border-radius:{t.control_radius}px;"
            f"background:{hex_to_rgba(t.color_window, 1.0)};color:{t.color_text_soft};font-weight:800;}}"
            f"QToolButton:hover{{background:{hex_to_rgba(t.color_surface, 1.0)};}}"
        )
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba(t.color_text_soft, 0.12)};border-radius:{t.control_radius}px;"
        f"background:{hex_to_rgba(t.color_surface_alt, 1.0)};color:{t.color_text_muted};font-weight:700;}}"
        f"QToolButton:hover{{background:{hex_to_rgba(t.color_surface, 1.0)};}}"
    )


def disabled_index_button_style() -> str:
    t = THEME
    return (
        f"QToolButton{{border:1px solid {hex_to_rgba(t.color_text_soft, 0.08)};border-radius:{t.control_radius}px;"
        f"background:{hex_to_rgba(t.color_surface_muted, 0.86)};color:{hex_to_rgba(t.color_text_muted, 0.48)};font-weight:700;}}"
    )


def table_line_edit_style(prefix: str = "") -> str:
    t = THEME
    return (
        f"{prefix}QLineEdit{{"
        f"background:{t.color_surface_alt};"
        "border:1px solid transparent;"
        "border-radius:8px;"
        "padding:0 6px;"
        f"color:{t.color_text};"
        f"selection-background-color:{t.color_pressed};"
        f"selection-color:{t.color_text};"
        "}"
        f"{prefix}QLineEdit:focus{{"
        f"background:{t.color_window};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.28)};"
        "}"
    )


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
        "padding:8px 10px;"
        "font-weight:600;"
        "}"
        "QTableWidget::item{" 
        "border:1px solid transparent;"
        "padding:4px 6px;"
        "}"
        "QTableWidget::item:selected{" 
        f"background:{t.color_surface_alt};"
        f"color:{t.color_text};"
        f"border:1px solid {t.color_border_soft};"
        "}"
        "}"
        "QTableWidget::item:focus{outline:none;}"
        + table_line_edit_style(prefix="QTableWidget ")
    )


def image_preview_style() -> str:
    t = THEME
    return f"background: transparent; border: none; color: {t.color_placeholder};"


def tooltip_style_override() -> str:
    t = THEME
    return (
        "QToolTip{" 
        f"background-color:{t.color_tooltip_bg};"
        f"color:{t.color_tooltip_text};"
        f"border:1px solid {t.color_tooltip_border};"
        f"border-radius:{t.tooltip_radius}px;"
        f"padding:{t.tooltip_padding_v}px {t.tooltip_padding_h}px;"
        f"font-size:{t.tooltip_font_px}px;"
        "font-weight:600;"
        "min-height:0px;"
        "}"
    )


def icon_button_override(font_px: int) -> str:
    _ = font_px
    return "QPushButton{font-weight:700;padding:0;margin:0;}"
