from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

from services.common.search_utils import matches_keyword
from ui.dialogs import show_error, show_info
from ui.pages.order_page import TemplateListCard
from ui.messages import DefaultTexts, DialogTitles, HelperTexts, InfoMessages, Labels, Warnings

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowOrderLogic:
    @staticmethod
    def refresh_order_page(window: "MainWindow") -> None:
        refs = window.order_page_refs
        summaries = window.controller.repository.list_template_summaries()
        month_combo = refs.month_combo
        selected_month = month_combo.currentData() if month_combo.count() else Labels.ALL_MONTHS
        months = sorted({summary.date[:7] for summary in summaries if summary.date[:7]}, reverse=True)
        month_combo.blockSignals(True)
        month_combo.clear()
        month_combo.addItem(Labels.ALL_MONTHS, Labels.ALL_MONTHS)
        for month in months:
            month_combo.addItem(month, month)
        restore_index = month_combo.findData(selected_month)
        if restore_index >= 0:
            month_combo.setCurrentIndex(restore_index)
        month_combo.blockSignals(False)

        keyword = refs.search_edit.text().strip()
        month_filter = month_combo.currentData() or Labels.ALL_MONTHS
        stats_map = window.order_repository.aggregate_by_template()
        refs.template_list.clear()
        for summary in summaries:
            if month_filter != Labels.ALL_MONTHS and not str(summary.date or '').startswith(str(month_filter)):
                continue
            if not matches_keyword(keyword, summary.name, summary.factory_name, summary.change_note):
                continue
            stats = stats_map.get(summary.template_id)
            subtitle = f"{summary.factory_name or InfoMessages.NO_FACTORY} · 기준일 {summary.date or DefaultTexts.EMPTY_VALUE}"
            meta_lines = [
                HelperTexts.ORDER_TEMPLATE_META_MATERIAL.format(fabric=summary.fabric_count, trim=summary.trim_count),
                HelperTexts.ORDER_TEMPLATE_META_STOCK.format(stock=getattr(stats, 'current_stock_qty', 0), in_progress=getattr(stats, 'in_progress_qty', 0)),
                HelperTexts.ORDER_TEMPLATE_META_LAST_ORDER.format(last_order=getattr(stats, 'last_ordered_at', '') or InfoMessages.NONE),
            ]
            item = QListWidgetItem(refs.template_list)
            item.setData(Qt.UserRole, summary.template_id)
            card = TemplateListCard(title=summary.name, subtitle=subtitle, meta_lines=meta_lines)
            item.setSizeHint(card.sizeHint())
            refs.template_list.addItem(item)
            refs.template_list.setItemWidget(item, card)

        if refs.template_list.count() > 0:
            refs.template_list.setCurrentRow(0)
        else:
            MainWindowOrderLogic.clear_order_template_detail(window)

    @staticmethod
    def on_order_template_selected(window: "MainWindow", row: int) -> None:
        refs = window.order_page_refs
        item = refs.template_list.item(row) if row >= 0 else None
        if item is None:
            MainWindowOrderLogic.clear_order_template_detail(window)
            return
        template_id = item.data(Qt.UserRole)
        detail = window.controller.repository.load_template_detail(template_id)
        if detail is None:
            MainWindowOrderLogic.clear_order_template_detail(window)
            return
        stats = window.order_repository.aggregate_for_template(template_id)
        summary = detail.summary
        refs.page.setProperty('selected_template_id', template_id)
        refs.lbl_name.setText(summary.name or DefaultTexts.EMPTY_VALUE)
        refs.lbl_factory.setText(summary.factory_name or DefaultTexts.EMPTY_VALUE)
        refs.lbl_date.setText(summary.date or DefaultTexts.EMPTY_VALUE)
        refs.lbl_cost.setText(summary.cost_display or DefaultTexts.EMPTY_VALUE)
        refs.lbl_labor.setText(summary.labor_display or DefaultTexts.EMPTY_VALUE)
        refs.lbl_sale_price.setText(summary.sale_price_display or DefaultTexts.EMPTY_VALUE)
        refs.lbl_material_summary.setText(HelperTexts.ORDER_DETAIL_MATERIAL_SUMMARY.format(fabric=summary.fabric_count, trim=summary.trim_count))
        refs.lbl_last_order.setText(stats.last_ordered_at or InfoMessages.NO_ORDER_HISTORY)
        refs.lbl_total_ordered.setText(str(stats.total_ordered_qty))
        refs.lbl_in_progress.setText(str(stats.in_progress_qty))
        refs.lbl_current_stock.setText(str(stats.current_stock_qty))
        refs.memo_view.setPlainText(summary.change_note or InfoMessages.NO_MEMO)
        refs.order_qty_spin.setValue(max(1, refs.order_qty_spin.value()))
        refs.order_memo_edit.clear()
        try:
            if summary.image_path:
                refs.image_preview.set_image(summary.image_path)
            else:
                refs.image_preview.clear_image()
        except Exception:
            refs.image_preview.clear_image()

    @staticmethod
    def clear_order_template_detail(window: "MainWindow") -> None:
        refs = window.order_page_refs
        refs.page.setProperty('selected_template_id', '')
        refs.lbl_name.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_factory.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_date.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_cost.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_labor.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_sale_price.setText(DefaultTexts.EMPTY_VALUE)
        refs.lbl_material_summary.setText(DefaultTexts.ORDER_MATERIAL_SUMMARY_EMPTY)
        refs.lbl_last_order.setText(InfoMessages.NO_ORDER_HISTORY)
        refs.lbl_total_ordered.setText('0')
        refs.lbl_in_progress.setText('0')
        refs.lbl_current_stock.setText('0')
        refs.memo_view.clear()
        refs.image_preview.clear_image()

    @staticmethod
    def on_order_create_clicked(window: "MainWindow") -> None:
        refs = window.order_page_refs
        template_id = refs.page.property('selected_template_id') or ''
        if not template_id:
            show_info(window, DialogTitles.ORDER, Warnings.ORDER_SELECT_TEMPLATE_FIRST)
            return
        detail = window.controller.repository.load_template_detail(template_id)
        if detail is None:
            show_error(window, DialogTitles.SAVE_FAILED, Warnings.ORDER_TEMPLATE_LOAD_FAILED)
            return
        qty = max(1, refs.order_qty_spin.value())
        ordered_at = refs.order_date_edit.date().toString('yyyy-MM-dd')
        memo = refs.order_memo_edit.toPlainText().strip()
        window.order_repository.create_order(
            template_id=template_id,
            template_name=detail.summary.name,
            factory_name=detail.summary.factory_name,
            ordered_qty=qty,
            ordered_at=ordered_at,
            memo=memo,
        )
        MainWindowOrderLogic.refresh_order_page(window)
        message = DefaultTexts.ORDER_SAVE_SUCCESS_MESSAGE.format(name=detail.summary.name, qty=qty, ordered_at=ordered_at)
        show_info(window, DefaultTexts.ORDER_SAVE_SUCCESS, message)
