from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QListWidgetItem

from ui.dialogs import show_info
from ui.messages import DefaultTexts, DialogTitles, InfoMessages, Warnings
from ui.pages.inbound_page import TemplateListCard

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowInboundLogic:
    @staticmethod
    def refresh_inbound_page(window: "MainWindow") -> None:
        refs = window.inbound_page_refs
        refs.order_list.clear()
        orders = sorted(window.order_repository.list_orders(), key=lambda row: ((row.ordered_at or ''), (row.created_at or ''), row.order_id), reverse=True)
        for order in orders:
            remaining_qty = max(0, int(order.ordered_qty or 0) - int(order.completed_qty or 0))
            meta_lines = [
                f"발주일 {order.ordered_at or DefaultTexts.EMPTY_VALUE} · 발주 {int(order.ordered_qty or 0)}",
                f"완료 {int(order.completed_qty or 0)} · 잔여 {remaining_qty}",
                f"상태 {MainWindowInboundLogic._display_status(order.status)}",
            ]
            item = QListWidgetItem(refs.order_list)
            item.setData(Qt.UserRole, order.order_id)
            card = TemplateListCard(
                title=order.template_name or DefaultTexts.EMPTY_VALUE,
                subtitle=f"{order.factory_name or InfoMessages.NO_FACTORY}",
                meta_lines=meta_lines,
            )
            item.setSizeHint(card.sizeHint())
            refs.order_list.addItem(item)
            refs.order_list.setItemWidget(item, card)
        if refs.order_list.count() > 0:
            refs.order_list.setCurrentRow(0)
            MainWindowInboundLogic._sync_list_selection(refs.order_list)
        else:
            MainWindowInboundLogic.clear_inbound_detail(window)

    @staticmethod
    def on_inbound_order_selected(window: "MainWindow", row: int) -> None:
        refs = window.inbound_page_refs
        MainWindowInboundLogic._sync_list_selection(refs.order_list)
        item = refs.order_list.item(row) if row >= 0 else None
        if item is None:
            MainWindowInboundLogic.clear_inbound_detail(window)
            return
        order_id = item.data(Qt.UserRole)
        order = next((row for row in window.order_repository.list_orders() if row.order_id == order_id), None)
        if order is None:
            MainWindowInboundLogic.clear_inbound_detail(window)
            return
        detail = window.controller.repository.load_template_detail(order.template_id)
        refs.page.setProperty('selected_order_id', order.order_id)
        refs.lbl_name.setText(order.template_name or DefaultTexts.EMPTY_VALUE)
        refs.lbl_factory.setText(order.factory_name or DefaultTexts.EMPTY_VALUE)
        refs.lbl_order_date.setText(order.ordered_at or DefaultTexts.EMPTY_VALUE)
        refs.lbl_order_qty.setText(str(int(order.ordered_qty or 0)))
        refs.lbl_completed_qty.setText(str(int(order.completed_qty or 0)))
        remaining_qty = max(0, int(order.ordered_qty or 0) - int(order.completed_qty or 0))
        refs.lbl_remaining_qty.setText(str(remaining_qty))
        refs.lbl_status.setText(MainWindowInboundLogic._display_status(order.status))
        refs.lbl_lead_days.setText(MainWindowInboundLogic._lead_days_text(order.ordered_at))
        refs.order_memo_view.setPlainText((order.memo or '').strip() or InfoMessages.NO_MEMO)
        refs.inbound_qty_spin.setMaximum(max(0, remaining_qty))
        refs.inbound_qty_spin.setValue(remaining_qty)
        refs.inbound_memo_edit.clear()
        refs.inbound_date_edit.setDate(QDate.currentDate())
        try:
            if detail is not None and detail.summary.image_path:
                refs.image_preview.set_image(detail.summary.image_path)
            else:
                refs.image_preview.clear_image()
        except Exception:
            refs.image_preview.clear_image()

    @staticmethod
    def clear_inbound_detail(window: "MainWindow") -> None:
        refs = window.inbound_page_refs
        refs.page.setProperty('selected_order_id', '')
        refs.lbl_name.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_factory.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_order_date.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_order_qty.setText('0')
        refs.lbl_completed_qty.setText('0')
        refs.lbl_remaining_qty.setText('0')
        refs.lbl_status.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_lead_days.setText(DefaultTexts.EMPTY_VALUE)
        refs.order_memo_view.clear()
        refs.image_preview.clear_image()
        refs.inbound_qty_spin.setMaximum(0)
        refs.inbound_qty_spin.setValue(0)
        refs.inbound_memo_edit.clear()
        MainWindowInboundLogic._sync_list_selection(refs.order_list)

    @staticmethod
    def show_apply_preview(window: "MainWindow") -> None:
        refs = window.inbound_page_refs
        order_id = refs.page.property('selected_order_id') or ''
        if not order_id:
            show_info(window, DialogTitles.INBOUND, Warnings.INBOUND_SELECT_ORDER_FIRST)
            return
        show_info(window, DialogTitles.INBOUND, InfoMessages.INBOUND_PENDING)

    @staticmethod
    def _sync_list_selection(order_list) -> None:
        current_row = order_list.currentRow()
        for row in range(order_list.count()):
            item = order_list.item(row)
            card = order_list.itemWidget(item)
            if hasattr(card, 'set_selected'):
                card.set_selected(row == current_row)

    @staticmethod
    def _display_status(status: str) -> str:
        mapping = {
            'ordered': '발주 완료',
            'in_progress': '진행중',
            'partial_completed': '부분 입고',
            'completed': '입고 완료',
        }
        return mapping.get((status or '').strip(), DefaultTexts.EMPTY_VALUE)

    @staticmethod
    def _lead_days_text(ordered_at: str) -> str:
        try:
            ordered = datetime.strptime(ordered_at, '%Y-%m-%d').date()
        except Exception:
            return DefaultTexts.EMPTY_VALUE
        return f"{max(0, (date.today() - ordered).days)}일"
