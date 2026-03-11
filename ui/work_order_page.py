from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QStyle, QVBoxLayout, QWidget

from ui.icon_factory import make_image_outline_icon, make_save_icon, standard_icon
from ui.image_preview import ImagePreview
from ui.postit_widgets import ChangeNotePostIt, PostItBar, SectionContainer, SectionTitleBadge
from ui.theme import THEME, image_preview_style
from ui.widget_factory import apply_icon_button_metrics


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
        page_layout.setContentsMargins(THEME.page_padding_x, THEME.page_padding_y, THEME.page_padding_x, THEME.page_padding_y)
        page_layout.setSpacing(THEME.block_spacing)

        btn_back = QPushButton('◀')
        apply_icon_button_metrics(btn_back, font_px=THEME.icon_button_font_px + 2, object_name='navButton', tooltip='뒤로가기')
        btn_reset = QPushButton('')
        apply_icon_button_metrics(btn_reset, font_px=THEME.reset_button_font_px, object_name='iconAction', tooltip='새로고침')
        btn_reset.setIcon(standard_icon(parent, [QStyle.SP_BrowserReload, QStyle.SP_FileDialogDetailedView]))
        btn_reset.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        btn_save = QPushButton('')
        apply_icon_button_metrics(btn_save, font_px=THEME.save_button_font_px, object_name='iconPrimary', tooltip='저장')
        save_icon = standard_icon(parent, [QStyle.SP_DialogSaveButton], fallback=make_save_icon(THEME.icon_size_md, THEME.color_text_on_primary))
        btn_save.setIcon(save_icon)
        btn_save.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        btn_upload = QPushButton('')
        apply_icon_button_metrics(btn_upload, font_px=THEME.icon_button_font_px + 2, object_name='iconAction', tooltip='사진 업로드')
        btn_upload.setIcon(make_image_outline_icon(THEME.icon_size_md))
        btn_upload.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        btn_delete_image = QPushButton('')
        apply_icon_button_metrics(btn_delete_image, font_px=THEME.icon_button_font_px + 2, object_name='iconDanger', tooltip='사진 삭제')
        delete_icon = parent.style().standardIcon(QStyle.SP_TrashIcon)
        if delete_icon.isNull():
            delete_icon = parent.style().standardIcon(QStyle.SP_DialogDiscardButton)
        btn_delete_image.setIcon(delete_icon)
        btn_delete_image.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        btn_delete_image.setEnabled(False)

        left_controls = QWidget()
        left_controls_layout = QHBoxLayout(left_controls)
        left_controls_layout.setContentsMargins(0, 0, 0, 0)
        left_controls_layout.setSpacing(THEME.top_button_spacing)
        left_controls_layout.addWidget(btn_back)
        left_controls_layout.addWidget(btn_reset)
        left_controls_layout.addWidget(btn_save)
        left_controls_layout.addStretch(1)

        image_controls = QWidget()
        image_controls_layout = QHBoxLayout(image_controls)
        image_controls_layout.setContentsMargins(0, 0, 0, 0)
        image_controls_layout.setSpacing(THEME.top_button_spacing)
        image_controls_layout.addStretch(1)
        image_controls_layout.addWidget(btn_upload)
        image_controls_layout.addWidget(btn_delete_image)

        feedback_label = QLabel('', parent)
        feedback_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        feedback_label.setMinimumHeight(THEME.feedback_label_height)
        feedback_label.setMaximumHeight(THEME.feedback_label_height)
        feedback_label.setStyleSheet(
            f'QLabel{{background:transparent;border:none;padding:0 {THEME.label_padding_x}px;color:{THEME.color_text};font-weight:700;}}'
        )

        image_preview = ImagePreview()
        image_preview.setMinimumHeight(THEME.image_preview_min_height)
        image_preview.setStyleSheet(image_preview_style())
        image_shell = QWidget()
        image_shell.setObjectName('imageShell')
        image_shell_layout = QVBoxLayout(image_shell)
        image_shell_layout.setContentsMargins(
            THEME.image_shell_margin,
            THEME.image_shell_margin,
            THEME.image_shell_margin,
            THEME.image_shell_margin,
        )
        image_shell_layout.setSpacing(0)
        image_shell_layout.addWidget(image_preview)

        change_note_postit = ChangeNotePostIt()
        change_note_title = SectionTitleBadge('메모', parent, color=THEME.color_change_title, border_color=THEME.color_change_border)
        change_note_wrap = SectionContainer(change_note_title, change_note_postit, spacing=THEME.top_button_spacing)

        top_row = QWidget()
        top_layout = QGridLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setHorizontalSpacing(THEME.section_gap)
        top_layout.setVerticalSpacing(THEME.row_spacing)
        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 1)
        top_layout.addWidget(left_controls, 0, 0, 1, 1)
        top_layout.addWidget(image_controls, 0, 1, 1, 1)
        top_layout.addWidget(image_shell, 1, 0, 1, 2)

        postit_bar = PostItBar()

        page_layout.addWidget(top_row, 2)
        page_layout.addWidget(postit_bar, 0)
        page_layout.addWidget(change_note_wrap, 1)
        page_layout.addWidget(feedback_label, 0)

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
