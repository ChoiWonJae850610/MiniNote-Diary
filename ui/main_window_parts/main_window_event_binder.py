from __future__ import annotations

from typing import TYPE_CHECKING

from services.field_keys import MaterialTargets
from ui.main_window_parts.main_window_work_order_logic import MATERIAL_TARGET_CONFIGS

if TYPE_CHECKING:
    from ui.main_window import MainWindow


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
