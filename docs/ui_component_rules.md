# UI Component Rules

## 1. 고정형 포스트잇 (Fixed Post-it)

적용 대상
- 기본정보 포스트잇
- 원단/부자재 카드
- 인덱스가 붙는 일반 포스트잇 카드

규칙
- `SectionContainer` / `PostItSectionColumn` 계산 체계를 사용한다.
- 탭 높이, `tab_overlap`, footer row, external row 는 `ui/postit/layouting/constants.py`와 `THEME` 토큰을 기준으로 맞춘다.
- 내용 높이가 명확한 경우 `lock_height_to_body=True`를 유지한다.
- 카드 높이는 내용 수량이 크게 변하지 않는 전제에서 사용한다.
- 일반 카드에는 stretch 기반 확장을 넣지 않는다.

언제 쓰면 안 되는가
- 큰 메모 입력창처럼 남는 공간을 먹어야 하는 경우
- 창 크기나 영역 배분에 따라 높이가 유동적이어야 하는 경우

## 2. 가변형 카드 (Flexible Card)

적용 대상
- 작업지시서 메모 영역
- 큰 텍스트 편집 영역
- 우측 하단 남는 공간을 직접 차지해야 하는 패널

규칙
- `SectionContainer`는 사용할 수 있지만, `lock_height_to_body=False`로 운용한다.
- 카드 본문 위젯은 `QSizePolicy.Expanding`을 사용한다.
- 높이는 계산식으로 고정하지 않고 부모 레이아웃의 stretch 로 받는다.
- 하단 정렬은 픽셀 보정값보다 같은 부모 레이아웃의 bottom 기준선을 우선한다.
- footer/external spacer 계산에 의존하지 않는다.

권장 구조
- `top_region`: 내용 높이만큼 점유
- `bottom_region`: stretch=1 로 남은 공간 점유

## 3. dialogs / buttons / icon strip 규칙

### Dialog 입력 위젯
- 가능하면 `setMinimumHeight()`를 사용하고 `setFixedHeight()`는 최소화한다.
- 가로 확장 가능한 필드는 `QSizePolicy.Expanding, QSizePolicy.Fixed`를 우선한다.
- 달력/검색/파트너 연결 버튼은 정사각형이 필요해도 `setMinimumSize()` + `QSizePolicy.Fixed`를 먼저 검토한다.

### 버튼
- 의미상 반드시 폭이 고정되어야 하는 CTA만 고정 폭을 허용한다.
- 아이콘 버튼은 가능하면 토큰 기반 최소 크기를 주고, 스타일이 크기를 결정하게 한다.

### Icon strip / index strip
- 번호 버튼 줄은 최소 정사각형 크기를 기준으로 한다.
- strip 전체 높이는 footer host가 담당하고, 개별 버튼은 가능하면 최소 크기만 가진다.

## 4. 리팩토링 판단 기준

다음 질문에 하나라도 `예`이면 가변형 카드 규칙을 적용한다.
- 이 위젯이 남는 공간을 먹어야 하는가?
- 하단선이 다른 카드/패널과 같은 부모 기준선에 맞아야 하는가?
- 텍스트 양이나 DPI에 따라 높이가 달라질 수 있는가?

그 외에는 고정형 포스트잇 규칙을 우선한다.
