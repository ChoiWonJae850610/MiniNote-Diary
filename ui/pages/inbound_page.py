from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QHBoxLayout, QListWidget, QPushButton, QSpinBox, QTextEdit, QWidget

from ui.image_preview import ImagePreview
from ui.messages import Buttons, DefaultTexts, Labels, Placeholders, SectionTitles
from ui.pages.common import (
    LabeledFieldRow,
    StatFieldRow,
    add_labeled_field_rows,
    add_two_column_stat_rows,
    make_form_grid,
    make_image_shell,
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
class InboundPageRefs:
    page: QWidget
    btn_back: QPushButton
    btn_reload: QPushButton
    btn_apply: QPushButton
    order_list: QListWidget
    image_preview: ImagePreview
    lbl_name: QWidget
    lbl_factory: QWidget
    lbl_order_date: QWidget
    lbl_order_qty: QWidget
    lbl_completed_qty: QWidget
    lbl_remaining_qty: QWidget
    lbl_status: QWidget
    lbl_lead_days: QWidget
    order_memo_view: QTextEdit
    inbound_date_edit: QDateEdit
    inbound_qty_spin: QSpinBox
    inbound_memo_edit: QTextEdit
    helper_label: QWidget


class InboundPageBuilder:
    @staticmethod
    def build() -> InboundPageRefs:
        page = QWidget()
        page.setObjectName('inboundPage')
        root = make_standard_page_layout(page)

        header_refs = make_standard_page_header(page, title_text=SectionTitles.INBOUND_PAGE, subtitle_text='')
        root.addLayout(header_refs.row)

        toolbar_panel, toolbar_layout = make_titled_panel(page, title_text=SectionTitles.INBOUND_FILTER, hint_text='', compact=True)
        toolbar_layout.setContentsMargins(THEME.filter_panel_margin_h, THEME.filter_panel_margin_v, THEME.filter_panel_margin_h, THEME.filter_panel_margin_v)
        btn_reload = make_action_button(Buttons.REFRESH, toolbar_panel, width=THEME.reload_button_width, height=THEME.primary_button_height - 2)
        btn_reload.setObjectName('inboundReloadButton')
        hint = make_hint_label(Placeholders.INBOUND_FILTER_HINT, toolbar_panel)
        toolbar_layout.addWidget(hint, 1)
        toolbar_layout.addWidget(btn_reload)
        root.addWidget(toolbar_panel)

        body_row = QHBoxLayout()
        body_row.setSpacing(THEME.section_gap)

        left_panel, left_layout = make_titled_panel(page, title_text=SectionTitles.INBOUND_ORDER_LIST, hint_text='')
        order_list = QListWidget(left_panel)
        order_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        order_list.setSpacing(6)
        order_list.setStyleSheet(list_widget_style())
        left_layout.addWidget(order_list, 1)

        right_refs = _build_right_panels(page)
        body_row.addWidget(left_panel, 4)
        body_row.addWidget(right_refs['scroll_area'], 6)
        root.addLayout(body_row, 1)

        return InboundPageRefs(
            page=page,
            btn_back=header_refs.back_button,
            btn_reload=btn_reload,
            btn_apply=right_refs['btn_apply'],
            order_list=order_list,
            image_preview=right_refs['image_preview'],
            lbl_name=right_refs['lbl_name'],
            lbl_factory=right_refs['lbl_factory'],
            lbl_order_date=right_refs['lbl_order_date'],
            lbl_order_qty=right_refs['lbl_order_qty'],
            lbl_completed_qty=right_refs['lbl_completed_qty'],
            lbl_remaining_qty=right_refs['lbl_remaining_qty'],
            lbl_status=right_refs['lbl_status'],
            lbl_lead_days=right_refs['lbl_lead_days'],
            order_memo_view=right_refs['order_memo_view'],
            inbound_date_edit=right_refs['inbound_date_edit'],
            inbound_qty_spin=right_refs['inbound_qty_spin'],
            inbound_memo_edit=right_refs['inbound_memo_edit'],
            helper_label=right_refs['helper_label'],
        )


def _build_right_panels(page: QWidget) -> dict[str, QWidget]:
    right_refs = make_scroll_panel(page)
    summary_refs = _build_summary_panel(right_refs.wrap)
    input_refs = _build_input_panel(right_refs.wrap)
    right_refs.layout.addWidget(summary_refs['panel'])
    right_refs.layout.addWidget(input_refs['panel'])
    right_refs.layout.addStretch(1)
    return {'scroll_area': right_refs.scroll_area, **summary_refs, **input_refs}


def _build_summary_panel(parent: QWidget) -> dict[str, QWidget]:
    summary_panel, summary_layout = create_order_panel(parent, spacing=THEME.section_gap)
    add_panel_title(summary_layout, summary_panel, SectionTitles.INBOUND_SELECTED_ORDER)

    top_row = QHBoxLayout()
    top_row.setSpacing(THEME.section_gap)
    image_preview = ImagePreview()
    image_preview.setMinimumSize(THEME.image_preview_min_size, THEME.image_preview_min_size)
    top_row.addWidget(make_image_shell(summary_panel, image_preview), 5)

    lbl_name = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_factory = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_order_date = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_order_qty = make_order_value_label('0')
    detail_grid = make_form_grid()
    detail_grid.setColumnStretch(1, 1)
    add_labeled_field_rows(
        detail_grid,
        [
            LabeledFieldRow(Labels.ORDER_TEMPLATE, lbl_name, label_parent=summary_panel),
            LabeledFieldRow(Labels.FACTORY, lbl_factory, label_parent=summary_panel),
            LabeledFieldRow(Labels.ORDER_DATE, lbl_order_date, label_parent=summary_panel),
            LabeledFieldRow(Labels.ORDER_QTY, lbl_order_qty, label_parent=summary_panel),
        ],
    )
    top_row.addLayout(detail_grid, 8)
    summary_layout.addLayout(top_row)

    stats_panel = QWidget(summary_panel)
    stats_layout = make_form_grid(parent=stats_panel)
    stats_layout.setContentsMargins(0, 0, 0, 0)
    lbl_completed_qty = make_order_value_label('0')
    lbl_remaining_qty = make_order_value_label('0')
    lbl_status = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    lbl_lead_days = make_order_value_label(DefaultTexts.EMPTY_VALUE)
    add_two_column_stat_rows(
        stats_layout,
        [
            StatFieldRow(Labels.COMPLETED_QTY, lbl_completed_qty),
            StatFieldRow(Labels.REMAINING_QTY, lbl_remaining_qty),
            StatFieldRow(Labels.ORDER_STATUS, lbl_status),
            StatFieldRow(Labels.LEAD_DAYS, lbl_lead_days),
        ],
        label_parent=stats_panel,
    )
    summary_layout.addWidget(stats_panel)

    add_panel_title(summary_layout, summary_panel, SectionTitles.ORDER_TEMPLATE_MEMO)
    order_memo_view = make_plain_text_editor(summary_panel, read_only=True, min_height=THEME.memo_min_height)
    summary_layout.addWidget(order_memo_view)

    return {
        'panel': summary_panel,
        'image_preview': image_preview,
        'lbl_name': lbl_name,
        'lbl_factory': lbl_factory,
        'lbl_order_date': lbl_order_date,
        'lbl_order_qty': lbl_order_qty,
        'lbl_completed_qty': lbl_completed_qty,
        'lbl_remaining_qty': lbl_remaining_qty,
        'lbl_status': lbl_status,
        'lbl_lead_days': lbl_lead_days,
        'order_memo_view': order_memo_view,
    }


def _build_input_panel(parent: QWidget) -> dict[str, QWidget]:
    panel, layout = create_order_panel(parent, spacing=THEME.block_spacing)
    add_panel_title(layout, panel, SectionTitles.INBOUND_INPUT)

    helper_label = make_hint_label('', panel)
    helper_label.hide()
    layout.addWidget(helper_label)

    form_grid = make_form_grid()

    inbound_date_edit = QDateEdit(panel)
    inbound_date_edit.setCalendarPopup(True)
    inbound_date_edit.setDate(QDate.currentDate())
    inbound_date_edit.setDisplayFormat('yyyy-MM-dd')
    inbound_date_edit.setFixedHeight(THEME.order_input_height)
    inbound_date_edit.setStyleSheet(input_line_edit_style())

    inbound_qty_spin = QSpinBox(panel)
    inbound_qty_spin.setMinimum(0)
    inbound_qty_spin.setMaximum(999999)
    inbound_qty_spin.setFixedHeight(THEME.order_input_height)
    inbound_qty_spin.setStyleSheet(input_line_edit_style())

    inbound_memo_edit = make_plain_text_editor(panel, min_height=THEME.order_memo_min_height)

    add_labeled_field_rows(
        form_grid,
        [
            LabeledFieldRow(Labels.INBOUND_DATE, inbound_date_edit, label_parent=panel),
            LabeledFieldRow(Labels.INBOUND_QTY, inbound_qty_spin, label_parent=panel),
            LabeledFieldRow(Labels.ORDER_MEMO, inbound_memo_edit, align_top=True, label_parent=panel),
        ],
    )
    layout.addLayout(form_grid)

    btn_apply = make_action_button(Buttons.INBOUND_APPLY, panel, primary=True, width=THEME.primary_button_width, height=THEME.primary_button_height)
    layout.addLayout(make_right_aligned_button_row(btn_apply))

    return {
        'panel': panel,
        'btn_apply': btn_apply,
        'inbound_date_edit': inbound_date_edit,
        'inbound_qty_spin': inbound_qty_spin,
        'inbound_memo_edit': inbound_memo_edit,
        'helper_label': helper_label,
    }


__all__ = ['InboundPageBuilder', 'InboundPageRefs', 'TemplateListCard']
