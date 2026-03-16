from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QFrame, QHBoxLayout, QSpinBox, QWidget

from ui.image_preview import ImagePreview
from ui.layout_metrics import OrderPageLayout
from ui.messages import Buttons, DefaultTexts, HelperTexts, InfoMessages, Labels, Placeholders, SectionTitles
from ui.pages.common import (
    LabeledFieldRow,
    StatFieldRow,
    add_labeled_field_rows,
    add_two_column_stat_rows,
    make_form_grid,
    make_image_shell,
    make_right_aligned_button_row,
    make_scroll_panel,
)
from ui.pages.order_panels import TemplateListCard, add_panel_title, create_order_panel, make_order_value_label
from ui.theme import THEME, input_line_edit_style
from ui.widget_factory import make_action_button, make_field_label, make_hint_label, make_input_line_edit, make_panel_frame, make_plain_text_editor, make_section_title_label


def build_filter_panel(page: QWidget) -> QFrame:
    filter_panel = make_panel_frame(page, compact=True)
    filter_layout = QHBoxLayout(filter_panel)
    filter_layout.setContentsMargins(THEME.filter_panel_margin_h, THEME.filter_panel_margin_v, THEME.filter_panel_margin_h, THEME.filter_panel_margin_v)
    filter_layout.setSpacing(THEME.row_spacing)

    month_combo = QComboBox(filter_panel)
    month_combo.setObjectName('orderMonthCombo')
    month_combo.setFixedWidth(OrderPageLayout.MONTH_COMBO_WIDTH)
    search_edit = make_input_line_edit(filter_panel, placeholder=Placeholders.ORDER_SEARCH)
    search_edit.setObjectName('orderSearchEdit')
    btn_reload = make_action_button(Buttons.REFRESH, filter_panel, width=THEME.reload_button_width, height=THEME.primary_button_height - 2)
    btn_reload.setObjectName('orderReloadButton')

    filter_layout.addWidget(make_field_label(Labels.MONTH_FILTER, filter_panel))
    filter_layout.addWidget(month_combo)
    filter_layout.addSpacing(OrderPageLayout.FILTER_INLINE_GAP)
    filter_layout.addWidget(make_field_label(Labels.SEARCH, filter_panel))
    filter_layout.addWidget(search_edit, 1)
    filter_layout.addWidget(btn_reload)
    return filter_panel



def build_right_panels(page: QWidget) -> dict[str, QWidget]:
    right_refs = make_scroll_panel(page)
    summary_refs = build_summary_panel(right_refs.wrap)
    order_refs = build_order_panel(right_refs.wrap)

    right_refs.layout.addWidget(summary_refs['panel'])
    right_refs.layout.addWidget(order_refs['panel'])
    right_refs.layout.addStretch(1)
    return {'scroll_area': right_refs.scroll_area, **summary_refs, **order_refs}



def build_summary_panel(parent: QWidget) -> dict[str, QWidget]:
    summary_panel, summary_layout = create_order_panel(parent, spacing=THEME.section_gap)
    add_panel_title(summary_layout, summary_panel, SectionTitles.ORDER_TEMPLATE_DETAIL)

    top_summary = QHBoxLayout()
    top_summary.setSpacing(THEME.section_gap)
    image_preview = ImagePreview()
    image_preview.setMinimumSize(THEME.image_preview_min_size, THEME.image_preview_min_size)
    top_summary.addWidget(make_image_shell(summary_panel, image_preview), 5)

    lbl_name = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_factory = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_date = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_cost = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_labor = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_sale_price = make_order_value_label(DefaultTexts.EMPTY_VALUE)

    detail_grid = make_form_grid()
    detail_grid.setColumnStretch(1, 1)
    add_labeled_field_rows(
        detail_grid,
        [
            LabeledFieldRow(Labels.ORDER_TEMPLATE, lbl_name, label_parent=summary_panel),
            LabeledFieldRow(Labels.FACTORY, lbl_factory, label_parent=summary_panel),
            LabeledFieldRow(Labels.BASE_DATE, lbl_date, label_parent=summary_panel),
            LabeledFieldRow(Labels.COST, lbl_cost, label_parent=summary_panel),
            LabeledFieldRow(Labels.LABOR, lbl_labor, label_parent=summary_panel),
            LabeledFieldRow(Labels.SALE_PRICE, lbl_sale_price, label_parent=summary_panel),
        ],
    )
    top_summary.addLayout(detail_grid, 8)
    summary_layout.addLayout(top_summary)

    stats_panel = QFrame(summary_panel)
    stats_panel.setObjectName('innerPanelFrame')
    stats_layout = make_form_grid(parent=stats_panel)
    stats_layout.setContentsMargins(THEME.filter_panel_margin_h, THEME.filter_panel_margin_v, THEME.filter_panel_margin_h, THEME.filter_panel_margin_v)

    lbl_last_order = make_order_value_label(InfoMessages.NO_ORDER_HISTORY)
    lbl_total_ordered = make_order_value_label('0')
    lbl_in_progress = make_order_value_label('0')
    lbl_current_stock = make_order_value_label('0')
    add_two_column_stat_rows(
        stats_layout,
        [
            StatFieldRow(Labels.LAST_ORDER, lbl_last_order),
            StatFieldRow(Labels.TOTAL_ORDERED, lbl_total_ordered),
            StatFieldRow(Labels.IN_PROGRESS_QTY, lbl_in_progress),
            StatFieldRow(Labels.CURRENT_STOCK, lbl_current_stock),
        ],
        label_parent=stats_panel,
    )
    summary_layout.addWidget(stats_panel)


    summary_layout.addWidget(make_section_title_label(SectionTitles.ORDER_TEMPLATE_MATERIAL_DETAIL, summary_panel))
    material_detail_view = make_plain_text_editor(summary_panel, read_only=True, min_height=THEME.order_memo_min_height + 90)
    material_detail_view.setStyleSheet(material_detail_view.styleSheet() + ' QTextEdit{font-family:"Consolas","D2Coding","Courier New",monospace;}')
    summary_layout.addWidget(material_detail_view)

    lbl_total_material_cost = make_order_value_label(DefaultTexts.EMPTY_VALUE)

    summary_layout.addWidget(make_section_title_label(SectionTitles.ORDER_TEMPLATE_MEMO, summary_panel))
    memo_view = make_plain_text_editor(summary_panel, read_only=True, min_height=THEME.memo_min_height)
    summary_layout.addWidget(memo_view)

    return {
        'panel': summary_panel,
        'image_preview': image_preview,
        'lbl_name': lbl_name,
        'lbl_factory': lbl_factory,
        'lbl_date': lbl_date,
        'lbl_cost': lbl_cost,
        'lbl_labor': lbl_labor,
        'lbl_sale_price': lbl_sale_price,
        'lbl_last_order': lbl_last_order,
        'lbl_total_ordered': lbl_total_ordered,
        'lbl_in_progress': lbl_in_progress,
        'lbl_current_stock': lbl_current_stock,
        'material_detail_view': material_detail_view,
        'lbl_total_material_cost': lbl_total_material_cost,
        'memo_view': memo_view,
    }



def build_order_panel(parent: QWidget) -> dict[str, QWidget]:
    order_panel, order_layout = create_order_panel(parent, spacing=THEME.block_spacing)
    add_panel_title(order_layout, order_panel, SectionTitles.ORDER_INPUT)
    helper_label = make_hint_label(HelperTexts.ORDER_SAVE_HINT, order_panel)
    order_layout.addWidget(helper_label)

    order_grid = make_form_grid()
    order_qty_spin = QSpinBox(order_panel)
    order_qty_spin.setMinimum(1)
    order_qty_spin.setMaximum(999999)
    order_qty_spin.setFixedHeight(THEME.order_input_height)
    order_qty_spin.setStyleSheet(input_line_edit_style())

    order_date_edit = QDateEdit(order_panel)
    order_date_edit.setCalendarPopup(True)
    order_date_edit.setDate(QDate.currentDate())
    order_date_edit.setDisplayFormat('yyyy-MM-dd')
    order_date_edit.setFixedHeight(THEME.order_input_height)
    order_date_edit.setStyleSheet(input_line_edit_style())

    order_memo_edit = make_plain_text_editor(order_panel, min_height=THEME.order_memo_min_height)
    add_labeled_field_rows(
        order_grid,
        [
            LabeledFieldRow(Labels.ORDER_QTY, order_qty_spin, label_parent=order_panel),
            LabeledFieldRow(Labels.ORDER_DATE, order_date_edit, label_parent=order_panel),
            LabeledFieldRow(Labels.ORDER_MEMO, order_memo_edit, align_top=True, label_parent=order_panel),
        ],
    )
    order_layout.addLayout(order_grid)

    btn_order = make_action_button(Buttons.ORDER_SAVE, order_panel, primary=True, width=THEME.primary_button_width, height=THEME.primary_button_height)
    order_layout.addLayout(make_right_aligned_button_row(btn_order))

    return {
        'panel': order_panel,
        'btn_order': btn_order,
        'order_qty_spin': order_qty_spin,
        'order_date_edit': order_date_edit,
        'order_memo_edit': order_memo_edit,
        'helper_label': helper_label,
    }


__all__ = ['TemplateListCard', 'build_filter_panel', 'build_order_panel', 'build_right_panels', 'build_summary_panel']
