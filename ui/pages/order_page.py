from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QComboBox, QLabel, QLineEdit, QListWidget, QPushButton, QSpinBox, QTextEdit, QWidget
from PySide6.QtWidgets import QDateEdit, QHBoxLayout

from ui.image_preview import ImagePreview
from ui.layout_metrics import OrderPageLayout
from ui.messages import PageDescriptions, PageTitles, SectionTitles
from ui.pages.common import make_standard_page_header, make_standard_page_layout, make_titled_panel
from ui.pages.order_sections import TemplateListCard, build_filter_panel, build_right_panels
from ui.theme import THEME, list_widget_style


@dataclass
class OrderPageRefs:
    page: QWidget
    btn_back: QPushButton
    btn_reload: QPushButton
    btn_order: QPushButton
    month_combo: QComboBox
    search_edit: QLineEdit
    template_list: QListWidget
    image_preview: ImagePreview
    lbl_name: QLabel
    lbl_factory: QLabel
    lbl_date: QLabel
    lbl_cost: QLabel
    lbl_labor: QLabel
    lbl_sale_price: QLabel
    lbl_material_summary: QLabel
    lbl_last_order: QLabel
    lbl_total_ordered: QLabel
    lbl_in_progress: QLabel
    lbl_current_stock: QLabel
    memo_view: QTextEdit
    material_detail_view: QTextEdit
    lbl_total_material_cost: QLabel
    order_qty_spin: QSpinBox
    order_date_edit: QDateEdit
    order_memo_edit: QTextEdit
    helper_label: QLabel


class OrderPageBuilder:
    @staticmethod
    def build() -> OrderPageRefs:
        page = QWidget()
        page.setObjectName('orderPage')
        root = make_standard_page_layout(page)
        root.setContentsMargins(THEME.page_padding_x, THEME.page_header_top_margin, THEME.page_padding_x, THEME.page_top_bottom)

        header_refs = make_standard_page_header(page, title_text=PageTitles.ORDER, subtitle_text='')
        root.addLayout(header_refs.row)
        root.addWidget(build_filter_panel(page))

        body_row = QHBoxLayout()
        body_row.setSpacing(THEME.section_gap)

        left_panel, left_layout = make_titled_panel(page, title_text=SectionTitles.ORDER_TEMPLATE_LIST, hint_text='')
        template_list = QListWidget(left_panel)
        template_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        template_list.setSpacing(OrderPageLayout.TEMPLATE_LIST_SPACING)
        template_list.setStyleSheet(list_widget_style())
        left_layout.addWidget(template_list, 1)

        right_refs = build_right_panels(page)
        body_row.addWidget(left_panel, 4)
        body_row.addWidget(right_refs['scroll_area'], 6)
        root.addLayout(body_row, 1)

        return OrderPageRefs(
            page=page,
            btn_back=header_refs.back_button,
            btn_reload=page.findChild(QPushButton, 'orderReloadButton'),
            btn_order=right_refs['btn_order'],
            month_combo=page.findChild(QComboBox, 'orderMonthCombo'),
            search_edit=page.findChild(QLineEdit, 'orderSearchEdit'),
            template_list=template_list,
            image_preview=right_refs['image_preview'],
            lbl_name=right_refs['lbl_name'],
            lbl_factory=right_refs['lbl_factory'],
            lbl_date=right_refs['lbl_date'],
            lbl_cost=right_refs['lbl_cost'],
            lbl_labor=right_refs['lbl_labor'],
            lbl_sale_price=right_refs['lbl_sale_price'],
            lbl_material_summary=QLabel(page),
            lbl_last_order=right_refs['lbl_last_order'],
            lbl_total_ordered=right_refs['lbl_total_ordered'],
            lbl_in_progress=right_refs['lbl_in_progress'],
            lbl_current_stock=right_refs['lbl_current_stock'],
            memo_view=right_refs['memo_view'],
            material_detail_view=right_refs['material_detail_view'],
            lbl_total_material_cost=right_refs['lbl_total_material_cost'],
            order_qty_spin=right_refs['order_qty_spin'],
            order_date_edit=right_refs['order_date_edit'],
            order_memo_edit=right_refs['order_memo_edit'],
            helper_label=right_refs['helper_label'],
        )


__all__ = ['OrderPageBuilder', 'OrderPageRefs', 'TemplateListCard']
