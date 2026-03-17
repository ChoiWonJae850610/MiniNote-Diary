from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget

from ui.icon_factory import make_image_outline_icon, make_save_icon, standard_icon
from ui.image_preview import ImagePreview
from ui.messages import PageTitles, SectionTitles, Tooltips
from ui.pages.common import make_image_shell, make_standard_body_row, make_standard_feedback_label, make_standard_page_header, make_standard_page_layout, make_standard_toolbar_strip
from ui.postit import ChangeNotePostIt, PostItBar
from ui.postit.layout import (
    POSTIT_BODY_HEIGHT,
    POSTIT_EXTERNAL_ROW_GAP_TIGHT,
    POSTIT_FOOTER_HEIGHT,
    make_postit_footer_spacer,
    make_static_postit_column,
    postit_column_height,
)
from ui.theme import THEME, image_preview_style
from ui.widget_factory import make_toolbar_icon_button


@dataclass
class WorkOrderPageRefs:
    page: QWidget
    btn_back: QPushButton
    btn_reset: QPushButton
    btn_save: QPushButton
    btn_load: QPushButton
    btn_upload: QPushButton
    btn_delete_image: QPushButton
    feedback_label: QLabel
    image_preview: ImagePreview
    image_shell: QWidget
    change_note_postit: ChangeNotePostIt
    postit_bar: PostItBar


class WorkOrderPageBuilder:
    @staticmethod
    def build(parent: QWidget) -> WorkOrderPageRefs:
        page = QWidget()
        page_layout = make_standard_page_layout(page)
        page_layout.setContentsMargins(THEME.page_padding_x, THEME.page_header_top_margin, THEME.page_padding_x, THEME.page_top_bottom)
        page_layout.setSpacing(max(THEME.row_spacing, THEME.section_gap - 6))

        header_refs = make_standard_page_header(
            page,
            title_text=PageTitles.WORK_ORDER,
            subtitle_text='',
        )

        toolbar_buttons = WorkOrderPageBuilder._build_toolbar_buttons(parent, page)
        feedback_label = make_standard_feedback_label(page)
        feedback_label.setMinimumHeight(0)
        feedback_label.setMaximumHeight(THEME.feedback_label_height)
        feedback_label.hide()

        postit_bar = PostItBar()
        image_preview, image_shell, image_toolbar, left_stack = WorkOrderPageBuilder._build_image_column(page, toolbar_buttons)
        change_note_postit, change_note_wrap = WorkOrderPageBuilder._build_change_note_column(
            page,
            image_toolbar=image_toolbar,
            image_shell=image_shell,
            postit_bar=postit_bar,
        )

        right_stack = WorkOrderPageBuilder._build_postit_stack(postit_bar, change_note_wrap)
        left_stack.setMinimumWidth(THEME.work_order_left_column_min_width)
        left_stack.setMaximumWidth(THEME.work_order_left_column_max_width)
        right_stack.setMinimumWidth(THEME.work_order_right_column_min_width)

        content_row = make_standard_body_row()
        content_row.addWidget(left_stack, THEME.work_order_left_stretch)
        content_row.addWidget(right_stack, THEME.work_order_right_stretch)

        page_layout.addLayout(header_refs.row)
        page_layout.addWidget(feedback_label)
        page_layout.addLayout(content_row, 1)

        return WorkOrderPageRefs(
            page=page,
            btn_back=header_refs.back_button,
            btn_reset=toolbar_buttons['btn_reset'],
            btn_save=toolbar_buttons['btn_save'],
            btn_load=toolbar_buttons['btn_load'],
            btn_upload=toolbar_buttons['btn_upload'],
            btn_delete_image=toolbar_buttons['btn_delete_image'],
            feedback_label=feedback_label,
            image_preview=image_preview,
            image_shell=image_shell,
            change_note_postit=change_note_postit,
            postit_bar=postit_bar,
        )

    @staticmethod
    def _build_toolbar_buttons(parent: QWidget, page: QWidget) -> dict[str, QPushButton]:
        btn_reset = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=Tooltips.RELOAD, font_px=THEME.reset_button_font_px)
        btn_reset.setIcon(standard_icon(parent, [QStyle.SP_BrowserReload]))

        btn_save = make_toolbar_icon_button(parent=page, object_name='iconPrimary', tooltip=Tooltips.SAVE, font_px=THEME.save_button_font_px)
        btn_save.setIcon(make_save_icon(THEME.icon_size_md, THEME.color_text_on_primary))

        btn_load = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=Tooltips.LOAD)
        btn_load.setIcon(standard_icon(parent, [QStyle.SP_DialogOpenButton, QStyle.SP_DirOpenIcon, QStyle.SP_DriveHDIcon]))

        btn_upload = make_toolbar_icon_button(parent=page, object_name='iconAction', tooltip=Tooltips.IMAGE_UPLOAD)
        btn_upload.setIcon(make_image_outline_icon(THEME.icon_size_md))

        btn_delete_image = make_toolbar_icon_button(parent=page, object_name='iconDanger', tooltip=Tooltips.IMAGE_DELETE)
        btn_delete_image.setIcon(parent.style().standardIcon(QStyle.SP_TrashIcon))

        return {
            'btn_reset': btn_reset,
            'btn_save': btn_save,
            'btn_load': btn_load,
            'btn_upload': btn_upload,
            'btn_delete_image': btn_delete_image,
        }

    @staticmethod
    def _build_image_toolbar(page: QWidget, toolbar_buttons: dict[str, QPushButton]) -> QWidget:
        image_toolbar, image_toolbar_layout = make_standard_toolbar_strip(page, object_name='workOrderToolbarPanel')
        image_toolbar.setFixedHeight(THEME.work_order_toolbar_panel_min_height)
        image_toolbar_layout.setContentsMargins(
            THEME.work_order_toolbar_inner_padding,
            3,
            THEME.work_order_toolbar_inner_padding,
            3,
        )

        for key in ('btn_reset', 'btn_load', 'btn_save'):
            image_toolbar_layout.addWidget(toolbar_buttons[key], 0, Qt.AlignLeft)

        image_toolbar_layout.addStretch(1)

        for key in ('btn_upload', 'btn_delete_image'):
            image_toolbar_layout.addWidget(toolbar_buttons[key], 0, Qt.AlignRight)

        return image_toolbar

    @staticmethod
    def _build_image_column(page: QWidget, toolbar_buttons: dict[str, QPushButton]) -> tuple[ImagePreview, QWidget, QWidget, QWidget]:
        image_toolbar = WorkOrderPageBuilder._build_image_toolbar(page, toolbar_buttons)
        image_preview = ImagePreview()
        image_preview.setMinimumHeight(THEME.work_order_image_preview_min_height)
        image_preview.setStyleSheet(image_preview_style())
        image_shell = make_image_shell(page, image_preview, margin=THEME.image_shell_margin)

        left_stack = QWidget(page)
        left_stack.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left_stack)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(THEME.work_order_toolbar_to_image_gap)
        left_layout.addWidget(image_toolbar, 0)
        left_layout.addWidget(image_shell, 1)
        return image_preview, image_shell, image_toolbar, left_stack

    @staticmethod
    def _build_change_note_column(
        page: QWidget,
        *,
        image_toolbar: QWidget,
        image_shell: QWidget,
        postit_bar: QWidget,
    ) -> tuple[ChangeNotePostIt, QWidget]:
        change_note_body_height = WorkOrderPageBuilder._aligned_change_note_body_height(
            image_toolbar=image_toolbar,
            image_shell=image_shell,
            postit_bar=postit_bar,
        )
        change_note_postit = ChangeNotePostIt()
        change_note_postit.setFixedHeight(change_note_body_height)
        change_note_wrap = make_static_postit_column(
            SectionTitles.CHANGE_NOTE,
            change_note_postit,
            parent=page,
            body_height=change_note_body_height,
            footer_widget=make_postit_footer_spacer(page),
        )
        change_note_wrap.setMinimumWidth(THEME.work_order_change_note_min_width)
        return change_note_postit, change_note_wrap

    @staticmethod
    def _aligned_change_note_body_height(
        *,
        image_toolbar: QWidget,
        image_shell: QWidget,
        postit_bar: QWidget,
    ) -> int:
        target_change_note_wrap_height = WorkOrderPageBuilder._target_change_note_wrap_height(
            image_toolbar=image_toolbar,
            image_shell=image_shell,
            postit_bar=postit_bar,
        )
        wrap_overhead = postit_column_height(
            body_height=0,
            has_footer=True,
            external_row_gap=POSTIT_EXTERNAL_ROW_GAP_TIGHT,
            external_row_height=POSTIT_FOOTER_HEIGHT,
        )
        body_height = target_change_note_wrap_height - wrap_overhead
        return max(THEME.memo_min_height, THEME.work_order_change_note_body_min_height, body_height)

    @staticmethod
    def _target_change_note_wrap_height(
        *,
        image_toolbar: QWidget,
        image_shell: QWidget,
        postit_bar: QWidget,
    ) -> int:
        image_column_total_height = (
            THEME.work_order_toolbar_panel_min_height
            + THEME.work_order_toolbar_to_image_gap
            + (THEME.image_shell_margin * 2)
            + THEME.work_order_image_preview_min_height
            + image_shell.frameWidth() * 2
        )
        postit_bar_total_height = postit_column_height(
            body_height=POSTIT_BODY_HEIGHT,
            has_footer=True,
            external_row_gap=POSTIT_EXTERNAL_ROW_GAP_TIGHT,
            external_row_height=POSTIT_FOOTER_HEIGHT,
        )
        return max(
            THEME.memo_min_height,
            image_column_total_height
            - THEME.work_order_column_spacing
            - postit_bar_total_height
            - THEME.work_order_bottom_safe_reserve
            + THEME.work_order_bottom_match_adjust,
        )

    @staticmethod
    def _build_postit_stack(postit_bar: PostItBar, change_note_wrap: QWidget) -> QWidget:
        right_stack = QWidget()
        right_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_stack.setContentsMargins(0, 0, 0, 0)
        right_layout = QVBoxLayout(right_stack)
        right_layout.setContentsMargins(0, max(0, THEME.work_order_postit_top_offset - 2), 0, 0)
        right_layout.setSpacing(THEME.work_order_column_spacing)
        right_layout.addWidget(postit_bar, 0, Qt.AlignTop)
        right_layout.addWidget(change_note_wrap, 1)
        return right_stack


__all__ = ['WorkOrderPageBuilder', 'WorkOrderPageRefs']
