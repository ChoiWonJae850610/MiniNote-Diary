from __future__ import annotations

from PySide6.QtCore import QDate, QSignalBlocker


def recompute_basic_prices(card) -> None:
    material_total = int(card.cost.digits() or "0")
    labor = int(card.labor.digits() or "0")
    loss = int(card.loss.digits() or "0")
    sale_total = material_total + labor + loss
    card._syncing_prices = True
    try:
        card.sale_price.setText(f"{sale_total:,}")
    finally:
        card._syncing_prices = False


def on_price_component_changed(card, _text: str) -> None:
    recompute_basic_prices(card)
    card._emit_price_fields()


def on_sale_price_changed(card, _text: str) -> None:
    if card._syncing_prices:
        return
    card._emit_price_fields()


def set_basic_header_data(card, header: dict) -> None:
    header = header or {}
    date = QDate.fromString(header.get("date", ""), "yyyy-MM-dd")
    if not date.isValid():
        date = QDate.currentDate()
    card._date_value = date
    card.date_text.setText(date.toString("yyyy-MM-dd"))
    blockers = [
        QSignalBlocker(card.style_no),
        QSignalBlocker(card.factory),
        QSignalBlocker(card.cost),
        QSignalBlocker(card.labor),
        QSignalBlocker(card.loss),
        QSignalBlocker(card.sale_price),
    ]
    try:
        card.style_no.set_text_silent(header.get("style_no", ""))
        card.factory.set_text_silent(header.get("factory", ""))
        card.factory.setProperty("factory_partner_id", header.get("factory_partner_id", ""))
        card._adjust_style_width(card.style_no.text())
        card.cost.setText(header.get("cost_display", header.get("cost", "0")) or "0")
        card.labor.setText(header.get("labor_display", header.get("labor", "0")) or "0")
        card.loss.setText(header.get("loss_display", header.get("loss", "0")) or "0")
        card.sale_price.setText(header.get("sale_price_display", header.get("sale_price", "0")) or "0")
    finally:
        del blockers
