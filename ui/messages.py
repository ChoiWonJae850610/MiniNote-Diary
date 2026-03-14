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


class DialogTitles:
    SAVE = "저장"
    SAVE_FAILED = "저장 실패"
    SAVE_BLOCKED = "저장 불가"
    ERROR = "오류"
    EDIT = "수정"
    BASIC_INFO_INPUT = "기본정보 입력"
    PARTNER_MANAGE = "거래처 관리"
    PARTNER_TYPE_MANAGE = "거래처 타입 관리"
    MATERIAL_ITEM_INPUT = "자재 입력"
    UNIT_MANAGE = "단위 관리"
    VALIDATION = "검증 결과"
    CONFIRM = "확인"


class Warnings:
    PARTNER_NAME_REQUIRED = "상호명을 입력하세요."
    PARTNER_TYPE_REQUIRED = "거래처 타입을 1개 이상 선택하세요."
    PARTNER_SELECT_TO_EDIT = "수정할 거래처를 먼저 선택하세요."
    MATERIAL_VENDOR_OR_ITEM_REQUIRED = "거래처 또는 품목을 1개 이상 입력하세요."


class WarningMessages(Warnings):
    pass


class InfoMessages:
    PARTNER_TYPES_SAVED = "거래처 타입 목록이 저장되었습니다."
    PARTNER_SAVED = "거래처가 저장되었습니다."
    PARTNER_UPDATED = "거래처가 수정되었습니다."
    UNITS_SAVED = "단위 목록이 저장되었습니다."
    MATERIAL_TOTAL_AUTO = "수량·단가를 입력하면 총액이 자동 계산됩니다."


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


class Placeholders:
    SEARCH = "검색어를 입력하세요"
    MEMO = "메모를 입력하세요"
    STYLE_NO = "제품명을 입력하세요"
    PARTNER_NAME = "상호명을 입력하세요"
    UNIT = "단위를 입력하세요"


class FeaturePageTexts:
    COMING_SOON_TITLE = "준비 중"
    COMING_SOON_SUBTITLE = "이 기능은 아직 연결되지 않았습니다."
    PRIMARY_ACTION = "기능 준비"
    SECONDARY_ACTION = "메뉴로"
