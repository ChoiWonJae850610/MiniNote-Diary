from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ui.feature_page import FeaturePageBuilder
from ui.menu_page import MenuPageBuilder
from ui.pages import InboundPageBuilder, OrderPageBuilder, ProductPageBuilder, StatsPageBuilder, WorkOrderPageBuilder

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowPageCoordinator:
    PAGE_NAMES_BY_FEATURE_KEY = {
        'receipt': 'page_receipt',
        'complete': 'page_complete',
        'inventory': 'page_inventory',
        'partner': 'page_partner',
    }

    @staticmethod
    def build_pages(window: "MainWindow") -> None:
        menu_refs = MenuPageBuilder.build()
        work_refs = WorkOrderPageBuilder.build(window)
        order_refs = OrderPageBuilder.build()
        inbound_refs = InboundPageBuilder.build()
        product_refs = ProductPageBuilder.build()
        stats_refs = StatsPageBuilder.build()
        window.work_order_page_ref = work_refs.page
        feature_pages = {config.key: FeaturePageBuilder.build(config) for config in window.build_feature_page_configs() if config.key not in {'sale', 'inventory'}}

        MainWindowPageCoordinator._apply_menu_refs(window, menu_refs)
        MainWindowPageCoordinator._apply_work_order_refs(window, work_refs)
        window.order_page_refs = order_refs
        window.inbound_page_refs = inbound_refs
        window.product_page_refs = product_refs
        window.stats_page_refs = stats_refs
        window.feature_pages = feature_pages
        window.pages = MainWindowPageCoordinator._build_page_map(window, menu_refs, order_refs, inbound_refs, product_refs, stats_refs, feature_pages)

        for page in window.pages.values():
            window.stack.addWidget(page)
        window.stack.setCurrentIndex(window.PAGE_MENU)

    @staticmethod
    def _apply_menu_refs(window: "MainWindow", refs) -> None:
        window.menu_page_refs = refs
        window.btn_template = refs.btn_template
        window.btn_job_start_menu = refs.btn_job_start
        window.btn_receipt_menu = refs.btn_receipt
        window.btn_complete_menu = refs.btn_complete
        window.btn_sale_menu = refs.btn_sale
        window.btn_inventory_menu = refs.btn_inventory
        window.btn_partner_mgmt_menu = refs.btn_partner_mgmt
        window.btn_unit_mgmt_menu = refs.btn_unit_mgmt
        window.btn_product_type_mgmt_menu = refs.btn_product_type_mgmt
        window.btn_material_mgmt_menu = refs.btn_material_mgmt
        window.btn_settings = refs.btn_settings

    @staticmethod
    def _apply_work_order_refs(window: "MainWindow", refs) -> None:
        window.btn_back = refs.btn_back
        window.btn_reset = refs.btn_reset
        window.btn_load = refs.btn_load
        window.btn_save = refs.btn_save
        window.btn_upload = refs.btn_upload
        window.btn_delete_image = refs.btn_delete_image
        window.feedback_label = refs.feedback_label
        window.image_preview = refs.image_preview
        window.change_note_postit = refs.change_note_postit
        window.postit_bar = refs.postit_bar

    @staticmethod
    def _build_page_map(window: "MainWindow", menu_refs, order_refs, inbound_refs, product_refs, stats_refs, feature_pages: dict[str, object]) -> dict[str, QWidget]:
        return {
            'page_menu': menu_refs.page,
            'page_work_order': window.work_order_page_ref,
            'page_job_start': order_refs.page,
            'page_receipt': feature_pages['receipt'].page,
            'page_complete': inbound_refs.page,
            'page_sale': product_refs.page,
            'page_inventory': stats_refs.page,
            'page_partner': feature_pages['partner'].page,
        }
