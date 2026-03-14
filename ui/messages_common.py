from __future__ import annotations


class Actions:
    RESET = "초기화"
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


class Symbols:
    BACK = "◀"
    TYPE_MANAGE = "≡"
    ADD = "+"
    SAVE = "✓"
    DELETE = "−"
    CLOSE = "×"
    STATUS_OK = "V"
    STATUS_FAIL = "X"




class Tooltips:
    RELOAD = "목록 새로고침"
    SAVE = "저장"
    LOAD = "불러오기"
    IMAGE_UPLOAD = "이미지 첨부"
    IMAGE_DELETE = "이미지 제거"
    OPEN_CALENDAR = "달력 열기"
    PARTNER_MANAGE = "거래처 관리"
    TYPE_MANAGE = "타입 관리"
    ADD = "추가"
    EDIT = "수정"
    DELETE = "삭제"
    CLOSE = "닫기"

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
