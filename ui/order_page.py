from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.image_preview import ImagePreview
from ui.theme import THEME, display_field_style, field_label_style, hint_label_style, input_line_edit_style, plain_text_edit_style, inner_panel_frame_style, list_widget_style, panel_title_style
from ui.widget_factory import apply_button_metrics, apply_icon_button_metrics, make_hint_label, make_page_title_label, make_panel_frame, make_panel_title_label, make_value_label


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
    order_qty_spin: QSpinBox
    order_date_edit: QDateEdit
    order_memo_edit: QTextEdit
    helper_label: QLabel


class OrderPageBuilder:
    @staticmethod
    def build() -> OrderPageRefs:
        page = QWidget()
        page.setObjectName('orderPage')
        root = QVBoxLayout(page)
        root.setContentsMargins(THEME.page_padding_x, THEME.page_header_top_margin, THEME.page_padding_x, THEME.page_top_bottom)
        root.setSpacing(THEME.section_gap)

        top_row = QHBoxLayout()
        top_row.setSpacing(THEME.top_button_spacing)
        btn_back = QPushButton('◀')
        apply_icon_button_metrics(btn_back, font_px=THEME.icon_button_font_px + 2, object_name='navButton', tooltip='뒤로가기')
        title_col = QVBoxLayout()
        title_col.setSpacing(THEME.title_stack_spacing)
        title = make_page_title_label('발주', page)
        subtitle = make_hint_label('저장된 작업지시서 템플릿을 선택하고 발주 수량을 입력합니다.', page)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        top_row.addWidget(btn_back, 0, Qt.AlignTop)
        top_row.addLayout(title_col, 1)
        root.addLayout(top_row)

        filter_panel = make_panel_frame(page, compact=True)
        filter_layout = QHBoxLayout(filter_panel)
        filter_layout.setContentsMargins(THEME.filter_panel_margin_h, THEME.filter_panel_margin_v, THEME.filter_panel_margin_h, THEME.filter_panel_margin_v)
        filter_layout.setSpacing(THEME.row_spacing)
        month_combo = QComboBox(filter_panel)
        month_combo.setFixedWidth(150)
        search_edit = QLineEdit(filter_panel)
        search_edit.setPlaceholderText('작업지시서 검색')
        search_edit.setStyleSheet(input_line_edit_style())
        btn_reload = QPushButton('목록 새로고침', filter_panel)
        apply_button_metrics(btn_reload, width=THEME.reload_button_width, height=THEME.primary_button_height - 2)
        filter_layout.addWidget(QLabel('기준 월', filter_panel))
        filter_layout.addWidget(month_combo)
        filter_layout.addSpacing(6)
        filter_layout.addWidget(QLabel('검색', filter_panel))
        filter_layout.addWidget(search_edit, 1)
        filter_layout.addWidget(btn_reload)
        root.addWidget(filter_panel)

        body_row = QHBoxLayout()
        body_row.setSpacing(THEME.section_gap)

        left_panel = make_panel_frame(page)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        left_layout.setSpacing(THEME.row_spacing)
        left_title = make_panel_title_label('작업지시서 목록', left_panel)
        left_hint = make_hint_label('월별 필터와 검색으로 템플릿을 찾고, 예전 작업지시서도 다시 발주할 수 있습니다.', left_panel)
        template_list = QListWidget(left_panel)
        template_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        template_list.setSpacing(6)
        template_list.setStyleSheet(list_widget_style())
        left_layout.addWidget(left_title)
        left_layout.addWidget(left_hint)
        left_layout.addWidget(template_list, 1)

        right_scroll = QScrollArea(page)
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right_wrap = QWidget()
        right_scroll.setWidget(right_wrap)
        right_layout = QVBoxLayout(right_wrap)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(THEME.section_gap)

        summary_panel = make_panel_frame(right_wrap)
        summary_layout = QVBoxLayout(summary_panel)
        summary_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        summary_layout.setSpacing(THEME.section_gap)
        summary_title = make_panel_title_label('선택 작업지시서', summary_panel)
        summary_layout.addWidget(summary_title)

        top_summary = QHBoxLayout()
        top_summary.setSpacing(THEME.section_gap)
        image_shell = QFrame(summary_panel)
        image_shell.setObjectName('imageShell')
        image_shell_layout = QVBoxLayout(image_shell)
        image_shell_layout.setContentsMargins(14, 14, 14, 14)
        image_preview = ImagePreview()
        image_preview.setMinimumSize(THEME.image_preview_min_size, THEME.image_preview_min_size)
        image_shell_layout.addWidget(image_preview)
        top_summary.addWidget(image_shell, 4)

        detail_grid = QGridLayout()
        detail_grid.setHorizontalSpacing(10)
        detail_grid.setVerticalSpacing(8)
        lbl_name = OrderPageBuilder._make_value_label('-')
        lbl_factory = OrderPageBuilder._make_value_label('-')
        lbl_date = OrderPageBuilder._make_value_label('-')
        lbl_cost = OrderPageBuilder._make_value_label('-')
        lbl_labor = OrderPageBuilder._make_value_label('-')
        lbl_sale_price = OrderPageBuilder._make_value_label('-')
        lbl_material_summary = OrderPageBuilder._make_value_label('원단 0 / 부자재 0')
        rows = [
            ('작업지시서', lbl_name),
            ('공장', lbl_factory),
            ('기준일', lbl_date),
            ('재료비', lbl_cost),
            ('공임', lbl_labor),
            ('원가', lbl_sale_price),
            ('자재 요약', lbl_material_summary),
        ]
        for row_idx, (label_text, value_widget) in enumerate(rows):
            label = QLabel(label_text, summary_panel)
            label.setStyleSheet(field_label_style())
            detail_grid.addWidget(label, row_idx, 0)
            detail_grid.addWidget(value_widget, row_idx, 1)
        top_summary.addLayout(detail_grid, 6)
        summary_layout.addLayout(top_summary)

        stats_panel = QFrame(summary_panel)
        stats_panel.setStyleSheet(inner_panel_frame_style())
        stats_layout = QGridLayout(stats_panel)
        stats_layout.setContentsMargins(THEME.filter_panel_margin_h, THEME.filter_panel_margin_v, THEME.filter_panel_margin_h, THEME.filter_panel_margin_v)
        stats_layout.setHorizontalSpacing(10)
        stats_layout.setVerticalSpacing(8)
        lbl_last_order = OrderPageBuilder._make_value_label('발주 이력 없음')
        lbl_total_ordered = OrderPageBuilder._make_value_label('0')
        lbl_in_progress = OrderPageBuilder._make_value_label('0')
        lbl_current_stock = OrderPageBuilder._make_value_label('0')
        stat_rows = [
            ('최근 발주', lbl_last_order),
            ('누적 발주', lbl_total_ordered),
            ('진행중 수량', lbl_in_progress),
            ('현재 재고', lbl_current_stock),
        ]
        for row_idx, (label_text, value_widget) in enumerate(stat_rows):
            label = QLabel(label_text, stats_panel)
            label.setStyleSheet(field_label_style())
            stats_layout.addWidget(label, row_idx // 2, (row_idx % 2) * 2)
            stats_layout.addWidget(value_widget, row_idx // 2, (row_idx % 2) * 2 + 1)
        summary_layout.addWidget(stats_panel)

        memo_title = QLabel('작업지시서 메모', summary_panel)
        memo_title.setStyleSheet(panel_title_style(font_px=THEME.section_title_font_px))
        memo_view = QTextEdit(summary_panel)
        memo_view.setReadOnly(True)
        memo_view.setMinimumHeight(THEME.memo_min_height)
        memo_view.setStyleSheet(plain_text_edit_style())
        summary_layout.addWidget(memo_title)
        summary_layout.addWidget(memo_view)
        right_layout.addWidget(summary_panel)

        order_panel = make_panel_frame(right_wrap)
        order_layout = QVBoxLayout(order_panel)
        order_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        order_layout.setSpacing(THEME.block_spacing)
        order_title = make_panel_title_label('신규 발주 입력', order_panel)
        helper_label = make_hint_label('발주 수량은 1 이상이어야 하며, 저장 후에도 작업지시서 템플릿은 계속 남아 다시 발주할 수 있습니다.', order_panel)
        order_layout.addWidget(order_title)
        order_layout.addWidget(helper_label)

        order_grid = QGridLayout()
        order_grid.setHorizontalSpacing(10)
        order_grid.setVerticalSpacing(8)
        order_qty_spin = QSpinBox(order_panel)
        order_qty_spin.setMinimum(1)
        order_qty_spin.setMaximum(999999)
        order_qty_spin.setFixedHeight(THEME.order_input_height)
        order_date_edit = QDateEdit(order_panel)
        order_date_edit.setCalendarPopup(True)
        order_date_edit.setDate(QDate.currentDate())
        order_date_edit.setDisplayFormat('yyyy-MM-dd')
        order_date_edit.setFixedHeight(THEME.order_input_height)
        order_memo_edit = QTextEdit(order_panel)
        order_memo_edit.setMinimumHeight(THEME.order_memo_min_height)
        order_memo_edit.setStyleSheet(plain_text_edit_style())
        order_qty_spin.setStyleSheet(input_line_edit_style())
        order_date_edit.setStyleSheet(input_line_edit_style())
        order_grid.addWidget(QLabel('발주 수량', order_panel), 0, 0)
        order_grid.addWidget(order_qty_spin, 0, 1)
        order_grid.addWidget(QLabel('발주일', order_panel), 1, 0)
        order_grid.addWidget(order_date_edit, 1, 1)
        order_grid.addWidget(QLabel('발주 메모', order_panel), 2, 0, Qt.AlignTop)
        order_grid.addWidget(order_memo_edit, 2, 1)
        order_layout.addLayout(order_grid)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        btn_order = QPushButton('발주 저장', order_panel)
        apply_button_metrics(btn_order, width=THEME.primary_button_width, height=THEME.primary_button_height)
        btn_order.setObjectName('primaryAction')
        button_row.addWidget(btn_order)
        order_layout.addLayout(button_row)
        right_layout.addWidget(order_panel)
        right_layout.addStretch(1)

        body_row.addWidget(left_panel, 4)
        body_row.addWidget(right_scroll, 6)
        root.addLayout(body_row, 1)

        return OrderPageRefs(
            page=page,
            btn_back=btn_back,
            btn_reload=btn_reload,
            btn_order=btn_order,
            month_combo=month_combo,
            search_edit=search_edit,
            template_list=template_list,
            image_preview=image_preview,
            lbl_name=lbl_name,
            lbl_factory=lbl_factory,
            lbl_date=lbl_date,
            lbl_cost=lbl_cost,
            lbl_labor=lbl_labor,
            lbl_sale_price=lbl_sale_price,
            lbl_material_summary=lbl_material_summary,
            lbl_last_order=lbl_last_order,
            lbl_total_ordered=lbl_total_ordered,
            lbl_in_progress=lbl_in_progress,
            lbl_current_stock=lbl_current_stock,
            memo_view=memo_view,
            order_qty_spin=order_qty_spin,
            order_date_edit=order_date_edit,
            order_memo_edit=order_memo_edit,
            helper_label=helper_label,
        )

    @staticmethod
    def _make_value_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setMinimumHeight(THEME.order_input_height - 2)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        label.setStyleSheet(display_field_style())
        return label


class TemplateListCard(QFrame):
    def __init__(self, *, title: str, subtitle: str, meta_lines: list[str], parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            inner_panel_frame_style()
            + f'QFrame:hover{{border-color:{THEME.color_border_hover}; background:{THEME.color_surface};}}'
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        title_label = QLabel(title, self)
        title_label.setStyleSheet(panel_title_style(font_px=THEME.section_title_font_px))
        subtitle_label = QLabel(subtitle, self)
        subtitle_label.setStyleSheet(hint_label_style())
        subtitle_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        for line in meta_lines:
            meta = QLabel(line, self)
            meta.setWordWrap(True)
            meta.setStyleSheet(f'QLabel{{color:{THEME.color_text_soft};background:transparent;}}')
            layout.addWidget(meta)
