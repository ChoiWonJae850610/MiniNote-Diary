from __future__ import annotations

import shutil
import webbrowser
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ui.dialogs import show_error, show_info
from ui.dialogs.base import _BaseThemedDialog
from ui.messages import Buttons, DialogTitles, InfoMessages
from ui.theme import THEME
from ui.widget_factory import apply_button_metrics, make_action_button
from ui.widget_factory_buttons import make_dialog_button


class SettingsDialog(_BaseThemedDialog):
    def __init__(self, parent=None):
        super().__init__(title=DialogTitles.SETTINGS, parent=parent)
        self.setMinimumWidth(max(self.minimumWidth(), 560))
        self.body.setSpacing(THEME.section_gap)

        self.body.addWidget(self._build_section(
            '관리',
            (
                ('거래처 관리', self._open_partner_management),
                ('단위 관리', self._open_unit_management),
                ('제품 타입 관리', self._open_product_type_management),
                ('모든 데이터 초기화', self._reset_all_data),
            ),
        ))
        self.body.addWidget(self._build_section(
            '지원',
            (
                ('도움말', self._show_help),
                ('백업하기', self._backup_project_data),
                ('테마 변경', self._show_theme_change_info),
                ('문의하기', self._contact_creator),
            ),
        ))

        close_row = QHBoxLayout()
        close_row.addStretch(1)
        btn_close = make_dialog_button(Buttons.CLOSE, self.card, role='close')
        btn_close.clicked.connect(self.reject)
        close_row.addWidget(btn_close)
        close_row.addStretch(1)
        self.body.addLayout(close_row)

    def _build_section(self, title: str, actions: tuple[tuple[str, object], ...]) -> QFrame:
        panel = QFrame(self.card)
        panel.setObjectName('dialogCard')
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel(title, panel)
        title_label.setObjectName('dialogTitle')
        title_label.show()
        layout.addWidget(title_label)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        for index, (text, callback) in enumerate(actions):
            button = make_action_button(text, panel, width=190, height=THEME.dialog_button_height + 6)
            apply_button_metrics(button, width=190, height=THEME.dialog_button_height + 6, font_px=THEME.base_font_px)
            button.clicked.connect(callback)
            grid.addWidget(button, index // 2, index % 2)
        layout.addLayout(grid)
        return panel

    def _run_window_action(self, method_name: str) -> None:
        parent = self.parent()
        if parent is None or not hasattr(parent, method_name):
            return
        self.reject()
        getattr(parent, method_name)()

    def _open_partner_management(self) -> None:
        self._run_window_action('on_partner_mgmt_clicked')

    def _open_unit_management(self) -> None:
        self._run_window_action('on_unit_mgmt_clicked')

    def _open_product_type_management(self) -> None:
        self._run_window_action('on_product_type_mgmt_clicked')

    def _reset_all_data(self) -> None:
        self._run_window_action('on_data_reset_clicked')

    def _show_help(self) -> None:
        show_info(
            self,
            DialogTitles.HELP,
            '작업지시서 작성 화면에서 저장/불러오기/이미지 첨부를 사용할 수 있습니다.\n\n'
            '관리 기능은 환경설정 안에서 열 수 있습니다.\n'
            '초기화는 모든 데이터를 삭제하므로 주의해서 사용하세요.',
        )

    def _backup_project_data(self) -> None:
        parent = self.parent()
        project_root = Path(getattr(parent, 'project_root', Path.cwd()))
        db_dir = project_root / 'db'
        if not db_dir.exists():
            show_error(self, DialogTitles.ERROR, '백업할 DB 폴더를 찾을 수 없습니다.')
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f'mininote_backup_{timestamp}.zip'
        target_path, _ = QFileDialog.getSaveFileName(self, DialogTitles.BACKUP, str(project_root / default_name), 'ZIP (*.zip)')
        if not target_path:
            return
        target = Path(target_path)
        archive_base = target.with_suffix('')
        try:
            created = Path(shutil.make_archive(str(archive_base), 'zip', root_dir=db_dir, base_dir='.'))
            if created != target:
                if target.exists():
                    target.unlink()
                created.replace(target)
        except Exception as exc:
            show_error(self, DialogTitles.ERROR, f'백업 파일을 만들지 못했습니다.\n\n{exc}')
            return
        show_info(self, DialogTitles.BACKUP, InfoMessages.BACKUP_DONE.format(path=str(target)))

    def _show_theme_change_info(self) -> None:
        show_info(self, DialogTitles.THEME_CHANGE, InfoMessages.THEME_CHANGE_PENDING)

    def _contact_creator(self) -> None:
        parent = self.parent()
        email = str(getattr(parent, 'support_email', '')) or 'support@example.com'
        try:
            webbrowser.open(f'mailto:{email}?subject=MiniNote%20Diary%20문의')
        except Exception:
            pass
        show_info(self, DialogTitles.CONTACT, InfoMessages.CONTACT_GUIDE.format(email=email))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)
