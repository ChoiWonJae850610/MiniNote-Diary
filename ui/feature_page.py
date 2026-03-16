from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from ui.messages import Buttons
from ui.pages.common import make_standard_page_header, make_standard_page_layout, make_titled_panel
from ui.theme import THEME
from ui.widget_factory import make_action_button, make_hint_label, make_meta_label, make_section_title_label


@dataclass(frozen=True)
class FeatureSection:
    title: str
    lines: Sequence[str]


@dataclass(frozen=True)
class FeaturePageConfig:
    key: str
    title: str
    subtitle: str
    left_title: str
    left_hint: str
    list_items: Sequence[str]
    summary_items: Sequence[str]
    sections: Sequence[FeatureSection]
    primary_button_text: str
    secondary_button_text: str = Buttons.SAVE
    helper_text: str = ''


@dataclass
class FeaturePageRefs:
    page: QWidget
    btn_back: QPushButton
    btn_primary: QPushButton
    btn_secondary: QPushButton
    item_list: QListWidget


class _SectionCard(QFrame):
    def __init__(self, title: str, lines: Sequence[str], parent=None):
        super().__init__(parent)
        self.setObjectName('featureCard')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding_compact, THEME.page_section_padding, THEME.page_section_padding_compact)
        layout.setSpacing(THEME.card_inner_spacing)

        title_label = make_section_title_label(title, self)
        title_label.setObjectName('featureSectionTitle')
        layout.addWidget(title_label)

        for line in lines:
            line_label = make_meta_label(f'• {line}', self)
            line_label.setObjectName('featureLine')
            layout.addWidget(line_label)


class FeaturePageBuilder:
    @staticmethod
    def build(config: FeaturePageConfig) -> FeaturePageRefs:
        page = QWidget()
        page.setObjectName('featurePage')
        root = make_standard_page_layout(page)

        header_refs = make_standard_page_header(
            page,
            title_text=config.title,
            subtitle_text=config.subtitle,
            title_object_name='featureTitle',
            subtitle_object_name='featureSubtitle',
        )
        root.addLayout(header_refs.row)

        summary_grid = QGridLayout()
        summary_grid.setHorizontalSpacing(THEME.row_spacing)
        summary_grid.setVerticalSpacing(THEME.row_spacing)
        for index, text in enumerate(config.summary_items):
            chip = QLabel(text, page)
            chip.setObjectName('summaryChip')
            chip.setAlignment(Qt.AlignCenter)
            summary_grid.addWidget(chip, index // 3, index % 3)
        root.addLayout(summary_grid)

        content_row = QHBoxLayout()
        content_row.setSpacing(THEME.section_gap)

        left_panel, left_layout = make_titled_panel(
            page,
            title_text=config.left_title,
            hint_text=config.left_hint,
            title_object_name='featurePanelTitle',
            hint_object_name='featureHint',
        )
        left_panel.setObjectName('featurePanel')
        item_list = QListWidget(left_panel)
        item_list.setObjectName('featureList')
        for item_text in config.list_items:
            QListWidgetItem(item_text, item_list)
        if item_list.count() > 0:
            item_list.setCurrentRow(0)
        left_layout.addWidget(item_list, 1)

        right_panel = QFrame(page)
        right_panel.setObjectName('featurePanel')
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        right_layout.setSpacing(THEME.section_gap)
        for section in config.sections:
            right_layout.addWidget(_SectionCard(section.title, section.lines, right_panel))
        right_layout.addStretch(1)

        content_row.addWidget(left_panel, 4)
        content_row.addWidget(right_panel, 6)
        root.addLayout(content_row, 1)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(THEME.row_spacing)
        helper = make_hint_label(config.helper_text, page)
        helper.setObjectName('featureHint')
        btn_secondary = make_action_button(config.secondary_button_text, page, width=THEME.secondary_button_width, height=THEME.primary_button_height)
        btn_primary = make_action_button(config.primary_button_text, page, primary=True, width=THEME.primary_button_width, height=THEME.primary_button_height)
        bottom_row.addWidget(helper, 1)
        bottom_row.addWidget(btn_secondary)
        bottom_row.addWidget(btn_primary)
        root.addLayout(bottom_row)

        return FeaturePageRefs(page=page, btn_back=header_refs.back_button, btn_primary=btn_primary, btn_secondary=btn_secondary, item_list=item_list)
