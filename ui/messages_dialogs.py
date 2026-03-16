from __future__ import annotations


class DialogTitles:
    APP = "미니노트 다이어리"
    SAVE = "저장"
    SAVE_FAILED = "저장 실패"
    SAVE_BLOCKED = "저장 불가"
    ERROR = "오류"
    EDIT = "수정"
    BASIC_INFO_INPUT = "기본정보 입력"
    PARTNER_MANAGE = "거래처 관리"
    PARTNER_MANAGEMENT = PARTNER_MANAGE
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
    LOAD_TEMPLATE = "작업지시서 불러오기"
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
    WORK_ORDER_LOAD_FAILED = "작업지시서 내용을 불러오지 못했습니다."
    TEMP_SAVE_CONFIRM = "임시 저장 하시겠습니까?"
    PARTNER_DELETE_CONFIRM = "거래처를 삭제하시겠습니까?"
    WORK_ORDER_LOAD_FAILED = "선택한 작업지시서를 현재 화면으로 불러오지 못했습니다."


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
    WORK_ORDER_LOADED = "작업지시서를 불러왔습니다. 필요한 부분을 수정한 뒤 새로 저장하세요."
