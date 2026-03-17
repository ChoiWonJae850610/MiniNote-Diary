from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from services.inbound.repository import InboundRepository
from services.order.repository import OrderRepository
from services.product.repository import ProductRepository
from services.work_order.repository import WorkOrderRepository


@dataclass(frozen=True)
class StatsMetric:
    label: str
    value: str


@dataclass(frozen=True)
class StyleStatsRow:
    template_id: str
    template_name: str
    ordered_qty: int
    inbound_qty: int
    sold_qty: int
    current_stock_qty: int
    status_text: str


@dataclass(frozen=True)
class FactoryStatsRow:
    factory_name: str
    order_count: int
    ordered_qty: int


@dataclass(frozen=True)
class StatsNoteItem:
    title: str
    detail: str


@dataclass(frozen=True)
class StatsPageData:
    metrics: tuple[StatsMetric, ...]
    style_rows: tuple[StyleStatsRow, ...]
    factory_rows: tuple[FactoryStatsRow, ...]
    notes: tuple[StatsNoteItem, ...]


class StatsService:
    PERIOD_ALL = 'all'
    PERIOD_THIS_MONTH = 'this_month'
    PERIOD_LAST_30_DAYS = 'last_30_days'

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.work_order_repository = WorkOrderRepository(self.base_dir)
        self.order_repository = OrderRepository(self.base_dir)
        self.inbound_repository = InboundRepository(self.base_dir)
        self.product_repository = ProductRepository(self.base_dir)

    def build_stats_page(self, period_key: str = PERIOD_ALL) -> StatsPageData:
        summaries = self.work_order_repository.list_template_summaries()
        orders = self.order_repository.load_all()
        inbound_records = self.inbound_repository.load_all()
        product_rows = self.product_repository.load_all()

        filtered_orders = [row for row in orders if self._matches_period(row.ordered_at, period_key)]
        filtered_inbound = [row for row in inbound_records if self._matches_period(row.inbound_date, period_key)]

        total_ordered_qty = sum(max(0, int(row.ordered_qty or 0)) for row in filtered_orders)
        total_inbound_qty = sum(max(0, int(row.good_qty or 0)) for row in filtered_inbound)
        total_sold_qty = sum(max(0, int(row.sold_qty or 0)) for row in filtered_orders)

        all_completed_good_qty = sum(max(0, int(row.good_qty or 0)) for row in inbound_records if (row.inspection_status or 'completed') != 'pending')
        all_sold_qty = sum(max(0, int(row.sold_qty or 0)) for row in orders)
        current_stock_qty = max(0, all_completed_good_qty - all_sold_qty)

        metrics = (
            StatsMetric('총 발주 수량', str(total_ordered_qty)),
            StatsMetric('총 입고 수량', str(total_inbound_qty)),
            StatsMetric('총 판매 수량', str(total_sold_qty)),
            StatsMetric('현재고 합계', str(current_stock_qty)),
        )

        style_rows = self._build_style_rows(summaries=summaries, orders=orders, inbound_records=inbound_records, period_key=period_key)
        factory_rows = self._build_factory_rows(filtered_orders)
        notes = self._build_notes(style_rows=style_rows, inbound_records=inbound_records, product_rows=product_rows)

        return StatsPageData(
            metrics=metrics,
            style_rows=tuple(style_rows),
            factory_rows=tuple(factory_rows),
            notes=tuple(notes),
        )

    def _build_style_rows(self, *, summaries, orders, inbound_records, period_key: str) -> list[StyleStatsRow]:
        display_names: dict[str, str] = {summary.template_id: (summary.name or summary.template_id) for summary in summaries}
        template_ids: set[str] = set(display_names.keys())
        template_ids.update(row.template_id for row in orders)
        template_ids.update(row.template_id for row in inbound_records)

        rows: list[StyleStatsRow] = []
        for template_id in template_ids:
            template_orders = [row for row in orders if row.template_id == template_id]
            template_inbound = [row for row in inbound_records if row.template_id == template_id]

            ordered_qty = sum(max(0, int(row.ordered_qty or 0)) for row in template_orders if self._matches_period(row.ordered_at, period_key))
            inbound_qty = sum(max(0, int(row.good_qty or 0)) for row in template_inbound if self._matches_period(row.inbound_date, period_key))
            sold_qty = sum(max(0, int(row.sold_qty or 0)) for row in template_orders if self._matches_period(row.ordered_at, period_key))

            all_completed_good_qty = sum(max(0, int(row.good_qty or 0)) for row in template_inbound if (row.inspection_status or 'completed') != 'pending')
            all_sold_qty = sum(max(0, int(row.sold_qty or 0)) for row in template_orders)
            current_stock_qty = max(0, all_completed_good_qty - all_sold_qty)

            pending_count = sum(1 for row in template_inbound if (row.inspection_status or 'completed') == 'pending')
            total_ordered_all = sum(max(0, int(row.ordered_qty or 0)) for row in template_orders)
            if pending_count > 0:
                status_text = f'미검수 {pending_count}건'
            elif all_completed_good_qty >= total_ordered_all and total_ordered_all > 0:
                status_text = '입고완료'
            elif all_completed_good_qty > 0:
                status_text = '부분입고'
            elif total_ordered_all > 0:
                status_text = '진행중'
            else:
                status_text = '대기'

            if not (ordered_qty or inbound_qty or sold_qty or current_stock_qty or pending_count):
                continue

            rows.append(
                StyleStatsRow(
                    template_id=template_id,
                    template_name=display_names.get(template_id) or template_id,
                    ordered_qty=ordered_qty,
                    inbound_qty=inbound_qty,
                    sold_qty=sold_qty,
                    current_stock_qty=current_stock_qty,
                    status_text=status_text,
                )
            )

        rows.sort(key=lambda row: (row.current_stock_qty, row.ordered_qty, row.template_name), reverse=True)
        return rows

    @staticmethod
    def _build_factory_rows(orders) -> list[FactoryStatsRow]:
        grouped: dict[str, FactoryStatsRow] = {}
        for row in orders:
            name = (row.factory_name or '').strip() or '거래처 없음'
            current = grouped.get(name)
            if current is None:
                grouped[name] = FactoryStatsRow(factory_name=name, order_count=1, ordered_qty=max(0, int(row.ordered_qty or 0)))
                continue
            grouped[name] = FactoryStatsRow(
                factory_name=name,
                order_count=current.order_count + 1,
                ordered_qty=current.ordered_qty + max(0, int(row.ordered_qty or 0)),
            )
        rows = list(grouped.values())
        rows.sort(key=lambda row: (row.ordered_qty, row.order_count, row.factory_name), reverse=True)
        return rows[:10]

    @staticmethod
    def _build_notes(*, style_rows: list[StyleStatsRow], inbound_records, product_rows) -> list[StatsNoteItem]:
        notes: list[StatsNoteItem] = []

        pending_rows = [row for row in inbound_records if (row.inspection_status or 'completed') == 'pending']
        pending_rows.sort(key=lambda row: ((row.inbound_date or ''), (row.created_at or ''), row.inbound_id), reverse=True)
        if pending_rows:
            notes.append(StatsNoteItem('미검수 대기', f'{len(pending_rows)}건 · 최신 {pending_rows[0].template_name or pending_rows[0].template_id}'))

        low_stock = [row for row in style_rows if row.current_stock_qty <= 3]
        if low_stock:
            top = low_stock[:3]
            notes.append(StatsNoteItem('저재고 품목', ', '.join(f'{row.template_name}({row.current_stock_qty})' for row in top)))

        if product_rows:
            latest_product = sorted(product_rows, key=lambda row: row.updated_at or '', reverse=True)[0]
            notes.append(StatsNoteItem('최근 상품 수정', f'{latest_product.template_name or latest_product.template_id} · {latest_product.updated_at[:10] if latest_product.updated_at else "날짜 없음"}'))

        if not notes:
            notes.append(StatsNoteItem('안내', '표시할 통계 알림이 없습니다.'))
        return notes[:5]

    @staticmethod
    def _matches_period(raw_date: str, period_key: str) -> bool:
        if period_key == StatsService.PERIOD_ALL:
            return True
        parsed = StatsService._parse_date(raw_date)
        if parsed is None:
            return False
        today = date.today()
        if period_key == StatsService.PERIOD_THIS_MONTH:
            return parsed.year == today.year and parsed.month == today.month
        if period_key == StatsService.PERIOD_LAST_30_DAYS:
            return parsed >= (today - timedelta(days=29))
        return True

    @staticmethod
    def _parse_date(raw_date: str) -> date | None:
        text = (raw_date or '').strip()
        if not text:
            return None
        for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'):
            try:
                return datetime.strptime(text[:19], fmt).date()
            except ValueError:
                continue
        return None
