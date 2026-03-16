from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QStyle, QVBoxLayout, QWidget

from ui.icon_factory import make_image_outline_icon, make_save_icon, standard_icon
from ui.image_preview import ImagePreview
from ui.messages import PageDescriptions, PageTitles, SectionTitles, Tooltips
from ui.pages.common import make_image_shell, make_standard_page_header, make_standard_page_layout
from ui.postit import ChangeNotePostIt, PostItBar
from ui.postit.layout import (
    POSTIT_BODY_HEIGHT,
    POSTIT_EXTERNAL_ROW_GAP,
    POSTIT_FOOTER_HEIGHT,
    POSTIT_HEADER_HEIGHT,
    POSTIT_MEMO_BODY_HEIGHT,
    POSTIT_TAB_OVERLAP,
    make_postit_footer_spacer,
    make_static_postit_column,
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
        page_layout.setSpacing(THEME.block_spacing)

        header_refs = make_standard_page_header(
            page,
            title_text=PageTitles.WORK_ORDER,
            subtitle_text='',
        )

        toolbar_buttons = WorkOrderPageBuilder._build_toolbar_buttons(parent, page)
        feedback_label = QLabel('')
        feedback_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        feedback_label.setMinimumHeight(THEME.feedback_label_height)

        postit_bar = PostItBar()
        image_preview, image_shell, image_toolbar, left_stack = WorkOrderPageBuilder._build_image_column(page, toolbar_buttons)
        change_note_postit, change_note_wrap = WorkOrderPageBuilder._build_change_note_column(page)

        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setHorizontalSpacing(THEME.section_gap)
        content_layout.setVerticalSpacing(THEME.row_spacing)

        right_stack = WorkOrderPageBuilder._build_postit_stack(postit_bar, change_note_wrap)

        content_layout.addWidget(left_stack, 0, 0)
        content_layout.addWidget(right_stack, 0, 1)
        content_layout.setColumnStretch(0, 2)
        content_layout.setColumnStretch(1, 1)

        page_layout.addLayout(header_refs.row)
        page_layout.addWidget(content)
        page_layout.addWidget(feedback_label)

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
        image_toolbar = QWidget(page)
        image_toolbar_layout = QHBoxLayout(image_toolbar)
        image_toolbar_layout.setContentsMargins(0, 0, 0, 0)
        image_toolbar_layout.setSpacing(THEME.top_button_spacing)
        for key in ('btn_reset', 'btn_load', 'btn_save', 'btn_upload', 'btn_delete_image'):
            image_toolbar_layout.addWidget(toolbar_buttons[key])
        image_toolbar_layout.addStretch(1)
        return image_toolbar

    @staticmethod
    def _build_image_column(page: QWidget, toolbar_buttons: dict[str, QPushButton]) -> tuple[ImagePreview, QWidget, QWidget, QWidget]:
        image_toolbar = WorkOrderPageBuilder._build_image_toolbar(page, toolbar_buttons)
        image_preview = ImagePreview()
        image_preview.setMinimumHeight(THEME.image_preview_min_height)
        image_preview.setStyleSheet(image_preview_style())
        image_shell = make_image_shell(page, image_preview, margin=THEME.image_shell_margin)

        left_stack = QWidget(page)
        left_layout = QVBoxLayout(left_stack)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(THEME.row_spacing)
        left_layout.addWidget(image_toolbar, 0, Qt.AlignLeft)
        left_layout.addWidget(image_shell, 1)
        return image_preview, image_shell, image_toolbar, left_stack

    @staticmethod
    def _build_change_note_column(page: QWidget) -> tuple[ChangeNotePostIt, QWidget]:
        change_note_body_height = WorkOrderPageBuilder._aligned_change_note_body_height()
        change_note_postit = ChangeNotePostIt()
        change_note_postit.setFixedHeight(change_note_body_height)
        change_note_wrap = make_static_postit_column(
            SectionTitles.CHANGE_NOTE,
            change_note_postit,
            parent=page,
            body_height=change_note_body_height,
            footer_widget=make_postit_footer_spacer(page),
        )
        return change_note_postit, change_note_wrap

    @staticmethod
    def _aligned_change_note_body_height() -> int:
        image_column_height = (
            THEME.icon_button_size
            + THEME.row_spacing
            + (THEME.image_shell_margin * 2)
            + THEME.image_preview_min_height
        )

        # The upper post-it block visually ends at its visible pager row.
        # Reserve alignment height against that visible block so the memo area
        # reaches the same bottom line as the image shell.
        postit_bar_visual_height = (
            POSTIT_HEADER_HEIGHT
            + POSTIT_TAB_OVERLAP
            + POSTIT_BODY_HEIGHT
            + POSTIT_FOOTER_HEIGHT
        )

        change_note_fixed_overhead = (
            POSTIT_HEADER_HEIGHT
            + POSTIT_TAB_OVERLAP
            + THEME.top_button_spacing
            + POSTIT_FOOTER_HEIGHT
            + POSTIT_EXTERNAL_ROW_GAP
            + POSTIT_FOOTER_HEIGHT
        )
        aligned_height = image_column_height - postit_bar_visual_height - THEME.section_gap - change_note_fixed_overhead
        return max(180, min(POSTIT_MEMO_BODY_HEIGHT, aligned_height))

    @staticmethod
    def _build_postit_stack(postit_bar: PostItBar, change_note_wrap: QWidget) -> QWidget:
        right_stack = QWidget()
        right_layout = QVBoxLayout(right_stack)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(THEME.section_gap)
        right_layout.addWidget(postit_bar, 0, Qt.AlignTop)
        right_layout.addWidget(change_note_wrap, 0, Qt.AlignTop)
        right_layout.addStretch(1)
        return right_stack


__all__ = ['WorkOrderPageBuilder', 'WorkOrderPageRefs']
