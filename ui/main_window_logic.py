from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QListWidgetItem, QWidget

from services.field_keys import MaterialTargets
from services.search_utils import matches_keyword
from ui.dialogs import show_error, show_info
from ui.order_page import TemplateListCard
from ui.messages import Buttons, DefaultTexts, DialogTitles, FileDialogFilters, InfoMessages, Labels, Warnings

if TYPE_CHECKING:
    from ui.main_window import MainWindow


MATERIAL_TARGET_CONFIGS = {
    MaterialTargets.FABRIC: ('fabric_deleted', 'fabric_item_changed', 'fabric_item_added', 'fabric'),
    MaterialTargets.TRIM: ('trim_deleted', 'trim_item_changed', 'trim_item_added', 'trim'),
    MaterialTargets.DYEING: ('dyeing_deleted', 'dyeing_item_changed', 'dyeing_item_added', 'dyeing'),
    MaterialTargets.FINISHING: ('finishing_deleted', 'finishing_item_changed', 'finishing_item_added', 'finishing'),
    MaterialTargets.OTHER: ('other_deleted', 'other_item_changed', 'other_item_added', 'other'),
}

MATERIAL_STACK_NAMES = {target: stack_name for target, (_, _, _, stack_name) in MATERIAL_TARGET_CONFIGS.items()}


class MainWindowEventBinder:
    @staticmethod
    def bind(window: "MainWindow") -> None:
        MainWindowEventBinder._bind_menu(window)
        MainWindowEventBinder._bind_feature_pages(window)
        MainWindowEventBinder._bind_order_page(window)
        MainWindowEventBinder._bind_work_order(window)

    @staticmethod
    def _bind_menu(window: "MainWindow") -> None:
        window.btn_template.clicked.connect(window.go_work_order)
        window.btn_job_start_menu.clicked.connect(window.open_order_page)
        window.btn_receipt_menu.clicked.connect(lambda: window.open_feature_page(window.PAGE_RECEIPT))
        window.btn_complete_menu.clicked.connect(lambda: window.open_feature_page(window.PAGE_COMPLETE))
        window.btn_sale_menu.clicked.connect(lambda: window.open_feature_page(window.PAGE_SALE))
        window.btn_inventory_menu.clicked.connect(lambda: window.open_feature_page(window.PAGE_INVENTORY))
        window.btn_partner_mgmt.clicked.connect(window.on_partner_mgmt_clicked)
        window.btn_unit_mgmt.clicked.connect(window.on_unit_mgmt_clicked)

    @staticmethod
    def _bind_feature_pages(window: "MainWindow") -> None:
        for refs in window.feature_pages.values():
            refs.btn_back.clicked.connect(window.go_menu)
            refs.btn_primary.clicked.connect(lambda _=False, page=refs.page: window.on_feature_primary(page))
            refs.btn_secondary.clicked.connect(lambda _=False, page=refs.page: window.on_feature_secondary(page))

    @staticmethod
    def _bind_order_page(window: "MainWindow") -> None:
        refs = window.order_page_refs
        refs.btn_back.clicked.connect(window.go_menu)
        refs.btn_reload.clicked.connect(window.refresh_order_page)
        refs.btn_order.clicked.connect(window.on_order_create_clicked)
        refs.search_edit.textChanged.connect(window.refresh_order_page)
        refs.month_combo.currentIndexChanged.connect(window.refresh_order_page)
        refs.template_list.currentRowChanged.connect(window.on_order_template_selected)

    @staticmethod
    def _bind_work_order(window: "MainWindow") -> None:
        window.btn_back.clicked.connect(window.on_back_clicked)
        window.btn_reset.clicked.connect(window.on_reset_clicked)
        window.btn_save.clicked.connect(window.on_save_clicked)
        window.btn_upload.clicked.connect(window.upload_image)
        window.btn_delete_image.clicked.connect(window.delete_image)

        window.change_note_postit.text_changed.connect(window.on_change_note_changed)
        bar = window.postit_bar
        for target, (deleted_signal, changed_signal, added_signal, _) in MATERIAL_TARGET_CONFIGS.items():
            getattr(bar, deleted_signal).connect(lambda idx, material_target=target: window.on_material_deleted(material_target, idx))
            getattr(bar, changed_signal).connect(lambda idx, patch, material_target=target: window.on_material_changed(material_target, idx, patch))
            getattr(bar, added_signal).connect(lambda material_target=target: window.on_add_material_clicked(material_target))
        bar.basic_data_changed.connect(window.on_basic_postit_changed)


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
                f"자재: 원단 {summary.fabric_count} / 부자재 {summary.trim_count}",
                f"재고 {getattr(stats, 'current_stock_qty', 0)} · 진행중 {getattr(stats, 'in_progress_qty', 0)}",
                f"최근 발주 {getattr(stats, 'last_ordered_at', '') or InfoMessages.NONE}",
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
        refs.lbl_material_summary.setText(f"원단 {summary.fabric_count} / 부자재 {summary.trim_count}")
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


class MainWindowFeatureLogic:
    PRIMARY_MESSAGE_BY_PAGE = {
        'page_partner': (DialogTitles.PARTNER_MANAGE, InfoMessages.FEATURE_PARTNER_PENDING),
        'page_inventory': (DialogTitles.INVENTORY, InfoMessages.FEATURE_INVENTORY_PENDING),
    }
    SECONDARY_MESSAGE_BY_PAGE = {
        'page_receipt': (DialogTitles.RECEIPT, InfoMessages.FEATURE_RECEIPT_EXTEND),
    }

    @staticmethod
    def show_primary(window: "MainWindow", page: QWidget) -> None:
        title, message = MainWindowFeatureLogic.PRIMARY_MESSAGE_BY_PAGE.get(
            MainWindowFeatureLogic._page_name(window, page),
            (DialogTitles.COMING_SOON, InfoMessages.FEATURE_GENERIC_PENDING),
        )
        show_info(window, title, message)

    @staticmethod
    def show_secondary(window: "MainWindow", page: QWidget) -> None:
        title, message = MainWindowFeatureLogic.SECONDARY_MESSAGE_BY_PAGE.get(
            MainWindowFeatureLogic._page_name(window, page),
            (DialogTitles.SCREEN_REVIEW, InfoMessages.FEATURE_SCREEN_REVIEW),
        )
        show_info(window, title, message)

    @staticmethod
    def _page_name(window: "MainWindow", page: QWidget) -> str:
        for name, current_page in window.pages.items():
            if current_page is page:
                return name
        return ''


class MainWindowWorkOrderLogic:
    @staticmethod
    def reset_form(window: "MainWindow") -> None:
        window._suppress_dirty = True
        try:
            window.state.reset()
            window.image_preview.clear_image()
            window.btn_delete_image.setEnabled(False)
            MainWindowWorkOrderLogic.refresh_postits(window, force_rebuild=True)
            window._clear_feedback()
            window._update_window_title()
        finally:
            window._suppress_dirty = False

    @staticmethod
    def refresh_postits(window: "MainWindow", *, force_rebuild: bool = False) -> None:
        window.postit_bar.set_data(
            header=window.state.header_data,
            fabrics=window.state.fabric_items,
            trims=window.state.trim_items,
            dyeings=window.state.dyeing_items,
            finishings=window.state.finishing_items,
            others=window.state.other_items,
            force_rebuild=force_rebuild,
        )
        window.change_note_postit.set_text(window.state.header.change_note)

    @staticmethod
    def refresh_basic_postit(window: "MainWindow") -> None:
        window.postit_bar.basic.set_header_data(window.state.header_data)

    @staticmethod
    def remove_material(window: "MainWindow", target: str, idx: int) -> None:
        if window.state.remove_material_item(target, idx):
            MainWindowWorkOrderLogic.refresh_postits(window, force_rebuild=True)
            window._update_window_title()

    @staticmethod
    def update_material(window: "MainWindow", target: str, idx: int, patch: dict) -> None:
        window.state.update_material_patch(target, idx, patch)
        MainWindowWorkOrderLogic.refresh_basic_postit(window)
        window._update_window_title()

    @staticmethod
    def add_material(window: "MainWindow", target: str) -> None:
        new_index = window.state.add_material_item(target)
        if new_index is None:
            return
        MainWindowWorkOrderLogic.refresh_postits(window, force_rebuild=True)
        getattr(window.postit_bar, MATERIAL_STACK_NAMES[target]).set_active_card(new_index)
        window._update_window_title()

    @staticmethod
    def upload_image(window: "MainWindow") -> None:
        path, _ = QFileDialog.getOpenFileName(window, DialogTitles.IMAGE_SELECT, '', FileDialogFilters.IMAGES)
        if not path:
            return
        try:
            window.image_preview.set_image(path)
            window.state.current_image_path = path
            window.btn_delete_image.setEnabled(True)
            window.mark_dirty()
            window._show_feedback(InfoMessages.IMAGE_ATTACHED)
        except Exception as exc:
            show_error(window, DialogTitles.ERROR, str(exc))

    @staticmethod
    def delete_image(window: "MainWindow") -> None:
        window.image_preview.clear_image()
        window.state.current_image_path = None
        window.btn_delete_image.setEnabled(False)
        window.mark_dirty()
        window._show_feedback(InfoMessages.IMAGE_REMOVED)
