from __future__ import annotations

from ui.theme_tokens import THEME, hex_to_rgba


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


def plain_text_edit_style() -> str:
    t = THEME
    return (
        f"QPlainTextEdit{{background:{hex_to_rgba(t.color_surface_alt, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_text_soft, 0.10)};color:{t.color_text};"
        f"font-size:{t.base_font_px}px;border-radius:{t.editor_radius}px;padding:10px;}}"
        f"QPlainTextEdit:focus{{background:{hex_to_rgba(t.color_window, 1.0)};"
        f"border:1px solid {hex_to_rgba(t.color_primary, 0.24)};}}"
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
