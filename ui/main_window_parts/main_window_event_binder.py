from __future__ import annotations

from typing import TYPE_CHECKING

from ui.main_window_parts.main_window_work_order_logic import MATERIAL_TARGET_CONFIGS

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowEventBinder:
    @staticmethod
    def bind(window: "MainWindow") -> None:
        MainWindowEventBinder._bind_menu(window)
        MainWindowEventBinder._bind_feature_pages(window)
        MainWindowEventBinder._bind_order_page(window)
        MainWindowEventBinder._bind_inbound_page(window)
        MainWindowEventBinder._bind_product_page(window)
        MainWindowEventBinder._bind_work_order(window)
        MainWindowEventBinder._bind_stats_page(window)

    @staticmethod
    def _bind_menu(window: "MainWindow") -> None:
        window.btn_template.clicked.connect(window.go_work_order)
        window.btn_job_start_menu.clicked.connect(window.open_order_page)
        window.btn_receipt_menu.clicked.connect(lambda: window.open_feature_page(window.PAGE_RECEIPT))
        window.btn_complete_menu.clicked.connect(window.on_partner_mgmt_clicked)
        window.btn_sale_menu.clicked.connect(window.on_unit_mgmt_clicked)
        window.btn_inventory_menu.clicked.connect(window.on_product_type_mgmt_clicked)
        window.btn_settings.clicked.connect(window.on_settings_clicked)

    @staticmethod
    def _bind_feature_pages(window: "MainWindow") -> None:
        for refs in window.feature_pages.values():
            refs.btn_back.clicked.connect(window.go_menu)
            refs.btn_primary.clicked.connect(lambda _=False, page=refs.page: window.on_feature_primary(page))
            refs.btn_secondary.clicked.connect(lambda _=False, page=refs.page: window.on_feature_secondary(page))

    @staticmethod
    def _bind_stats_page(window: "MainWindow") -> None:
        refs = window.stats_page_refs
        refs.btn_back.clicked.connect(window.go_menu)
        refs.btn_refresh.clicked.connect(window.refresh_stats_page)
        refs.period_combo.currentIndexChanged.connect(lambda _index: window.refresh_stats_page())

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
    def _bind_inbound_page(window: "MainWindow") -> None:
        refs = window.inbound_page_refs
        refs.btn_back.clicked.connect(window.go_menu)
        refs.btn_reload.clicked.connect(window.refresh_inbound_page)
        refs.status_filter_combo.currentIndexChanged.connect(window.refresh_inbound_page)
        refs.order_list.currentRowChanged.connect(window.on_inbound_order_selected)
        refs.btn_toggle_memo.toggled.connect(window.on_inbound_memo_toggled)
        refs.btn_apply.clicked.connect(window.on_inbound_apply_clicked)


    @staticmethod
    def _bind_product_page(window: "MainWindow") -> None:
        refs = window.product_page_refs
        refs.btn_back.clicked.connect(window.go_menu)
        refs.product_list.currentRowChanged.connect(window.on_product_selected)
        refs.btn_save_product.clicked.connect(window.on_product_save_clicked)
        refs.btn_apply_pending.clicked.connect(window.on_product_pending_apply_clicked)
        refs.btn_register_sale.clicked.connect(window.on_product_sale_clicked)

    @staticmethod
    def _bind_work_order(window: "MainWindow") -> None:
        window.btn_back.clicked.connect(window.on_back_clicked)
        window.btn_reset.clicked.connect(window.on_reset_clicked)
        window.btn_save.clicked.connect(window.on_save_clicked)
        window.btn_load.clicked.connect(window.on_load_clicked)
        window.btn_upload.clicked.connect(window.upload_image)
        window.btn_delete_image.clicked.connect(window.delete_image)

        window.change_note_postit.text_changed.connect(window.on_change_note_changed)
        bar = window.postit_bar
        for target, (deleted_signal, changed_signal, added_signal, _) in MATERIAL_TARGET_CONFIGS.items():
            getattr(bar, deleted_signal).connect(lambda idx, material_target=target: window.on_material_deleted(material_target, idx))
            getattr(bar, changed_signal).connect(lambda idx, patch, material_target=target: window.on_material_changed(material_target, idx, patch))
            getattr(bar, added_signal).connect(lambda material_target=target: window.on_add_material_clicked(material_target))
        bar.basic_data_changed.connect(window.on_basic_postit_changed)
