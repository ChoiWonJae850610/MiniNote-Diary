from __future__ import annotations


class Tooltips:
    BACK = "뒤로가기"
    RELOAD = "새로고침"
    SAVE = "저장"
    LOAD = "불러오기"
    IMAGE_UPLOAD = "사진 업로드"
    IMAGE_DELETE = "사진 삭제"
    OPEN_CALENDAR = "달력 열기"
    PARTNER_MANAGE = "거래처 관리"
    TYPE_MANAGE = "타입 관리"
    ADD = "추가"
    EDIT = "수정"
    CLOSE = "닫기"
    DELETE = "삭제"


class Buttons:
    OK = "확인"
    CANCEL = "취소"
    CLOSE = "닫기"
    ADD = "추가"
    SAVE = "저장"
    DELETE = "삭제"
    LOAD = "불러오기"
    RESET = "초기화"
    YES = "예"
    NO = "아니요"
    REFRESH = "목록 새로고침"
    IMAGE_ATTACH = "이미지 첨부"
    REVIEW_BEFORE_COMPLETE = "완료 전 검토"
    FILTER_OPEN = "필터 열기"
    SALES_PREVIEW = "판매 미리보기"
    TYPE_MANAGE = "타입 관리"
    ORDER_SAVE = "발주 저장"
    COMPLETE_PROCESS = "작업 완료 처리"
    STATS_REFRESH = "조회 새로고침"
    PARTNER_SAVE = "거래처 저장"
    RECEIPT_SAVE = "영수증 저장"


class DialogTitles:
    APP = "미니노트 다이어리"
    SAVE = "저장"
    SAVE_FAILED = "저장 실패"
    SAVE_BLOCKED = "저장 불가"
    ERROR = "오류"
    EDIT = "수정"
    BASIC_INFO_INPUT = "기본정보 입력"
    PARTNER_MANAGE = "거래처 관리"
    PARTNER_TYPE_MANAGE = "거래처 타입 관리"
    PARTNER_ADD = "거래처 추가"
    PARTNER_EDIT = "거래처 수정"
    PARTNER_LIST = "거래처 목록"
    PARTNER_BASIC_INFO = "거래처 기본 정보"
    PARTNER_TYPE = "거래처 타입"
    MATERIAL_ITEM_INPUT = "자재 입력"
    UNIT_MANAGE = "단위 관리"
    VALIDATION = "검증 결과"
    CONFIRM = "확인"
    NOTE = "메모"
    ORDER = "발주"
    ORDER_SAVE = "발주 저장"
    TEMP_SAVE = "임시 저장"
    IMAGE_SELECT = "이미지 선택"
    RECEIPT = "영수증 등록"
    INVENTORY = "재고 / 통계"
    COMING_SOON = "준비중"
    SCREEN_REVIEW = "화면 검토"


class Warnings:
    PARTNER_NAME_REQUIRED = "상호명을 입력하세요."
    PARTNER_TYPE_REQUIRED = "거래처 타입을 1개 이상 선택하세요."
    PARTNER_SELECT_TO_EDIT = "수정할 거래처를 먼저 선택하세요."
    MATERIAL_VENDOR_OR_ITEM_REQUIRED = "거래처 또는 품목을 1개 이상 입력하세요."
    ORDER_SELECT_TEMPLATE_FIRST = "발주할 작업지시서를 먼저 선택하세요."
    ORDER_TEMPLATE_LOAD_FAILED = "선택한 작업지시서를 다시 불러올 수 없습니다."
    TEMP_SAVE_CONFIRM = "임시 저장 하시겠습니까?"
    PARTNER_DELETE_CONFIRM = "거래처를 삭제하시겠습니까?"


class WarningMessages(Warnings):
    pass


class InfoMessages:
    PARTNER_TYPES_SAVED = "거래처 타입 목록이 저장되었습니다."
    PARTNER_SAVED = "거래처가 저장되었습니다."
    PARTNER_UPDATED = "거래처가 수정되었습니다."
    UNITS_SAVED = "단위 목록이 저장되었습니다."
    MATERIAL_TOTAL_AUTO = "수량·단가를 입력하면 총액이 자동 계산됩니다."
    IMAGE_ATTACHED = "이미지 첨부됨"
    IMAGE_REMOVED = "이미지 제거됨"
    NO_ORDER_HISTORY = "발주 이력 없음"
    NO_MEMO = "메모 없음"
    NO_FACTORY = "공장 미지정"
    NONE = "없음"
    FEATURE_PARTNER_PENDING = "거래처 관리 편집 화면은 다음 단계에서 실제 입력 폼과 연결합니다."
    FEATURE_INVENTORY_PENDING = "통계 화면은 SQLite 전환 후 실제 집계 데이터와 연결합니다."
    FEATURE_GENERIC_PENDING = "이 화면은 UI 흐름 검토용으로 먼저 배치했습니다. 다음 단계에서 실제 입력/저장 로직을 연결합니다."
    FEATURE_RECEIPT_EXTEND = "이미지 첨부와 포스트잇 입력을 결합하는 방향으로 화면을 확장할 예정입니다."
    FEATURE_SCREEN_REVIEW = "현재는 메뉴 구조와 화면 흐름을 먼저 확인하는 단계입니다."
    PARTNER_TYPE_SELECT_HINT = "최소 1개 이상 선택"
    PARTNER_MEMO_HINT = "간단한 메모"
    PARTNER_SEARCH_PLACEHOLDER = "검색"
    PARTNER_EMPTY_VALUE = "-"
    PARTNER_EMPTY_LIST = "(목록 없음)"


class Labels:
    DATE = "날짜"
    STYLE_NO = "제품명"
    FACTORY = "공장"
    COST = "재료비"
    LABOR = "공임"
    LOSS = "로스"
    SALE_PRICE = "원가"
    VENDOR = "거래처"
    FABRIC_VENDOR = "원단처"
    ITEM = "품목"
    QTY = "수량"
    UNIT = "단위"
    UNIT_PRICE = "단가"
    TOTAL = "총액"
    CHANGE_NOTE = "메모"
    UNIT_VALUE = "단위"
    UNIT_DISPLAY_NAME = "표시 이름"
    PARTNER_TYPE = "거래처 타입"
    ORDER_TEMPLATE = "작업지시서"
    BASE_DATE = "기준일"
    MATERIAL_SUMMARY = "자재 요약"
    LAST_ORDER = "최근 발주"
    TOTAL_ORDERED = "누적 발주"
    IN_PROGRESS_QTY = "진행중 수량"
    CURRENT_STOCK = "현재 재고"
    ORDER_QTY = "발주 수량"
    ORDER_DATE = "발주일"
    ORDER_MEMO = "발주 메모"
    MONTH_FILTER = "기준 월"
    SEARCH = "검색"
    ALL_MONTHS = "전체 월"
    PARTNER_NAME = "상호명"
    OWNER_NAME = "사장명"
    PHONE = "연락처"
    ADDRESS = "주소"
    MEMO = "메모"


class Placeholders:
    SEARCH = "검색어를 입력하세요"
    MEMO = "메모를 입력하세요"
    STYLE_NO = "제품명을 입력하세요"
    PARTNER_NAME = "상호명을 입력하세요"
    UNIT = "단위를 입력하세요"
    ORDER_SEARCH = "작업지시서 검색"
    OWNER_NAME = "사장명"
    PHONE = "연락처"
    ADDRESS = "주소"
    SHORT_MEMO = "간단한 메모"
    PARTNER_SEARCH = "검색"


class FileDialogFilters:
    IMAGES = "Images (*.png *.jpg *.jpeg *.bmp)"


class UiTiming:
    FEEDBACK_TIMEOUT_MS = 2200


class FeaturePageTexts:
    COMING_SOON_TITLE = "준비 중"
    COMING_SOON_SUBTITLE = "이 기능은 아직 연결되지 않았습니다."
    PRIMARY_ACTION = "기능 준비"
    SECONDARY_ACTION = "메뉴로"


class PageTitles:
    WORK_ORDER = "작업지시서 생성"
    ORDER = DialogTitles.ORDER


class PageDescriptions:
    WORK_ORDER = "작업지시서 내용을 입력하고 이미지, 자재, 메모를 함께 관리합니다."
    ORDER = "저장된 작업지시서 템플릿을 선택하고 발주 수량을 입력합니다."
    ORDER_LIST = "월별 필터와 검색으로 템플릿을 찾고, 예전 작업지시서도 다시 발주할 수 있습니다."


class SectionTitles:
    ORDER_TEMPLATE_LIST = "작업지시서 목록"
    ORDER_TEMPLATE_DETAIL = "선택 작업지시서"
    ORDER_TEMPLATE_MEMO = "작업지시서 메모"
    ORDER_INPUT = "신규 발주 입력"
    CHANGE_NOTE = "메모"
    BASIC_INFO = "기본정보"
    FABRIC = "원단"
    TRIM = "부자재"
    DYEING = "염색"
    FINISHING = "마감"
    OTHER = "기타"


class DefaultTexts:
    EMPTY_VALUE = "-"
    ORDER_MATERIAL_SUMMARY_EMPTY = "원단 0 / 부자재 0"
    ORDER_SAVE_SUCCESS = "발주 저장"
    ORDER_SAVE_SUCCESS_MESSAGE = "발주 저장 완료\n\n작업지시서: {name}\n수량: {qty}\n발주일: {ordered_at}"


class MenuPageTexts:
    TITLE = "업무 메뉴"
    SUBTITLE = "작업지시서 관리부터 작업 시작, 영수증 등록, 판매/재고 확인까지 흐름 기준으로 화면을 구성합니다."
    TEMPLATE_TITLE = "작업지시서 관리"
    TEMPLATE_SUBTITLE = "기준 문서 생성 · 수정"
    ORDER_TITLE = "발주"
    ORDER_SUBTITLE = "템플릿 선택 후 발주 수량 입력"
    RECEIPT_TITLE = "원단/부자재 등록"
    RECEIPT_SUBTITLE = "영수증 첨부 · 실제 지출 기록"
    COMPLETE_TITLE = "작업 완료"
    COMPLETE_SUBTITLE = "완료 수량 반영 · 재고 생성"
    SALE_TITLE = "판매 등록"
    SALE_SUBTITLE = "판매 수량 · 수입 반영"
    INVENTORY_TITLE = "재고 / 통계"
    INVENTORY_SUBTITLE = "재고 현황 · 월별 흐름 확인"


class TableHeaders:
    UNIT = (Labels.UNIT_VALUE, Labels.UNIT_DISPLAY_NAME)
    PARTNER_TYPE = (DialogTitles.PARTNER_TYPE,)


class PostItTexts:
    CLEAR_UNIT = "(비움)"
    EMPTY_UNIT_LIST = "(단위 목록 없음)"


class HelperTexts:
    ORDER_SAVE_HINT = "발주 수량은 1 이상이어야 하며, 저장 후에도 작업지시서 템플릿은 계속 남아 다시 발주할 수 있습니다."
    ORDER_TEMPLATE_META_MATERIAL = "자재: 원단 {fabric} / 부자재 {trim}"
    ORDER_TEMPLATE_META_STOCK = "재고 {stock} · 진행중 {in_progress}"
    ORDER_TEMPLATE_META_LAST_ORDER = "최근 발주 {last_order}"
    ORDER_DETAIL_MATERIAL_SUMMARY = "원단 {fabric} / 부자재 {trim}"


class DomainTexts:
    PARTNER_TYPE_FACTORY = "공장"
    PARTNER_TYPE_FABRIC = "원단"
    PARTNER_TYPE_TRIM = "부자재"
    PARTNER_TYPE_DYEING = "염색"
    PARTNER_TYPE_FINISH = "마감"
    PARTNER_TYPE_OTHER = "기타"


class FeatureConfigTexts:
    RECEIPT_TITLE = "원단 / 부자재 등록"
    RECEIPT_SUBTITLE = "진행 중인 작업을 선택하고 영수증 이미지를 첨부한 뒤 실제 매입 내용을 입력하는 흐름입니다."
    RECEIPT_LEFT_TITLE = "진행중 작업 선택"
    RECEIPT_LEFT_HINT = "이미 생성된 작업 중 지출을 등록할 대상을 선택합니다."
    RECEIPT_LIST_ITEMS = ("JOB-0001 하늘색 저지 자켓", "JOB-0002 테스트 원단 샘플")
    RECEIPT_SUMMARY_ITEMS = ("영수증 이미지 첨부", "실제 원단 · 부자재 입력", "지출 금액 기록")
    RECEIPT_SECTIONS = (("영수증 등록", ("이미지 파일 첨부", "거래처 선택 또는 입력", "등록 일자 / 메모")), ("자재 입력", ("원단 포스트잇 입력", "부자재 포스트잇 입력", "실제 단가 · 총액 반영")), ("향후 DB 포인트", ("job_id 연결", "receipt_image_path 저장", "expense transaction 생성")))
    RECEIPT_PRIMARY = "영수증 저장"
    RECEIPT_SECONDARY = "이미지 첨부"
    RECEIPT_HELPER = "현재는 클릭 가능한 화면 뼈대만 배치했고, 실제 입력 위젯은 다음 단계에서 연결하면 됩니다."

    COMPLETE_TITLE = "작업 완료"
    COMPLETE_SUBTITLE = "작업 완료 처리 시 실제 완료 수량을 확정하고 재고 생성 흐름으로 연결하는 화면입니다."
    COMPLETE_LEFT_TITLE = "완료 대상 작업"
    COMPLETE_LEFT_HINT = "진행 중 상태의 작업을 골라 완료 처리합니다."
    COMPLETE_LIST_ITEMS = ("JOB-0001 하늘색 저지 자켓", "JOB-0004 기본 상의 템플릿")
    COMPLETE_SUMMARY_ITEMS = ("완료 수량 입력", "불량 / 누락 반영", "재고 생성")
    COMPLETE_SECTIONS = (("완료 입력", ("완료 일자", "실제 완료 수량", "불량 / 추가 메모")), ("재고 반영", ("현재고 생성 또는 증가", "완료 후 작업 상태 변경", "필요 시 수량 조정 허용")), ("향후 DB 포인트", ("job status update", "inventory movement create", "completed_at 기록")))
    COMPLETE_PRIMARY = "작업 완료 처리"
    COMPLETE_SECONDARY = "완료 전 검토"
    COMPLETE_HELPER = "재고는 별도 테이블보다 이동 이력 기반으로 보는 방향을 염두에 둔 화면입니다."

    SALE_TITLE = "판매 등록"
    SALE_SUBTITLE = "생성된 재고 중 판매 대상을 선택하고 수량과 금액을 기록하는 화면 흐름입니다."
    SALE_LEFT_TITLE = "판매 대상 선택"
    SALE_LEFT_HINT = "현재고가 존재하는 품목을 기준으로 판매를 기록합니다."
    SALE_LIST_ITEMS = ("하늘색 저지 자켓 / 현재고 12", "기본 상의 템플릿 / 현재고 4")
    SALE_SUMMARY_ITEMS = ("판매 수량 입력", "판매 금액 기록", "재고 차감")
    SALE_SECTIONS = (("판매 입력", ("판매일", "판매 수량", "판매 단가 / 총액")), ("재고 / 수입 반영", ("판매 후 재고 차감", "수입 거래 생성", "필요 시 메모 기록")), ("향후 DB 포인트", ("inventory decrease", "sale row create", "income transaction 생성")))
    SALE_PRIMARY = "판매 저장"
    SALE_SECONDARY = "판매 미리보기"
    SALE_HELPER = "판매 화면은 재고 조회 화면과 연결되는 구조가 자연스럽습니다."

    INVENTORY_TITLE = "재고 / 통계"
    INVENTORY_SUBTITLE = "현재고, 진행중 작업 수, 월별 지출/수입 흐름을 한 번에 보는 대시보드 방향의 화면입니다."
    INVENTORY_LEFT_TITLE = "조회 기준"
    INVENTORY_LEFT_HINT = "제품별 / 거래처별 / 기간별 조회가 들어갈 자리를 먼저 잡아둡니다."
    INVENTORY_LIST_ITEMS = ("현재고 보기", "월별 지출 흐름", "거래처별 지출 비교", "작업 진행 상태")
    INVENTORY_SUMMARY_ITEMS = ("현재고 확인", "월별 지출 · 수입", "거래처별 통계")
    INVENTORY_SECTIONS = (("대시보드 카드", ("진행중 작업 수", "완료 작업 수", "재고 합계 / 품목 수")), ("그래프 영역 후보", ("월별 지출 추이", "월별 수입 추이", "거래처별 원가 비교")), ("향후 DB 포인트", ("financial transaction 집계", "inventory movement 집계", "기간 필터 query")))
    INVENTORY_PRIMARY = "조회 새로고침"
    INVENTORY_SECONDARY = "필터 열기"
    INVENTORY_HELPER = "이 화면은 SQLite 전환 후 repository / stats service가 준비되면 실제 데이터와 바로 연결할 수 있습니다."

    PARTNER_TITLE = "거래처 관리"
    PARTNER_SUBTITLE = "거래처 정보와 역할 타입을 관리하는 화면 구조입니다. 실제 원단처/부자재처/공장 구분을 여기서 정리합니다."
    PARTNER_LEFT_TITLE = "거래처 목록"
    PARTNER_LEFT_HINT = "상호명 중심으로 조회하고 상세 정보는 우측에서 편집하는 구성을 상정합니다."
    PARTNER_LIST_ITEMS = ("민트 봉제공장", "샘플 원단상사", "테스트 부자재", "OO염색")
    PARTNER_SUMMARY_ITEMS = ("거래처 기본정보", "타입 다중 선택", "주소 / 연락처 관리")
    PARTNER_SECTIONS = (("기본 정보", ("상호명", "사장명 / 연락처", "주소 / 메모")), ("타입 관리", ("봉제공장", "원단처", "부자재처", "염색 / 마감 / 기사 / 기타")), ("향후 DB 포인트", ("partner master", "partner type link", "거래 이력 연결")))
    PARTNER_PRIMARY = "거래처 저장"
    PARTNER_SECONDARY = "타입 관리"
    PARTNER_HELPER = "거래처 타입 추가 기능은 별도 작은 관리 팝업으로 분리하는 쪽이 유지보수에 유리합니다."
