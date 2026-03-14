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


class DefaultTexts:
    EMPTY_VALUE = "-"
    ORDER_MATERIAL_SUMMARY_EMPTY = "원단 0 / 부자재 0"
    ORDER_SAVE_SUCCESS = "발주 저장"
    ORDER_SAVE_SUCCESS_MESSAGE = "발주 저장 완료\n\n작업지시서: {name}\n수량: {qty}\n발주일: {ordered_at}"
