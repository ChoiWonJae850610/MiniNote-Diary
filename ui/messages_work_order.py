from __future__ import annotations

from ui.messages_common import Labels
from ui.messages_dialogs import DialogTitles


class PageTitles:
    WORK_ORDER = "작업지시서 생성"
    ORDER = DialogTitles.ORDER


class PageDescriptions:
    WORK_ORDER = "작업지시서 내용을 입력하고 이미지, 자재, 메모를 함께 관리합니다."
    ORDER = "저장된 작업지시서 템플릿을 선택하고 발주 의뢰 수량을 입력합니다."
    WORK_ORDER_LOAD = "저장된 작업지시서를 요약과 함께 확인한 뒤 불러와 수정하고 새 문서로 재생성할 수 있습니다."
    ORDER_LIST = "월별 필터와 검색으로 템플릿을 찾고, 예전 작업지시서도 다시 발주 의뢰할 수 있습니다."


class SectionTitles:
    ORDER_TEMPLATE_LIST = "작업지시서 목록"
    INBOUND_PAGE = "입고&검수"
    INBOUND_FILTER = "입고 대상 새로고침"
    INBOUND_ORDER_LIST = "발주 의뢰 목록"
    INBOUND_SELECTED_ORDER = "선택 발주 의뢰"
    INBOUND_INPUT = "입고 · 검수 입력"
    ORDER_TEMPLATE_DETAIL = "선택 작업지시서"
    ORDER_TEMPLATE_MATERIAL_DETAIL = "자재 상세 내역"
    ORDER_TEMPLATE_MEMO = "작업지시서 메모"
    ORDER_INPUT = "신규 발주 의뢰 입력"
    WORK_ORDER_LOAD_PREVIEW = "선택 작업지시서 요약"
    CHANGE_NOTE = "메모"
    BASIC_INFO = "기본정보"
    FABRIC = "원단"
    TRIM = "부자재"
    DYEING = "염색"
    FINISHING = "마감"
    OTHER = "기타"


class DefaultTexts:
    EMPTY_VALUE = "-"
    ORDER_MATERIAL_SUMMARY_EMPTY = "자재 내역 없음"
    NO_SAVED_WORK_ORDER = "저장된 작업지시서가 없습니다."
    WORK_ORDER_LOAD_FAILED = "선택한 작업지시서를 미리보기할 수 없습니다."
    ORDER_SAVE_SUCCESS = "발주 의뢰 저장"
    ORDER_SAVE_SUCCESS_MESSAGE = "발주 의뢰 저장 완료\n\n작업지시서: {name}\n수량: {qty}\n의뢰일: {ordered_at}"


class PostItTexts:
    CLEAR_UNIT = "(비움)"
    EMPTY_UNIT_LIST = "(단위 목록 없음)"


class HelperTexts:
    ORDER_SAVE_HINT = "발주 의뢰 수량은 1 이상이어야 하며, 저장 후에도 작업지시서 템플릿은 계속 남아 다시 의뢰할 수 있습니다."
    ORDER_TEMPLATE_META_MATERIAL = "자재: 원단 {fabric} / 부자재 {trim}"
    ORDER_TEMPLATE_META_STOCK = "재고 {stock} · 진행중 {in_progress}"
    ORDER_TEMPLATE_META_LAST_ORDER = "최근 발주 의뢰 {last_order}"
    ORDER_DETAIL_MATERIAL_SUMMARY = "{summary}"
    ORDER_DETAIL_TOTAL_MATERIAL_COST = "총 재료비 {total}"


class DomainTexts:
    PARTNER_TYPE_FACTORY = "공장"
    PARTNER_TYPE_FABRIC = "원단"
    PARTNER_TYPE_TRIM = "부자재"
    PARTNER_TYPE_DYEING = "염색"
    PARTNER_TYPE_FINISH = "마감"
    PARTNER_TYPE_OTHER = "기타"


class TableHeaders:
    UNIT = (Labels.UNIT_VALUE, Labels.UNIT_DISPLAY_NAME)
    PARTNER_TYPE = (DialogTitles.PARTNER_TYPE,)
