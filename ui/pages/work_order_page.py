from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from ui.icon_factory import make_image_upload_icon, make_save_icon, standard_icon
from ui.image_preview import ImagePreview
from ui.messages import PageTitles, SectionTitles, Tooltips
from ui.pages.common import (
    make_image_shell,
    make_standard_body_row,
    make_standard_page_header,
    make_standard_page_layout,
    make_standard_toolbar_strip,
)
from ui.postit import ChangeNotePostIt, PostItBar
from ui.theme import THEME, image_preview_style
from ui.widget_factory import make_toolbar_icon_button


@dataclass
class WorkOrderPageRefs:
    page: QWidget
    btn_back: QPushButton
    btn_help: QPushButton | None
    btn_reset: QPushButton
    btn_save: QPushButton
    btn_load: QPushButton
    btn_upload: QPushButton
    btn_delete_image: QPushButton
    btn_prev_page: QPushButton
    btn_next_page: QPushButton
    page_indicator: QLabel
    page_stack: QStackedWidget
    feedback_label: QWidget | None
    image_preview: ImagePreview
    image_shell: QWidget
    change_note_postit: ChangeNotePostIt
    postit_bar: PostItBar


class WorkOrderPageBuilder:
    @staticmethod
    def _build_section_card(title: str, body: QWidget, parent: QWidget, *, stretch: int = 0) -> QFrame:
        card = QFrame(parent)
        card.setObjectName('featureCard')
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding if stretch else QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title_label = QLabel(title, card)
        title_label.setObjectName('featureSectionTitle')
        layout.addWidget(title_label, 0, Qt.AlignTop)
        layout.addWidget(body, 1 if stretch else 0)
        return card

    @staticmethod
    def build(parent: QWidget) -> WorkOrderPageRefs:
        page = QWidget()
        page_layout = make_standard_page_layout(page)
        page_layout.setContentsMargins(12, THEME.page_header_top_margin, 12, 8)
        page_layout.setSpacing(max(THEME.row_spacing, THEME.section_gap - 4))

        header_refs = make_standard_page_header(
            page,
            title_text=PageTitles.WORK_ORDER,
            subtitle_text='',
        )

        toolbar_buttons = WorkOrderPageBuilder._build_toolbar_buttons(parent, page)
        WorkOrderPageBuilder._install_header_actions(header_refs, toolbar_buttons, page)
        postit_bar = PostItBar()
        image_preview, image_shell, image_toolbar = WorkOrderPageBuilder._build_image_page(page, toolbar_buttons)
        change_note_postit, change_note_wrap = WorkOrderPageBuilder._build_change_note_column(page)
        info_page = WorkOrderPageBuilder._build_info_page(page, postit_bar, change_note_wrap)

        page_stack = QStackedWidget(page)
        page_stack.setObjectName('workOrderDiaryStack')
        page_stack.addWidget(info_page)
        page_stack.addWidget(image_shell.parentWidget())
        page_stack.setCurrentIndex(0)

        btn_prev_page, btn_next_page, page_indicator, pager_row = WorkOrderPageBuilder._build_pager(page)
        WorkOrderPageBuilder._update_pager_ui(page_stack, btn_prev_page, btn_next_page, page_indicator)

        page_layout.addLayout(header_refs.row)
        page_layout.addWidget(page_stack, 1)
        page_layout.addLayout(pager_row)

        return WorkOrderPageRefs(
            page=page,
            btn_back=header_refs.back_button,
            btn_help=header_refs.help_button,
            btn_reset=toolbar_buttons['btn_reset'],
            btn_save=toolbar_buttons['btn_save'],
            btn_load=toolbar_buttons['btn_load'],
            btn_upload=toolbar_buttons['btn_upload'],
            btn_delete_image=toolbar_buttons['btn_delete_image'],
            btn_prev_page=btn_prev_page,
            btn_next_page=btn_next_page,
            page_indicator=page_indicator,
            page_stack=page_stack,
            feedback_label=None,
            image_preview=image_preview,
            image_shell=image_shell,
            change_note_postit=change_note_postit,
            postit_bar=postit_bar,
        )

    @staticmethod
    def _build_pager(page: QWidget) -> tuple[QPushButton, QPushButton, QLabel, QHBoxLayout]:
        btn_prev = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip='이전 페이지')
        btn_prev.setIcon(page.style().standardIcon(QStyle.SP_ArrowBack))
        btn_next = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip='다음 페이지')
        btn_next.setIcon(page.style().standardIcon(QStyle.SP_ArrowForward))

        indicator = QLabel('1 / 2', page)
        indicator.setObjectName('workOrderDiaryIndicator')
        indicator.setAlignment(Qt.AlignCenter)
        indicator.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout()
        row.setContentsMargins(0, 8, 0, 0)
        row.setSpacing(THEME.row_spacing)
        row.addStretch(1)
        row.addWidget(btn_prev, 0, Qt.AlignVCenter)
        row.addWidget(indicator, 0, Qt.AlignVCenter)
        row.addWidget(btn_next, 0, Qt.AlignVCenter)
        row.addStretch(1)
        return btn_prev, btn_next, indicator, row

    @staticmethod
    def _build_toolbar_buttons(parent: QWidget, page: QWidget) -> dict[str, QPushButton]:
        btn_reset = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=Tooltips.RELOAD, font_px=THEME.reset_button_font_px)
        btn_reset.setIcon(standard_icon(parent, [QStyle.SP_BrowserReload]))

        btn_save = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=Tooltips.SAVE, font_px=THEME.save_button_font_px)
        btn_save.setIcon(make_save_icon(THEME.icon_size_md, THEME.color_icon))

        btn_load = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=Tooltips.LOAD)
        btn_load.setIcon(standard_icon(parent, [QStyle.SP_DialogOpenButton, QStyle.SP_DirOpenIcon, QStyle.SP_DriveHDIcon]))

        btn_upload = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=Tooltips.IMAGE_UPLOAD)
        btn_upload.setIcon(make_image_upload_icon(THEME.icon_size_md, THEME.color_icon))

        btn_delete_image = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=Tooltips.IMAGE_DELETE)
        btn_delete_image.setIcon(parent.style().standardIcon(QStyle.SP_TrashIcon))

        return {
            'btn_reset': btn_reset,
            'btn_save': btn_save,
            'btn_load': btn_load,
            'btn_upload': btn_upload,
            'btn_delete_image': btn_delete_image,
        }

    @staticmethod
    def _install_header_actions(header_refs: object, toolbar_buttons: dict[str, QPushButton], page: QWidget) -> None:
        action_layout = header_refs.action_layout
        if action_layout is None:
            return

        def _proxy_button(source: QPushButton, tooltip: str) -> QPushButton:
            proxy = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=tooltip)
            proxy.setIcon(source.icon())
            proxy.clicked.connect(source.click)
            return proxy

        for key, tip in (
            ('btn_save', Tooltips.SAVE),
            ('btn_load', Tooltips.LOAD),
            ('btn_reset', Tooltips.RELOAD),
        ):
            action_layout.addWidget(_proxy_button(toolbar_buttons[key], tip), 0, Qt.AlignTop)

        if header_refs.help_button is not None:
            action_layout.addWidget(header_refs.help_button, 0, Qt.AlignTop)

    @staticmethod
    def _build_image_toolbar(page: QWidget, toolbar_buttons: dict[str, QPushButton]) -> QWidget:
        image_toolbar, image_toolbar_layout = make_standard_toolbar_strip(page, object_name='workOrderToolbarPanel')
        image_toolbar.setMinimumHeight(THEME.work_order_toolbar_panel_min_height)
        image_toolbar.setMaximumHeight(THEME.work_order_toolbar_panel_min_height)
        image_toolbar_layout.setContentsMargins(
            THEME.work_order_toolbar_inner_padding,
            THEME.work_order_toolbar_inner_padding_y,
            THEME.work_order_toolbar_inner_padding,
            THEME.work_order_toolbar_inner_padding_y,
        )
        image_toolbar_layout.setAlignment(Qt.AlignVCenter)

        for key in ('btn_reset', 'btn_load', 'btn_save'):
            image_toolbar_layout.addWidget(toolbar_buttons[key], 0, Qt.AlignLeft)

        image_toolbar_layout.addStretch(1)

        for key in ('btn_upload', 'btn_delete_image'):
            image_toolbar_layout.addWidget(toolbar_buttons[key], 0, Qt.AlignRight)

        return image_toolbar

    @staticmethod
    def _build_image_page(page: QWidget, toolbar_buttons: dict[str, QPushButton]) -> tuple[ImagePreview, QWidget, QWidget]:
        image_toolbar = WorkOrderPageBuilder._build_image_toolbar(page, toolbar_buttons)
        image_preview = ImagePreview()
        image_preview.setMinimumHeight(THEME.work_order_image_preview_min_height)
        image_preview.setStyleSheet(image_preview_style())
        image_shell = make_image_shell(page, image_preview, margin=THEME.image_shell_margin)

        image_page = QWidget(page)
        image_page.setObjectName('workOrderDiaryImagePage')
        image_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(image_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(THEME.section_gap)
        layout.addWidget(image_toolbar, 0)
        layout.addWidget(image_shell, 1)
        return image_preview, image_shell, image_toolbar

    @staticmethod
    def _build_change_note_column(page: QWidget) -> tuple[ChangeNotePostIt, QWidget]:
        change_note_postit = ChangeNotePostIt()
        change_note_postit.set_embedded_mode(True)
        change_note_postit.setMinimumHeight(0)
        change_note_postit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        change_note_card = WorkOrderPageBuilder._build_section_card(SectionTitles.CHANGE_NOTE, change_note_postit, page, stretch=1)
        change_note_card.setMinimumWidth(280)
        change_note_card.setMaximumWidth(360)
        change_note_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return change_note_postit, change_note_card

    @staticmethod
    def _build_info_page(page: QWidget, postit_bar: PostItBar, change_note_wrap: QWidget) -> QWidget:
        info_page = QWidget(page)
        info_page.setObjectName('workOrderDiaryInfoPage')
        info_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root_layout = QVBoxLayout(info_page)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(10)

        body_row = make_standard_body_row()
        body_row.setSpacing(14)

        left_column = QWidget(info_page)
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        basic_card = WorkOrderPageBuilder._build_section_card(SectionTitles.BASIC_INFO, postit_bar.basic, left_column)
        partner_title = getattr(SectionTitles, 'OUTSOURCE_INFO', '외주정보')
        partner_card = WorkOrderPageBuilder._build_section_card(partner_title, postit_bar.partner, left_column)

        left_layout.addWidget(basic_card, 0)
        left_layout.addWidget(partner_card, 0)

        right_column = QWidget(info_page)
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(change_note_wrap, 1)

        left_column.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_column.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body_row.addWidget(left_column, 3)
        body_row.addWidget(right_column, 2)

        root_layout.addLayout(body_row, 1)
        return info_page

    @staticmethod
    def _update_pager_ui(page_stack: QStackedWidget, btn_prev: QPushButton, btn_next: QPushButton, indicator: QLabel) -> None:
        current = page_stack.currentIndex()
        total = page_stack.count()
        indicator.setText(f'{current + 1} / {total}')
        btn_prev.setEnabled(current > 0)
        btn_next.setEnabled(current < total - 1)


__all__ = ['WorkOrderPageBuilder', 'WorkOrderPageRefs']
