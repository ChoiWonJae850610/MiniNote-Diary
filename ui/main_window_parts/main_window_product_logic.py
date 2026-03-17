from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

from ui.dialogs import InboundInspectionDialog, show_info, show_warning
from ui.messages import DefaultTexts, DialogTitles, InfoMessages, Warnings
from ui.pages.order_panels import TemplateListCard

if TYPE_CHECKING:
    from ui.main_window import MainWindow


@dataclass
class ProductStats:
    template_id: str
    template_name: str
    sale_price: int = 0
    note: str = ''
    stock_qty: int = 0
    pending_qty: int = 0
    defect_qty: int = 0
    sold_qty: int = 0


class MainWindowProductLogic:
    @staticmethod
    def refresh_product_page(window: "MainWindow") -> None:
        refs = window.product_page_refs
        current_template_id = refs.page.property('selected_template_id') or ''
        refs.product_list.clear()
        stats_map = MainWindowProductLogic._build_stats_map(window)
        for stats in sorted(stats_map.values(), key=lambda row: row.template_name or '', reverse=False):
            item = QListWidgetItem(refs.product_list)
            item.setData(Qt.UserRole, stats.template_id)
            card = TemplateListCard(
                title=stats.template_name or DefaultTexts.EMPTY_VALUE,
                subtitle=f'판매가 {stats.sale_price:,}원' if stats.sale_price else '판매가 미등록',
                meta_lines=[
                    f'재고 {stats.stock_qty} · 미검수 {stats.pending_qty} · 불량 {stats.defect_qty}',
                    f'판매 누계 {stats.sold_qty}',
                ],
            )
            item.setSizeHint(card.sizeHint())
            refs.product_list.addItem(item)
            refs.product_list.setItemWidget(item, card)
        if refs.product_list.count() > 0:
            if current_template_id:
                MainWindowProductLogic._select_template(window, current_template_id)
                if refs.product_list.currentRow() < 0:
                    refs.product_list.setCurrentRow(0)
            else:
                refs.product_list.setCurrentRow(0)
            MainWindowProductLogic._sync_list_selection(refs.product_list)
        else:
            MainWindowProductLogic.clear_product_detail(window)

    @staticmethod
    def on_product_selected(window: "MainWindow", row: int) -> None:
        refs = window.product_page_refs
        MainWindowProductLogic._sync_list_selection(refs.product_list)
        item = refs.product_list.item(row) if row >= 0 else None
        if item is None:
            MainWindowProductLogic.clear_product_detail(window)
            return
        template_id = item.data(Qt.UserRole)
        stats = MainWindowProductLogic._build_stats_map(window).get(template_id)
        if stats is None:
            MainWindowProductLogic.clear_product_detail(window)
            return
        refs.page.setProperty('selected_template_id', template_id)
        refs.lbl_name.setText(stats.template_name or DefaultTexts.EMPTY_VALUE)
        refs.lbl_code.setText(template_id or DefaultTexts.EMPTY_VALUE)
        refs.lbl_stock_qty.setText(str(stats.stock_qty))
        refs.lbl_pending_qty.setText(str(stats.pending_qty))
        refs.lbl_defect_qty.setText(str(stats.defect_qty))
        refs.price_spin.setValue(max(0, int(stats.sale_price or 0)))
        refs.sale_price_spin.setValue(max(0, int(stats.sale_price or 0)))
        refs.product_note_edit.setPlainText(stats.note or '')
        refs.sale_qty_spin.setMaximum(max(0, stats.stock_qty))
        refs.sale_qty_spin.setValue(1 if stats.stock_qty > 0 else 0)
        refs.sale_memo_edit.clear()
        MainWindowProductLogic._populate_pending_list(window, template_id)

    @staticmethod
    def clear_product_detail(window: "MainWindow") -> None:
        refs = window.product_page_refs
        refs.page.setProperty('selected_template_id', '')
        refs.lbl_name.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_code.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_stock_qty.setText('0')
        refs.lbl_pending_qty.setText('0')
        refs.lbl_defect_qty.setText('0')
        refs.price_spin.setValue(0)
        refs.sale_price_spin.setValue(0)
        refs.product_note_edit.clear()
        refs.pending_list.clear()
        refs.sale_qty_spin.setMaximum(0)
        refs.sale_qty_spin.setValue(0)
        refs.sale_memo_edit.clear()
        MainWindowProductLogic._sync_list_selection(refs.product_list)

    @staticmethod
    def save_product(window: "MainWindow") -> None:
        refs = window.product_page_refs
        template_id = refs.page.property('selected_template_id') or ''
        if not template_id:
            show_warning(window, DialogTitles.PRODUCT, Warnings.PRODUCT_SELECT_FIRST)
            return
        template_name = refs.lbl_name.text().strip() or DefaultTexts.EMPTY_VALUE
        window.product_repository.upsert(
            template_id=template_id,
            template_name=template_name,
            sale_price=int(refs.price_spin.value() or 0),
            note=refs.product_note_edit.toPlainText().strip(),
        )
        MainWindowProductLogic.refresh_product_page(window)
        window.refresh_menu_page()
        MainWindowProductLogic._select_template(window, template_id)
        show_info(window, DialogTitles.PRODUCT, InfoMessages.PRODUCT_SAVED)

    @staticmethod
    def apply_pending_inspection(window: "MainWindow") -> None:
        refs = window.product_page_refs
        item = refs.pending_list.currentItem()
        if item is None:
            show_warning(window, DialogTitles.PRODUCT, Warnings.PRODUCT_PENDING_SELECT_FIRST)
            return
        inbound_id = item.data(Qt.UserRole)
        record = next((row for row in window.inbound_repository.load_all() if row.inbound_id == inbound_id), None)
        if record is None:
            show_warning(window, DialogTitles.PRODUCT, Warnings.PRODUCT_PENDING_SELECT_FIRST)
            return
        dialog = InboundInspectionDialog(inbound_qty=int(record.inbound_qty or 0), parent=window)
        if not dialog.exec():
            return
        result = dialog.result_data()
        if result.inspection_exempt:
            show_warning(window, DialogTitles.PRODUCT, '상품관리 화면에서는 검수 예외처리를 다시 지정할 수 없습니다.')
            return
        window.inbound_repository.update_inspection(
            inbound_id=record.inbound_id,
            defect_qty=result.defect_qty,
            good_qty=result.good_qty,
            inspection_memo=result.inspection_memo,
        )
        template_id = refs.page.property('selected_template_id') or ''
        MainWindowProductLogic.refresh_product_page(window)
        window.refresh_menu_page()
        if template_id:
            MainWindowProductLogic._select_template(window, template_id)
        show_info(window, DialogTitles.PRODUCT, InfoMessages.PRODUCT_INSPECTION_APPLIED.format(good_qty=result.good_qty, defect_qty=result.defect_qty))

    @staticmethod
    def register_sale(window: "MainWindow") -> None:
        refs = window.product_page_refs
        template_id = refs.page.property('selected_template_id') or ''
        if not template_id:
            show_warning(window, DialogTitles.PRODUCT, Warnings.PRODUCT_SELECT_FIRST)
            return
        stats = MainWindowProductLogic._build_stats_map(window).get(template_id)
        if stats is None:
            show_warning(window, DialogTitles.PRODUCT, Warnings.PRODUCT_SELECT_FIRST)
            return
        sale_qty = int(refs.sale_qty_spin.value() or 0)
        if sale_qty <= 0 or sale_qty > stats.stock_qty:
            show_warning(window, DialogTitles.PRODUCT, Warnings.PRODUCT_SALE_QTY_INVALID)
            return
        rows = window.order_repository.load_all()
        candidate_indexes = [index for index, row in enumerate(rows) if row.template_id == template_id]
        if not candidate_indexes:
            show_warning(window, DialogTitles.PRODUCT, Warnings.PRODUCT_SELECT_FIRST)
            return
        latest_index = candidate_indexes[-1]
        rows[latest_index].sold_qty = max(0, int(rows[latest_index].sold_qty or 0)) + sale_qty
        window.order_repository.save_all(rows)
        MainWindowProductLogic.refresh_product_page(window)
        window.refresh_menu_page()
        MainWindowProductLogic._select_template(window, template_id)
        show_info(window, DialogTitles.PRODUCT, InfoMessages.PRODUCT_SALE_SAVED.format(sale_qty=sale_qty, stock_qty=max(0, stats.stock_qty - sale_qty)))

    @staticmethod
    def _populate_pending_list(window: "MainWindow", template_id: str) -> None:
        refs = window.product_page_refs
        refs.pending_list.clear()
        for record in window.inbound_repository.pending_records(template_id=template_id):
            item = QListWidgetItem(refs.pending_list)
            item.setData(Qt.UserRole, record.inbound_id)
            card = TemplateListCard(
                title=f'{record.inbound_date or DefaultTexts.EMPTY_VALUE} / {record.inbound_qty}개',
                subtitle=record.factory_name or DefaultTexts.EMPTY_VALUE,
                meta_lines=[
                    f'입고 {record.inbound_qty} · 미검수 대기',
                    record.source_memo or InfoMessages.NO_MEMO,
                ],
            )
            item.setSizeHint(card.sizeHint())
            refs.pending_list.addItem(item)
            refs.pending_list.setItemWidget(item, card)
        if refs.pending_list.count() > 0:
            refs.pending_list.setCurrentRow(0)

    @staticmethod
    def _build_stats_map(window: "MainWindow") -> dict[str, ProductStats]:
        result: dict[str, ProductStats] = {}
        orders = window.order_repository.load_all()
        product_rows = {row.template_id: row for row in window.product_repository.load_all()}
        for row in orders:
            stats = result.setdefault(
                row.template_id,
                ProductStats(
                    template_id=row.template_id,
                    template_name=row.template_name or DefaultTexts.EMPTY_VALUE,
                    sale_price=max(0, int((product_rows.get(row.template_id).sale_price if product_rows.get(row.template_id) else 0) or 0)),
                    note=(product_rows.get(row.template_id).note if product_rows.get(row.template_id) else ''),
                ),
            )
            stats.sold_qty += max(0, int(row.sold_qty or 0))
            if not stats.template_name and row.template_name:
                stats.template_name = row.template_name

        for record in window.inbound_repository.load_all():
            stats = result.setdefault(
                record.template_id,
                ProductStats(
                    template_id=record.template_id,
                    template_name=record.template_name or DefaultTexts.EMPTY_VALUE,
                    sale_price=max(0, int((product_rows.get(record.template_id).sale_price if product_rows.get(record.template_id) else 0) or 0)),
                    note=(product_rows.get(record.template_id).note if product_rows.get(record.template_id) else ''),
                ),
            )
            if (record.inspection_status or 'completed') == 'pending':
                stats.pending_qty += max(0, int(record.inbound_qty or 0))
            else:
                stats.stock_qty += max(0, int(record.good_qty or 0))
                stats.defect_qty += max(0, int(record.defect_qty or 0))

        for template_id, product_row in product_rows.items():
            stats = result.setdefault(
                template_id,
                ProductStats(
                    template_id=template_id,
                    template_name=product_row.template_name or DefaultTexts.EMPTY_VALUE,
                    sale_price=max(0, int(product_row.sale_price or 0)),
                    note=product_row.note or '',
                ),
            )
            stats.sale_price = max(0, int(product_row.sale_price or 0))
            stats.note = product_row.note or ''
        for stats in result.values():
            stats.stock_qty = max(0, stats.stock_qty - stats.sold_qty)
        return result

    @staticmethod
    def _select_template(window: "MainWindow", template_id: str) -> None:
        product_list = window.product_page_refs.product_list
        for row in range(product_list.count()):
            item = product_list.item(row)
            if item.data(Qt.UserRole) == template_id:
                product_list.setCurrentRow(row)
                MainWindowProductLogic.on_product_selected(window, row)
                return

    @staticmethod
    def _sync_list_selection(product_list) -> None:
        current_row = product_list.currentRow()
        for row in range(product_list.count()):
            item = product_list.item(row)
            card = product_list.itemWidget(item)
            if hasattr(card, 'set_selected'):
                card.set_selected(row == current_row)
