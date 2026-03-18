from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication, QStackedWidget, QVBoxLayout, QWidget

from services.common.project_paths import project_root_str
from services.inbound.repository import InboundRepository
from services.order.repository import OrderRepository
from services.partner.lookup_service import PartnerLookupService
from services.product.repository import ProductRepository
from services.work_order.controller import WorkOrderController
from services.work_order.state import WorkOrderState
from ui.theme import THEME, build_app_stylesheet
from ui.window_policy import lock_window_size

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowBootstrap:
    @staticmethod
    def project_root() -> str:
        return project_root_str(__file__)

    @staticmethod
    def initialize_services(window: "MainWindow") -> None:
        window.project_root = MainWindowBootstrap.project_root()
        window.state = WorkOrderState()
        window.controller = WorkOrderController(window.state, window.project_root)
        window.order_repository = OrderRepository(window.project_root)
        window.inbound_repository = InboundRepository(window.project_root)
        window.product_repository = ProductRepository(window.project_root)
        window.partner_lookup_service = PartnerLookupService(window.project_root)
        window._suppress_dirty = False

    @staticmethod
    def build_root(window: "MainWindow") -> None:
        root = QWidget()
        window.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        window.stack = QStackedWidget()
        root_layout.addWidget(window.stack)

    @staticmethod
    def apply_defaults(window: "MainWindow") -> None:
        lock_window_size(window, width=THEME.window_min_width, height=THEME.window_min_height)
        window.setStyleSheet(build_app_stylesheet())
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(window)
        window._install_shortcuts()
        window._refresh_postits(force_rebuild=True)
        window._update_window_title()
