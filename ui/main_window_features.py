from __future__ import annotations

from ui.feature_page import FeaturePageConfig, FeatureSection


def build_feature_page_configs() -> list[FeaturePageConfig]:
    return [
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
