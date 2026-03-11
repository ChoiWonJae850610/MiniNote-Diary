
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QStyle, QVBoxLayout, QWidget

from ui.icon_factory import make_image_outline_icon, make_save_icon, standard_icon
from ui.image_preview import ImagePreview
from ui.postit_widgets import ChangeNotePostIt, FolderTabHeader, PostItBar, SectionContainer
from ui.theme import THEME, image_preview_style
from ui.widget_factory import apply_icon_button_metrics, make_hint_label, make_page_title_label


@dataclass
class WorkOrderPageRefs:
    page: QWidget
    btn_back: QPushButton
    btn_reset: QPushButton
    btn_save: QPushButton
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

        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(
            THEME.page_padding_x,
            THEME.page_padding_y,
            THEME.page_padding_x,
            THEME.page_padding_y,
        )
        page_layout.setSpacing(THEME.block_spacing)

        btn_back = QPushButton("◀")
        apply_icon_button_metrics(btn_back, font_px=THEME.icon_button_font_px + 2, object_name="navButton", tooltip="뒤로가기")

        btn_reset = QPushButton("")
        apply_icon_button_metrics(btn_reset, font_px=THEME.reset_button_font_px, object_name="iconAction", tooltip="새로고침")
        btn_reset.setIcon(standard_icon(parent, [QStyle.SP_BrowserReload]))

        btn_save = QPushButton("")
        apply_icon_button_metrics(btn_save, font_px=THEME.save_button_font_px, object_name="iconPrimary", tooltip="저장")
        btn_save.setIcon(make_save_icon(THEME.icon_size_md, THEME.color_text_on_primary))

        btn_upload = QPushButton("")
        apply_icon_button_metrics(btn_upload, font_px=THEME.icon_button_font_px, object_name="iconAction", tooltip="사진 업로드")
        btn_upload.setIcon(make_image_outline_icon(THEME.icon_size_md))

        btn_delete_image = QPushButton("")
        apply_icon_button_metrics(btn_delete_image, font_px=THEME.icon_button_font_px, object_name="iconDanger", tooltip="사진 삭제")
        btn_delete_image.setIcon(parent.style().standardIcon(QStyle.SP_TrashIcon))

        top_row = QHBoxLayout()
        top_row.setSpacing(THEME.top_button_spacing)

        title_col = QVBoxLayout()
        title_col.setSpacing(THEME.title_stack_spacing)
        title = make_page_title_label('작업지시서 생성', page)
        subtitle = make_hint_label('작업지시서 내용을 입력하고 이미지, 자재, 메모를 함께 관리합니다.', page)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        top_row.addWidget(btn_back, 0, Qt.AlignTop)
        top_row.addLayout(title_col, 1)
        top_row.addStretch(1)
        top_row.addWidget(btn_reset, 0, Qt.AlignTop)
        top_row.addWidget(btn_save, 0, Qt.AlignTop)
        top_row.addWidget(btn_upload, 0, Qt.AlignTop)
        top_row.addWidget(btn_delete_image, 0, Qt.AlignTop)

        feedback_label = QLabel("")
        feedback_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        feedback_label.setMinimumHeight(THEME.feedback_label_height)

        image_preview = ImagePreview()
        image_preview.setMinimumHeight(THEME.image_preview_min_height)
        image_preview.setStyleSheet(image_preview_style())

        image_shell = QWidget()
        image_layout = QVBoxLayout(image_shell)
        image_layout.setContentsMargins(THEME.image_shell_margin, THEME.image_shell_margin, THEME.image_shell_margin, THEME.image_shell_margin)
        image_layout.addWidget(image_preview)

        postit_bar = PostItBar()

        change_note_postit = ChangeNotePostIt()
        change_note_title = FolderTabHeader('메모', page)
        change_note_wrap = SectionContainer(change_note_title, change_note_postit, spacing=0, header_alignment=None)

        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setHorizontalSpacing(THEME.section_gap)
        content_layout.setVerticalSpacing(THEME.row_spacing)

        right_stack = QWidget()
        right_layout = QVBoxLayout(right_stack)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(THEME.section_gap)

        right_layout.addWidget(postit_bar)
        right_layout.addWidget(change_note_wrap)

        content_layout.addWidget(image_shell, 0, 0)
        content_layout.addWidget(right_stack, 0, 1)

        content_layout.setColumnStretch(0, 2)
        content_layout.setColumnStretch(1, 1)

        page_layout.addLayout(top_row)
        page_layout.addWidget(content)
        page_layout.addWidget(feedback_label)

        return WorkOrderPageRefs(
            page=page,
            btn_back=btn_back,
            btn_reset=btn_reset,
            btn_save=btn_save,
            btn_upload=btn_upload,
            btn_delete_image=btn_delete_image,
            feedback_label=feedback_label,
            image_preview=image_preview,
            image_shell=image_shell,
            change_note_postit=change_note_postit,
            postit_bar=postit_bar,
        )
