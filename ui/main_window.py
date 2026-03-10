import os

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QStackedWidget,
    QTextEdit,
    QWidget,
    QVBoxLayout,
    QDialog,
)

from services.schema import DEFAULT_FEEDBACK_TIMEOUT_MS, SUPPORTED_IMAGE_FILTER
from services.work_order_controller import WorkOrderController
from services.work_order_state import WorkOrderState
from ui.basic_info_dialog import BasicInfoDialog
from ui.dialogs import ConfirmActionDialog, ValidationStatusDialog, show_error, show_info
from ui.feature_page import FeaturePageBuilder, FeaturePageConfig, FeatureSection
from ui.menu_page import MenuPageBuilder
from ui.theme import THEME, build_app_stylesheet
from ui.unit_dialog import UnitDialog
from ui.partner_dialog import PartnerDialog
from ui.work_order_page import WorkOrderPageBuilder


class MainWindow(QMainWindow):
    PAGE_MENU = 0
    PAGE_WORK_ORDER = 1
    PAGE_JOB_START = 2
    PAGE_RECEIPT = 3
    PAGE_COMPLETE = 4
    PAGE_SALE = 5
    PAGE_INVENTORY = 6
    PAGE_PARTNER = 7

    def __init__(self):
        super().__init__()
        self.setWindowTitle('미니노트 다이어리')
        self.menuBar().hide()

        self.project_root = self._project_root()
        self.state = WorkOrderState()
        self.controller = WorkOrderController(self.state, self.project_root)
        self._suppress_dirty = False
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self._clear_feedback)

        self._build_root()
        self._build_pages()
        self._bind_page_events()
        self._apply_window_defaults()

    @staticmethod
    def _project_root() -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    @property
    def is_dirty(self) -> bool:
        return self.state.is_dirty

    def _build_root(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)

    def _build_pages(self) -> None:
        menu_refs = MenuPageBuilder.build()
        work_refs = WorkOrderPageBuilder.build(self)
        feature_pages = self._build_feature_pages()

        self.page_menu = menu_refs.page
        self.page_work_order = work_refs.page
        self.page_job_start = feature_pages['job_start'].page
        self.page_receipt = feature_pages['receipt'].page
        self.page_complete = feature_pages['complete'].page
        self.page_sale = feature_pages['sale'].page
        self.page_inventory = feature_pages['inventory'].page
        self.page_partner = feature_pages['partner'].page

        self.btn_template = menu_refs.btn_template
        self.btn_job_start_menu = menu_refs.btn_job_start
        self.btn_receipt_menu = menu_refs.btn_receipt
        self.btn_complete_menu = menu_refs.btn_complete
        self.btn_sale_menu = menu_refs.btn_sale
        self.btn_inventory_menu = menu_refs.btn_inventory
        self.btn_partner_mgmt = menu_refs.btn_partner_mgmt
        self.btn_unit_mgmt = menu_refs.btn_unit_mgmt

        self.btn_back = work_refs.btn_back
        self.btn_reset = work_refs.btn_reset
        self.btn_save = work_refs.btn_save
        self.btn_upload = work_refs.btn_upload
        self.btn_delete_image = work_refs.btn_delete_image
        self.feedback_label = work_refs.feedback_label
        self.image_preview = work_refs.image_preview
        self.change_note_postit = work_refs.change_note_postit
        self.postit_bar = work_refs.postit_bar

        self.feature_pages = feature_pages

        self.stack.addWidget(self.page_menu)
        self.stack.addWidget(self.page_work_order)
        self.stack.addWidget(self.page_job_start)
        self.stack.addWidget(self.page_receipt)
        self.stack.addWidget(self.page_complete)
        self.stack.addWidget(self.page_sale)
        self.stack.addWidget(self.page_inventory)
        self.stack.addWidget(self.page_partner)
        self.stack.setCurrentIndex(self.PAGE_MENU)

    def _bind_page_events(self) -> None:
        self.btn_template.clicked.connect(self.go_work_order)
        self.btn_job_start_menu.clicked.connect(lambda: self.open_feature_page(self.PAGE_JOB_START))
        self.btn_receipt_menu.clicked.connect(lambda: self.open_feature_page(self.PAGE_RECEIPT))
        self.btn_complete_menu.clicked.connect(lambda: self.open_feature_page(self.PAGE_COMPLETE))
        self.btn_sale_menu.clicked.connect(lambda: self.open_feature_page(self.PAGE_SALE))
        self.btn_inventory_menu.clicked.connect(lambda: self.open_feature_page(self.PAGE_INVENTORY))
        self.btn_partner_mgmt.clicked.connect(self.on_partner_mgmt_clicked)
        self.btn_unit_mgmt.clicked.connect(self.on_unit_mgmt_clicked)

        for refs in self.feature_pages.values():
            refs.btn_back.clicked.connect(self.go_menu)
            refs.btn_primary.clicked.connect(lambda _=False, page=refs.page: self.on_feature_primary(page))
            refs.btn_secondary.clicked.connect(lambda _=False, page=refs.page: self.on_feature_secondary(page))

        self.btn_back.clicked.connect(self.on_back_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_delete_image.clicked.connect(self.delete_image)

        self.change_note_postit.text_changed.connect(self.on_change_note_changed)
        self.postit_bar.fabric_deleted.connect(self.on_fabric_deleted)
        self.postit_bar.trim_deleted.connect(self.on_trim_deleted)
        self.postit_bar.fabric_item_changed.connect(self.on_fabric_postit_changed)
        self.postit_bar.trim_item_changed.connect(self.on_trim_postit_changed)
        self.postit_bar.fabric_item_added.connect(self.on_add_fabric_clicked)
        self.postit_bar.trim_item_added.connect(self.on_add_trim_clicked)
        self.postit_bar.basic_data_changed.connect(self.on_basic_postit_changed)

    def _apply_window_defaults(self) -> None:
        self.setMinimumSize(THEME.window_min_width, THEME.window_min_height)
        self.resize(THEME.window_min_width, THEME.window_min_height)
        self.setStyleSheet(build_app_stylesheet())
        self._install_global_focus_clear()
        self._install_shortcuts()
        self._refresh_postits(force_rebuild=True)
        self._update_window_title()

    def _install_global_focus_clear(self):
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _install_shortcuts(self):
        self.save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.save_shortcut.activated.connect(self._handle_save_shortcut)

    def _handle_save_shortcut(self):
        if self.stack.currentIndex() == self.PAGE_WORK_ORDER:
            self.on_save_clicked()

    def _is_text_input_widget(self, widget) -> bool:
        return isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QAbstractSpinBox))

    def _has_input_ancestor(self, widget) -> bool:
        current = widget
        while current is not None:
            if self._is_text_input_widget(current):
                return True
            current = current.parentWidget()
        return False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            focused = QApplication.focusWidget()
            target = obj if isinstance(obj, QWidget) else None
            if focused is not None and target is not None and self._is_text_input_widget(focused):
                if target is not focused and not focused.isAncestorOf(target) and not self._has_input_ancestor(target):
                    focused.clearFocus()
        return super().eventFilter(obj, event)


    def on_partner_mgmt_clicked(self):
        dlg = PartnerDialog(project_root=self.project_root, parent=self)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.exec()

    def on_unit_mgmt_clicked(self):
        dlg = UnitDialog(project_root=self.project_root, parent=self)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.exec()

    def _show_feedback(self, message: str, timeout_ms: int = DEFAULT_FEEDBACK_TIMEOUT_MS):
        self.feedback_label.setText(message)
        self._feedback_timer.start(timeout_ms)

    def _clear_feedback(self):
        self.feedback_label.clear()

    def _update_window_title(self):
        suffix = ' *' if self.state.is_dirty else ''
        self.setWindowTitle(f'미니노트 다이어리{suffix}')

    def _build_feature_pages(self) -> dict[str, object]:
        configs = [
            FeaturePageConfig(
                key='job_start',
                title='작업 시작',
                subtitle='기존 작업지시서를 선택하고 수량을 입력해 실제 생산 작업을 생성하는 화면 흐름입니다.',
                left_title='작업지시서 선택',
                left_hint='저장된 작업지시서 목록에서 기준 문서를 선택합니다.',
                list_items=['하늘색 저지 자켓', '테스트 원단 샘플', '기본 상의 템플릿'],
                summary_items=['선택한 작업지시서 미리보기', '생산 수량 입력', '시작 시점 지출 예정'],
                sections=[
                    FeatureSection('선택 정보 요약', ['대표 이미지 유무', '기본 거래처 / 스타일번호', '원단 · 부자재 카드 요약']),
                    FeatureSection('작업 생성 입력', ['생산 수량', '작업 시작일', '작업 메모 / 공장 메모']),
                    FeatureSection('향후 DB 포인트', ['template_id 참조', 'planned_qty 저장', '작업 시작 지출 이벤트 기록']),
                ],
                primary_button_text='작업 생성',
                secondary_button_text='선택 미리보기',
                helper_text='실제 연결 전 단계에서는 화면 흐름과 필요한 입력 묶음을 먼저 확인합니다.',
            ),
            FeaturePageConfig(
                key='receipt',
                title='원단 / 부자재 등록',
                subtitle='진행 중인 작업을 선택하고 영수증 이미지를 첨부한 뒤 실제 매입 내용을 입력하는 흐름입니다.',
                left_title='진행중 작업 선택',
                left_hint='이미 생성된 작업 중 지출을 등록할 대상을 선택합니다.',
                list_items=['JOB-0001 하늘색 저지 자켓', 'JOB-0002 테스트 원단 샘플'],
                summary_items=['영수증 이미지 첨부', '실제 원단 · 부자재 입력', '지출 금액 기록'],
                sections=[
                    FeatureSection('영수증 등록', ['이미지 파일 첨부', '거래처 선택 또는 입력', '등록 일자 / 메모']),
                    FeatureSection('자재 입력', ['원단 포스트잇 입력', '부자재 포스트잇 입력', '실제 단가 · 총액 반영']),
                    FeatureSection('향후 DB 포인트', ['job_id 연결', 'receipt_image_path 저장', 'expense transaction 생성']),
                ],
                primary_button_text='영수증 저장',
                secondary_button_text='이미지 첨부',
                helper_text='현재는 클릭 가능한 화면 뼈대만 배치했고, 실제 입력 위젯은 다음 단계에서 연결하면 됩니다.',
            ),
            FeaturePageConfig(
                key='complete',
                title='작업 완료',
                subtitle='작업 완료 처리 시 실제 완료 수량을 확정하고 재고 생성 흐름으로 연결하는 화면입니다.',
                left_title='완료 대상 작업',
                left_hint='진행 중 상태의 작업을 골라 완료 처리합니다.',
                list_items=['JOB-0001 하늘색 저지 자켓', 'JOB-0004 기본 상의 템플릿'],
                summary_items=['완료 수량 입력', '불량 / 누락 반영', '재고 생성'],
                sections=[
                    FeatureSection('완료 입력', ['완료 일자', '실제 완료 수량', '불량 / 추가 메모']),
                    FeatureSection('재고 반영', ['현재고 생성 또는 증가', '완료 후 작업 상태 변경', '필요 시 수량 조정 허용']),
                    FeatureSection('향후 DB 포인트', ['job status update', 'inventory movement create', 'completed_at 기록']),
                ],
                primary_button_text='작업 완료 처리',
                secondary_button_text='완료 전 검토',
                helper_text='재고는 별도 테이블보다 이동 이력 기반으로 보는 방향을 염두에 둔 화면입니다.',
            ),
            FeaturePageConfig(
                key='sale',
                title='판매 등록',
                subtitle='생성된 재고 중 판매 대상을 선택하고 수량과 금액을 기록하는 화면 흐름입니다.',
                left_title='판매 대상 선택',
                left_hint='현재고가 존재하는 품목을 기준으로 판매를 기록합니다.',
                list_items=['하늘색 저지 자켓 / 현재고 12', '기본 상의 템플릿 / 현재고 4'],
                summary_items=['판매 수량 입력', '판매 금액 기록', '재고 차감'],
                sections=[
                    FeatureSection('판매 입력', ['판매일', '판매 수량', '판매 단가 / 총액']),
                    FeatureSection('재고 / 수입 반영', ['판매 후 재고 차감', '수입 거래 생성', '필요 시 메모 기록']),
                    FeatureSection('향후 DB 포인트', ['inventory decrease', 'sale row create', 'income transaction 생성']),
                ],
                primary_button_text='판매 저장',
                secondary_button_text='판매 미리보기',
                helper_text='판매 화면은 재고 조회 화면과 연결되는 구조가 자연스럽습니다.',
            ),
            FeaturePageConfig(
                key='inventory',
                title='재고 / 통계',
                subtitle='현재고, 진행중 작업 수, 월별 지출/수입 흐름을 한 번에 보는 대시보드 방향의 화면입니다.',
                left_title='조회 기준',
                left_hint='제품별 / 거래처별 / 기간별 조회가 들어갈 자리를 먼저 잡아둡니다.',
                list_items=['현재고 보기', '월별 지출 흐름', '거래처별 지출 비교', '작업 진행 상태'],
                summary_items=['현재고 확인', '월별 지출 · 수입', '거래처별 통계'],
                sections=[
                    FeatureSection('대시보드 카드', ['진행중 작업 수', '완료 작업 수', '재고 합계 / 품목 수']),
                    FeatureSection('그래프 영역 후보', ['월별 지출 추이', '월별 수입 추이', '거래처별 원가 비교']),
                    FeatureSection('향후 DB 포인트', ['financial transaction 집계', 'inventory movement 집계', '기간 필터 query']),
                ],
                primary_button_text='조회 새로고침',
                secondary_button_text='필터 열기',
                helper_text='이 화면은 SQLite 전환 후 repository / stats service가 준비되면 실제 데이터와 바로 연결할 수 있습니다.',
            ),
            FeaturePageConfig(
                key='partner',
                title='거래처 관리',
                subtitle='거래처 정보와 역할 타입을 관리하는 화면 구조입니다. 실제 원단처/부자재처/공장 구분을 여기서 정리합니다.',
                left_title='거래처 목록',
                left_hint='상호명 중심으로 조회하고 상세 정보는 우측에서 편집하는 구성을 상정합니다.',
                list_items=['민트 봉제공장', '샘플 원단상사', '테스트 부자재', 'OO염색'],
                summary_items=['거래처 기본정보', '타입 다중 선택', '주소 / 연락처 관리'],
                sections=[
                    FeatureSection('기본 정보', ['상호명', '사장명 / 연락처', '주소 / 메모']),
                    FeatureSection('타입 관리', ['봉제공장', '원단처', '부자재처', '염색 / 마감 / 기사 / 기타']),
                    FeatureSection('향후 DB 포인트', ['partner master', 'partner type link', '거래 이력 연결']),
                ],
                primary_button_text='거래처 저장',
                secondary_button_text='타입 관리',
                helper_text='거래처 타입 추가 기능은 별도 작은 관리 팝업으로 분리하는 쪽이 유지보수에 유리합니다.',
            ),
        ]
        return {config.key: FeaturePageBuilder.build(config) for config in configs}

    def open_feature_page(self, page_index: int) -> None:
        self.stack.setCurrentIndex(page_index)

    def on_feature_primary(self, page: QWidget) -> None:
        if page is self.page_partner:
            show_info(self, '거래처 관리', '거래처 관리 편집 화면은 다음 단계에서 실제 입력 폼과 연결합니다.')
            return
        if page is self.page_inventory:
            show_info(self, '재고 / 통계', '통계 화면은 SQLite 전환 후 실제 집계 데이터와 연결합니다.')
            return
        show_info(self, '준비중', '이 화면은 UI 흐름 검토용으로 먼저 배치했습니다. 다음 단계에서 실제 입력/저장 로직을 연결합니다.')

    def on_feature_secondary(self, page: QWidget) -> None:
        if page is self.page_receipt:
            show_info(self, '영수증 등록', '이미지 첨부와 포스트잇 입력을 결합하는 방향으로 화면을 확장할 예정입니다.')
            return
        show_info(self, '화면 검토', '현재는 메뉴 구조와 화면 흐름을 먼저 확인하는 단계입니다.')

    def _focus_style_input(self):
        QTimer.singleShot(0, lambda: self.postit_bar.basic.style_no.activate_for_input())

    def go_work_order(self):
        self._refresh_postits(force_rebuild=True)
        self.stack.setCurrentIndex(self.PAGE_WORK_ORDER)
        self._focus_style_input()

    def go_menu(self):
        self.stack.setCurrentIndex(self.PAGE_MENU)

    def mark_dirty(self):
        if self._suppress_dirty:
            return
        self.state.mark_dirty()
        self._update_window_title()

    def has_any_data(self) -> bool:
        return self.state.has_any_data()

    def reset_work_order_form(self):
        self._suppress_dirty = True
        try:
            self.state.reset()
            self.image_preview.clear_image()
            self.btn_delete_image.setEnabled(False)
            self._refresh_postits(force_rebuild=True)
            self._clear_feedback()
            self._update_window_title()
        finally:
            self._suppress_dirty = False

    def _refresh_postits(self, force_rebuild: bool = False):
        self.postit_bar.set_data(
            header=self.state.header_data,
            fabrics=self.state.fabric_items,
            trims=self.state.trim_items,
            force_rebuild=force_rebuild,
        )
        self.change_note_postit.set_text(self.state.header.change_note)

    def on_add_basic_clicked(self):
        dlg = BasicInfoDialog(initial=self.state.header_data, parent=self)
        if dlg.exec() == dlg.Accepted:
            self.state.header_data = dlg.get_data()
            self.mark_dirty()
            self._refresh_postits(force_rebuild=True)

    def on_fabric_deleted(self, idx: int):
        if self.state.remove_material_item('fabric', idx):
            self._refresh_postits(force_rebuild=True)
            self._update_window_title()

    def on_trim_deleted(self, idx: int):
        if self.state.remove_material_item('trim', idx):
            self._refresh_postits(force_rebuild=True)
            self._update_window_title()

    def on_reset_clicked(self):
        self.reset_work_order_form()

    def on_back_clicked(self):
        if not self.has_any_data():
            self.go_menu()
            return
        dialog = ConfirmActionDialog(title='임시 저장', message='임시 저장 하시겠습니까?', confirm_text='예', cancel_text='아니요', parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted:
            self.go_menu()
        else:
            self.reset_work_order_form()
            self.go_menu()

    def on_save_clicked(self):
        statuses = self.controller.get_save_requirement_statuses()
        if not all(ok for _, ok in statuses):
            ValidationStatusDialog('저장 불가', statuses, parent=self).exec()
            return
        try:
            result = self.controller.save()
        except Exception as exc:
            show_error(self, '저장 실패', str(exc))
            return
        self.reset_work_order_form()
        message = f'저장 완료\n\nJSON: {result.json_path}\nSHA256(평문): {result.sha256_plain}'
        if result.image_path:
            message += f'\n이미지: {result.image_path}'
        show_info(self, '저장', message)

    def on_basic_postit_changed(self, data: dict):
        self.state.update_header(data)
        self._update_window_title()

    def on_change_note_changed(self, text: str):
        self.state.update_change_note(text)
        self._update_window_title()

    def on_fabric_postit_changed(self, idx: int, patch: dict):
        self.state.update_material_patch('fabric', idx, patch)
        self._update_window_title()

    def on_trim_postit_changed(self, idx: int, patch: dict):
        self.state.update_material_patch('trim', idx, patch)
        self._update_window_title()

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(self, '이미지 선택', '', SUPPORTED_IMAGE_FILTER)
        if not path:
            return
        try:
            self.image_preview.set_image(path)
            self.state.current_image_path = path
            self.btn_delete_image.setEnabled(True)
            self.mark_dirty()
            self._show_feedback('이미지 첨부됨')
        except Exception as exc:
            show_error(self, '오류', str(exc))

    def delete_image(self):
        self.image_preview.clear_image()
        self.state.current_image_path = None
        self.btn_delete_image.setEnabled(False)
        self.mark_dirty()
        self._show_feedback('이미지 제거됨')

    def on_add_fabric_clicked(self):
        new_index = self.state.add_material_item('fabric')
        if new_index is None:
            return
        self._refresh_postits(force_rebuild=True)
        self.postit_bar.fabric.set_active_card(new_index)
        self._update_window_title()

    def on_add_trim_clicked(self):
        new_index = self.state.add_material_item('trim')
        if new_index is None:
            return
        self._refresh_postits(force_rebuild=True)
        self.postit_bar.trim.set_active_card(new_index)
        self._update_window_title()
