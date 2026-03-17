from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QDateEdit, QHBoxLayout, QListWidget, QPushButton, QSpinBox, QTextEdit, QWidget

from ui.messages import Buttons, DefaultTexts, Labels, SectionTitles
from ui.pages.common import (
    LabeledFieldRow,
    StatFieldRow,
    add_labeled_field_rows,
    add_two_column_stat_rows,
    make_form_grid,
    make_right_aligned_button_row,
    make_scroll_panel,
    make_standard_page_header,
    make_standard_page_layout,
    make_titled_panel,
)
from ui.pages.order_panels import TemplateListCard, add_panel_title, create_order_panel, make_order_value_label
from ui.theme import THEME, input_line_edit_style, list_widget_style
from ui.widget_factory import make_action_button, make_hint_label, make_plain_text_editor


@dataclass
class ProductPageRefs:
    page: QWidget
    btn_back: QPushButton
    product_list: QListWidget
    lbl_name: QWidget
    lbl_code: QWidget
    lbl_stock_qty: QWidget
    lbl_pending_qty: QWidget
    lbl_defect_qty: QWidget
    price_spin: QSpinBox
    product_note_edit: QTextEdit
    btn_save_product: QPushButton
    pending_list: QListWidget
    btn_apply_pending: QPushButton
    sale_date_edit: QDateEdit
    sale_qty_spin: QSpinBox
    sale_price_spin: QSpinBox
    sale_memo_edit: QTextEdit
    btn_register_sale: QPushButton


class ProductPageBuilder:
    @staticmethod
    def build() -> ProductPageRefs:
        page = QWidget()
        page.setObjectName('productPage')
        root = make_standard_page_layout(page)

        header_refs = make_standard_page_header(page, title_text='상품관리', subtitle_text='')
        root.addLayout(header_refs.row)

        body_row = QHBoxLayout()
        body_row.setSpacing(THEME.section_gap)

        left_panel, left_layout = make_titled_panel(page, title_text='상품 목록', hint_text='')
        product_list = QListWidget(left_panel)
        product_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        product_list.setSpacing(6)
        product_list.setStyleSheet(list_widget_style())
        left_layout.addWidget(product_list, 1)

        right_refs = _build_right_panels(page)
        body_row.addWidget(left_panel, 4)
        body_row.addWidget(right_refs['scroll_area'], 6)
        root.addLayout(body_row, 1)

        return ProductPageRefs(
            page=page,
            btn_back=header_refs.back_button,
            product_list=product_list,
            lbl_name=right_refs['lbl_name'],
            lbl_code=right_refs['lbl_code'],
            lbl_stock_qty=right_refs['lbl_stock_qty'],
            lbl_pending_qty=right_refs['lbl_pending_qty'],
            lbl_defect_qty=right_refs['lbl_defect_qty'],
            price_spin=right_refs['price_spin'],
            product_note_edit=right_refs['product_note_edit'],
            btn_save_product=right_refs['btn_save_product'],
            pending_list=right_refs['pending_list'],
            btn_apply_pending=right_refs['btn_apply_pending'],
            sale_date_edit=right_refs['sale_date_edit'],
            sale_qty_spin=right_refs['sale_qty_spin'],
            sale_price_spin=right_refs['sale_price_spin'],
            sale_memo_edit=right_refs['sale_memo_edit'],
            btn_register_sale=right_refs['btn_register_sale'],
        )


def _build_right_panels(page: QWidget) -> dict[str, QWidget]:
    right_refs = make_scroll_panel(page)
    summary_refs = _build_summary_panel(right_refs.wrap)
    product_refs = _build_product_panel(right_refs.wrap)
    pending_refs = _build_pending_panel(right_refs.wrap)
    sale_refs = _build_sale_panel(right_refs.wrap)
    right_refs.layout.addWidget(summary_refs['panel'])
    right_refs.layout.addWidget(product_refs['panel'])
    right_refs.layout.addWidget(pending_refs['panel'])
    right_refs.layout.addWidget(sale_refs['panel'])
    right_refs.layout.addStretch(1)
    return {'scroll_area': right_refs.scroll_area, **summary_refs, **product_refs, **pending_refs, **sale_refs}


def _build_summary_panel(parent: QWidget) -> dict[str, QWidget]:
    panel, layout = create_order_panel(parent, spacing=THEME.section_gap)
    add_panel_title(layout, panel, '상품 요약')

    lbl_name = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_code = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    grid = make_form_grid()
    grid.setColumnStretch(1, 1)
    add_labeled_field_rows(
        grid,
        [
            LabeledFieldRow('상품명', lbl_name, label_parent=panel),
            LabeledFieldRow('상품코드', lbl_code, label_parent=panel),
        ],
    )
    layout.addLayout(grid)

    stats_panel = QWidget(panel)
    stats_layout = make_form_grid(parent=stats_panel)
    stats_layout.setContentsMargins(0, 0, 0, 0)
    lbl_stock_qty = make_order_value_label('0')
    lbl_pending_qty = make_order_value_label('0')
    lbl_defect_qty = make_order_value_label('0')
    add_two_column_stat_rows(
        stats_layout,
        [
            StatFieldRow('현재 재고', lbl_stock_qty),
            StatFieldRow('미검수 수량', lbl_pending_qty),
            StatFieldRow('불량 누계', lbl_defect_qty),
        ],
        label_parent=stats_panel,
    )
    layout.addWidget(stats_panel)
    return {
        'panel': panel,
        'lbl_name': lbl_name,
        'lbl_code': lbl_code,
        'lbl_stock_qty': lbl_stock_qty,
        'lbl_pending_qty': lbl_pending_qty,
        'lbl_defect_qty': lbl_defect_qty,
    }


def _build_product_panel(parent: QWidget) -> dict[str, QWidget]:
    panel, layout = create_order_panel(parent, spacing=THEME.block_spacing)
    add_panel_title(layout, panel, '상품 정보')

    form_grid = make_form_grid()
    price_spin = QSpinBox(panel)
    price_spin.setRange(0, 10_000_000)
    price_spin.setSingleStep(100)
    price_spin.setFixedHeight(THEME.order_input_height)
    price_spin.setStyleSheet(input_line_edit_style())
    form_grid.addWidget(make_hint_label('판매가', panel, word_wrap=False), 0, 0)
    form_grid.addWidget(price_spin, 0, 1)
    layout.addLayout(form_grid)

    product_note_edit = make_plain_text_editor(panel, read_only=False, min_height=THEME.memo_min_height)
    product_note_edit.setPlaceholderText('상품 메모를 입력하세요')
    layout.addWidget(product_note_edit)

    btn_save_product = make_action_button('상품 저장', panel, width=THEME.footer_button_width, height=THEME.primary_button_height)
    layout.addLayout(make_right_aligned_button_row(btn_save_product))
    return {'panel': panel, 'price_spin': price_spin, 'product_note_edit': product_note_edit, 'btn_save_product': btn_save_product}


def _build_pending_panel(parent: QWidget) -> dict[str, QWidget]:
    panel, layout = create_order_panel(parent, spacing=THEME.block_spacing)
    add_panel_title(layout, panel, '미검수 검수')
    pending_list = QListWidget(panel)
    pending_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
    pending_list.setSpacing(6)
    pending_list.setStyleSheet(list_widget_style())
    pending_list.setMinimumHeight(180)
    layout.addWidget(pending_list)
    btn_apply_pending = make_action_button('선택 미검수 검수', panel, width=THEME.footer_button_width + 60, height=THEME.primary_button_height)
    layout.addLayout(make_right_aligned_button_row(btn_apply_pending))
    return {'panel': panel, 'pending_list': pending_list, 'btn_apply_pending': btn_apply_pending}


def _build_sale_panel(parent: QWidget) -> dict[str, QWidget]:
    panel, layout = create_order_panel(parent, spacing=THEME.block_spacing)
    add_panel_title(layout, panel, '판매 등록')
    form_grid = make_form_grid()

    sale_date_edit = QDateEdit(panel)
    sale_date_edit.setCalendarPopup(True)
    sale_date_edit.setDate(QDate.currentDate())
    sale_date_edit.setDisplayFormat('yyyy-MM-dd')
    sale_date_edit.setFixedHeight(THEME.order_input_height)
    sale_date_edit.setStyleSheet(input_line_edit_style())

    sale_qty_spin = QSpinBox(panel)
    sale_qty_spin.setRange(0, 999999)
    sale_qty_spin.setFixedHeight(THEME.order_input_height)
    sale_qty_spin.setStyleSheet(input_line_edit_style())

    sale_price_spin = QSpinBox(panel)
    sale_price_spin.setRange(0, 10_000_000)
    sale_price_spin.setSingleStep(100)
    sale_price_spin.setFixedHeight(THEME.order_input_height)
    sale_price_spin.setStyleSheet(input_line_edit_style())

    add_labeled_field_rows(
        form_grid,
        [
            LabeledFieldRow('판매일', sale_date_edit, label_parent=panel),
            LabeledFieldRow('판매 수량', sale_qty_spin, label_parent=panel),
            LabeledFieldRow('판매 단가', sale_price_spin, label_parent=panel),
        ],
    )
    layout.addLayout(form_grid)

    sale_memo_edit = make_plain_text_editor(panel, read_only=False, min_height=THEME.memo_min_height)
    sale_memo_edit.setPlaceholderText('판매 메모를 입력하세요')
    layout.addWidget(sale_memo_edit)

    btn_register_sale = make_action_button('판매 등록', panel, width=THEME.footer_button_width, height=THEME.primary_button_height)
    layout.addLayout(make_right_aligned_button_row(btn_register_sale))
    return {
        'panel': panel,
        'sale_date_edit': sale_date_edit,
        'sale_qty_spin': sale_qty_spin,
        'sale_price_spin': sale_price_spin,
        'sale_memo_edit': sale_memo_edit,
        'btn_register_sale': btn_register_sale,
    }
