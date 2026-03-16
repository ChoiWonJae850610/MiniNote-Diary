from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QListWidgetItem

from ui.dialogs import InboundInspectionDialog, show_info, show_warning
from ui.messages import Buttons, DefaultTexts, DialogTitles, InfoMessages, Warnings
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
            completed_qty = max(0, int(order.completed_qty or 0))
            ordered_qty = max(0, int(order.ordered_qty or 0))
            remaining_qty = max(0, ordered_qty - completed_qty)
            status_code = MainWindowInboundLogic._status_code(completed_qty=completed_qty, ordered_qty=ordered_qty)
            if status_code == 'completed':
                continue
            status_text = MainWindowInboundLogic._display_status(order.status, completed_qty=completed_qty, ordered_qty=ordered_qty)
            meta_lines = [
                f"상태 {status_text}",
                f"의뢰 {ordered_qty} · 입고 {completed_qty} · 잔여 {remaining_qty}",
                f"의뢰일 {order.ordered_at or DefaultTexts.EMPTY_VALUE}",
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
        completed_qty = max(0, int(order.completed_qty or 0))
        refs.lbl_completed_qty.setText(str(completed_qty))
        remaining_qty = max(0, int(order.ordered_qty or 0) - completed_qty)
        refs.lbl_remaining_qty.setText(str(remaining_qty))
        refs.lbl_status.setText(MainWindowInboundLogic._display_status(order.status, completed_qty=completed_qty, ordered_qty=int(order.ordered_qty or 0)))
        refs.lbl_lead_days.setText(MainWindowInboundLogic._lead_days_text(order.ordered_at))
        refs.order_memo_view.setPlainText((order.memo or '').strip() or InfoMessages.NO_MEMO)
        refs.inbound_qty_spin.setMaximum(max(0, remaining_qty))
        refs.inbound_qty_spin.setValue(remaining_qty if remaining_qty > 0 else 0)
        refs.inbound_memo_edit.clear()
        refs.inbound_date_edit.setDate(QDate.currentDate())
        refs.btn_toggle_memo.setChecked(False)
        refs.btn_toggle_memo.setText('메모 보기 ▾')
        refs.order_memo_view.hide()
        try:
            if detail is not None and detail.summary.image_path:
                refs.image_preview.set_image(detail.summary.image_path)
            else:
                refs.image_preview.clear_image()
        except Exception:
            refs.image_preview.clear_image()

    @staticmethod
    def toggle_order_memo(window: "MainWindow", checked: bool) -> None:
        refs = window.inbound_page_refs
        refs.order_memo_view.setVisible(bool(checked))
        refs.btn_toggle_memo.setText('메모 접기 ▴' if checked else '메모 보기 ▾')

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
        refs.btn_toggle_memo.setChecked(False)
        refs.btn_toggle_memo.setText('메모 보기 ▾')
        refs.order_memo_view.hide()
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
            show_warning(window, DialogTitles.INBOUND, Warnings.INBOUND_SELECT_ORDER_FIRST)
            return
        order = next((row for row in window.order_repository.list_orders() if row.order_id == order_id), None)
        if order is None:
            show_warning(window, DialogTitles.INBOUND, Warnings.INBOUND_SELECT_ORDER_FIRST)
            return
        inbound_qty = int(refs.inbound_qty_spin.value() or 0)
        remaining_qty = max(0, int(order.ordered_qty or 0) - int(order.completed_qty or 0))
        if inbound_qty <= 0 or inbound_qty > remaining_qty:
            show_warning(window, DialogTitles.INBOUND, Warnings.INBOUND_QTY_INVALID)
            return

        dialog = InboundInspectionDialog(inbound_qty=inbound_qty, parent=window)
        if not dialog.exec():
            return
        result = dialog.result_data()

        inbound_date = refs.inbound_date_edit.date().toString('yyyy-MM-dd')
        updated_inbound_qty = max(0, int(order.completed_qty or 0)) + inbound_qty
        updated_status = MainWindowInboundLogic._status_code(completed_qty=updated_inbound_qty, ordered_qty=int(order.ordered_qty or 0))

        orders = window.order_repository.load_all()
        for index, row in enumerate(orders):
            if row.order_id != order.order_id:
                continue
            row.completed_qty = updated_inbound_qty
            row.status = updated_status
            orders[index] = row
            break
        window.order_repository.save_all(orders)

        window.inbound_repository.create_record(
            order_id=order.order_id,
            template_id=order.template_id,
            template_name=order.template_name,
            factory_name=order.factory_name,
            inbound_date=inbound_date,
            inbound_qty=inbound_qty,
            defect_qty=result.defect_qty,
            good_qty=result.good_qty,
            inspection_memo=result.inspection_memo,
            source_memo=refs.inbound_memo_edit.toPlainText().strip(),
            lead_days=MainWindowInboundLogic._lead_days_value(order.ordered_at, inbound_date=inbound_date),
        )

        MainWindowInboundLogic.refresh_inbound_page(window)
        if updated_status != 'completed':
            MainWindowInboundLogic._select_order(window, order.order_id)
        show_info(
            window,
            DialogTitles.INBOUND,
            InfoMessages.INBOUND_APPLIED.format(
                good_qty=result.good_qty,
                defect_qty=result.defect_qty,
                remaining_qty=max(0, int(order.ordered_qty or 0) - updated_inbound_qty),
            ),
        )

    @staticmethod
    def _select_order(window: "MainWindow", order_id: str) -> None:
        order_list = window.inbound_page_refs.order_list
        for row in range(order_list.count()):
            item = order_list.item(row)
            if item.data(Qt.UserRole) == order_id:
                order_list.setCurrentRow(row)
                MainWindowInboundLogic.on_inbound_order_selected(window, row)
                return

    @staticmethod
    def _sync_list_selection(order_list) -> None:
        current_row = order_list.currentRow()
        for row in range(order_list.count()):
            item = order_list.item(row)
            card = order_list.itemWidget(item)
            if hasattr(card, 'set_selected'):
                card.set_selected(row == current_row)

    @staticmethod
    def _display_status(status: str, *, completed_qty: int = 0, ordered_qty: int = 0) -> str:
        status_code = (status or '').strip()
        if status_code not in {'ordered', 'in_progress', 'partial_completed', 'completed'}:
            status_code = MainWindowInboundLogic._status_code(completed_qty=completed_qty, ordered_qty=ordered_qty)
        mapping = {
            'ordered': '미입고',
            'in_progress': '부분입고',
            'partial_completed': '부분입고',
            'completed': '완료',
        }
        return mapping.get(status_code, DefaultTexts.EMPTY_VALUE)

    @staticmethod
    def _status_code(*, completed_qty: int, ordered_qty: int) -> str:
        if completed_qty <= 0:
            return 'ordered'
        if completed_qty < max(0, ordered_qty):
            return 'partial_completed'
        return 'completed'

    @staticmethod
    def _lead_days_text(ordered_at: str) -> str:
        days = MainWindowInboundLogic._lead_days_value(ordered_at)
        if days is None:
            return DefaultTexts.EMPTY_VALUE
        return f"{days}일"

    @staticmethod
    def _lead_days_value(ordered_at: str, *, inbound_date: str | None = None) -> int | None:
        try:
            ordered = datetime.strptime(ordered_at, '%Y-%m-%d').date()
        except Exception:
            return None
        try:
            end_date = datetime.strptime(inbound_date, '%Y-%m-%d').date() if inbound_date else date.today()
        except Exception:
            end_date = date.today()
        return max(0, (end_date - ordered).days)
