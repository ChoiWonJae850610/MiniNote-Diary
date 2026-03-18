from __future__ import annotations

class FeaturePageTexts:
    COMING_SOON_TITLE = "준비 중"
    COMING_SOON_SUBTITLE = "이 기능은 아직 연결되지 않았습니다."
    PRIMARY_ACTION = "기능 준비"
    SECONDARY_ACTION = "메뉴로"






class MenuPageTexts:
    TITLE = "오늘의 작업 다이어리"
    SUBTITLE = ""
    DATE_PREFIX = "기록 기준"
    FLOW_TITLE = "업무 메뉴"
    FLOW_SUBTITLE = ""
    STATUS_TITLE = "오늘 현황"
    STATUS_SUBTITLE = ""
    UTILITIES_TITLE = "빠른 관리"
    UTILITIES_SUBTITLE = ""
    RECENT_TEMPLATE_TITLE = "최근 작업지시서"
    RECENT_ACTIVITY_TITLE = "최근 처리 내역"
    RECENT_TEMPLATE_EMPTY = "표시할 작업지시서가 없습니다."
    RECENT_ACTIVITY_EMPTY = "표시할 처리 내역이 없습니다."
    TEMPLATE_TITLE = "작업지시서 관리"
    TEMPLATE_SUBTITLE = "작성 · 수정"
    ORDER_TITLE = "발주 의뢰"
    ORDER_SUBTITLE = "수량 · 일정"
    RECEIPT_TITLE = "자재 관리"
    RECEIPT_SUBTITLE = "추가 예정"
    COMPLETE_TITLE = "거래처 관리"
    COMPLETE_SUBTITLE = "거래처 · 역할"
    SALE_TITLE = "단위 관리"
    SALE_SUBTITLE = "규격 · 단위"
    INVENTORY_TITLE = "제품 관리"
    INVENTORY_SUBTITLE = "제품 타입"
    SETTINGS_TITLE = "환경 설정"
    SETTINGS_SUBTITLE = "백업 · 초기화"



class FeatureConfigTexts:
    RECEIPT_TITLE = "자재 관리"
    RECEIPT_SUBTITLE = "원단/부자재 관리 화면을 준비 중이며, 현재는 메뉴 구조와 연결 흐름을 먼저 정리한 상태입니다."
    RECEIPT_LEFT_TITLE = "자재 관리 준비"
    RECEIPT_LEFT_HINT = "원단, 부자재, 거래처 연결을 한 화면에서 관리하는 구조를 위한 자리입니다."
    RECEIPT_LIST_ITEMS = ("JOB-0001 하늘색 저지 자켓", "JOB-0002 테스트 원단 샘플")
    RECEIPT_SUMMARY_ITEMS = ("영수증 이미지 첨부", "실제 원단 · 부자재 입력", "지출 금액 기록")
    RECEIPT_SECTIONS = (("영수증 등록", ("이미지 파일 첨부", "거래처 선택 또는 입력", "등록 일자 / 메모")), ("자재 입력", ("원단 포스트잇 입력", "부자재 포스트잇 입력", "실제 단가 · 총액 반영")), ("향후 DB 포인트", ("job_id 연결", "receipt_image_path 저장", "expense transaction 생성")))
    RECEIPT_PRIMARY = "구조 확인"
    RECEIPT_SECONDARY = "메뉴로"
    RECEIPT_HELPER = "자재 관리는 추후 별도 화면으로 확장할 예정입니다."

    COMPLETE_TITLE = "입고&검수"
    COMPLETE_SUBTITLE = "발주 의뢰 이력을 기준으로 입고일, 수량, 메모를 확인하는 화면입니다."
    COMPLETE_LEFT_TITLE = "입고 대상 발주 의뢰"
    COMPLETE_LEFT_HINT = "발주 의뢰 목록에서 입고 처리할 건을 선택합니다."
    COMPLETE_LIST_ITEMS = ("JOB-0001 하늘색 저지 자켓", "JOB-0004 기본 상의 템플릿")
    COMPLETE_SUMMARY_ITEMS = ("완료 수량 입력", "불량 / 누락 반영", "재고 생성")
    COMPLETE_SECTIONS = (("완료 입력", ("완료 일자", "실제 완료 수량", "불량 / 추가 메모")), ("재고 반영", ("현재고 생성 또는 증가", "완료 후 작업 상태 변경", "필요 시 수량 조정 허용")), ("향후 DB 포인트", ("job status update", "inventory movement create", "completed_at 기록")))
    COMPLETE_PRIMARY = "입고 반영"
    COMPLETE_SECONDARY = "화면 검토"
    COMPLETE_HELPER = "재고는 별도 테이블보다 이동 이력 기반으로 보는 방향을 염두에 둔 화면입니다."

    SALE_TITLE = "상품관리"
    SALE_SUBTITLE = "제품 가격 등록, 재고 확인, 미검수 검수, 판매 등록을 한 화면에서 처리합니다."
    SALE_LEFT_TITLE = "상품 선택"
    SALE_LEFT_HINT = "상품별 가격, 재고, 미검수 물량, 판매 등록을 관리합니다."
    SALE_LIST_ITEMS = ("하늘색 저지 자켓 / 현재고 12", "기본 상의 템플릿 / 현재고 4")
    SALE_SUMMARY_ITEMS = ("판매가 등록", "미검수 검수", "판매 등록")
    SALE_SECTIONS = (("판매 입력", ("판매일", "판매 수량", "판매 단가 / 총액")), ("재고 / 수입 반영", ("판매 후 재고 차감", "수입 거래 생성", "필요 시 메모 기록")), ("향후 DB 포인트", ("inventory decrease", "sale row create", "income transaction 생성")))
    SALE_PRIMARY = "판매 저장"
    SALE_SECONDARY = "판매 미리보기"
    SALE_HELPER = "판매 화면은 재고 조회 화면과 연결되는 구조가 자연스럽습니다."

    INVENTORY_TITLE = "제품 관리"
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
