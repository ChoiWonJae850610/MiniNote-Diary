from __future__ import annotations

import html
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable

from services.common.models import MaterialItem
from services.order.repository import TemplateOrderStats
from services.work_order.repository import WorkOrderTemplateDetail


@dataclass(frozen=True)
class MaterialLineSummary:
    partner: str
    item: str
    qty: str
    unit: str
    unit_price: str
    total: str
    total_amount: int


@dataclass(frozen=True)
class MaterialPartnerSummary:
    partner: str
    items: list[MaterialLineSummary]
    subtotal_amount: int


@dataclass(frozen=True)
class MaterialCategorySummary:
    key: str
    title: str
    partners: list[MaterialPartnerSummary]
    subtotal_amount: int
    item_count: int


@dataclass(frozen=True)
class WorkOrderSummaryView:
    name: str
    factory_name: str
    date: str
    change_note: str
    image_attached: bool
    categories: list[MaterialCategorySummary]
    total_amount: int
    order_stats: TemplateOrderStats | None = None

    @property
    def material_summary_text(self) -> str:
        counts = []
        for category in self.categories:
            counts.append(f"{category.title} {category.item_count}")
        return " / ".join(counts) if counts else "자재 없음"


    def to_detail_html(self, *, include_total_amount: bool = True, include_header: bool = True) -> str:
        blocks: list[str] = []
        if include_header:
            header_rows: list[str] = []
            if self.name:
                header_rows.append(f"<div><b>작업지시서</b> {html.escape(self.name)}</div>")
            if self.factory_name:
                header_rows.append(f"<div><b>공장</b> {html.escape(self.factory_name)}</div>")
            if self.date:
                header_rows.append(f"<div><b>기준일</b> {html.escape(self.date)}</div>")
            if self.order_stats is not None:
                last_order = self.order_stats.last_ordered_at or "없음"
                header_rows.append(f"<div><b>발주이력</b> {self.order_stats.order_count}건 / 최근 {html.escape(last_order)}</div>")
            if header_rows:
                blocks.append(''.join(header_rows))
        for category in self.categories:
            rows = [
                "<tr><th style='text-align:left;padding:4px 8px;'>품목</th><th style='text-align:center;padding:4px 8px;'>수량</th><th style='text-align:center;padding:4px 8px;'>단위</th><th style='text-align:right;padding:4px 8px;'>단가</th><th style='text-align:right;padding:4px 8px;'>금액</th></tr>"
            ]
            if not category.partners:
                rows.append("<tr><td colspan='5' style='padding:6px 8px;'>내역 없음</td></tr>")
            else:
                for partner_summary in category.partners:
                    rows.append(f"<tr><td colspan='5' style='padding:8px 8px 4px 8px;font-weight:700;background:#f5f5f5;'>{html.escape(partner_summary.partner)}</td></tr>")
                    for item in partner_summary.items:
                        rows.append(
                            f"<tr>"
                            f"<td style='padding:4px 8px;'>{html.escape(item.item or '-')}</td>"
                            f"<td style='padding:4px 8px;text-align:center;'>{html.escape(item.qty or '-')}</td>"
                            f"<td style='padding:4px 8px;text-align:center;'>{html.escape(item.unit or '-')}</td>"
                            f"<td style='padding:4px 8px;text-align:right;'>{html.escape(item.unit_price or '-')}</td>"
                            f"<td style='padding:4px 8px;text-align:right;'>{html.escape(item.total or _format_amount(item.total_amount))}</td>"
                            f"</tr>"
                        )
                    rows.append(f"<tr><td colspan='4' style='padding:4px 8px;text-align:right;font-weight:700;'>소계</td><td style='padding:4px 8px;text-align:right;font-weight:700;'>{_format_amount(partner_summary.subtotal_amount)}</td></tr>")
                rows.append(f"<tr><td colspan='4' style='padding:6px 8px;text-align:right;font-weight:700;'> {html.escape(category.title)} 합계</td><td style='padding:6px 8px;text-align:right;font-weight:700;'>{_format_amount(category.subtotal_amount)}</td></tr>")
            table = "<table cellspacing='0' cellpadding='0' style='width:100%; border-collapse:collapse;'>" + ''.join(rows) + "</table>"
            blocks.append(f"<div style='margin-top:10px;'><div style='font-weight:700; margin-bottom:6px;'>{html.escape(category.title)}</div>{table}</div>")
        if include_total_amount:
            blocks.append(f"<div style='margin-top:10px;font-weight:700;text-align:right;'>총 재료비 {_format_amount(self.total_amount)}</div>")
        if self.change_note:
            blocks.append(f"<div style='margin-top:12px;'><div style='font-weight:700; margin-bottom:4px;'>메모</div><div>{html.escape(self.change_note).replace(chr(10), '<br/>')}</div></div>")
        return "<div style='font-family:Arial, Malgun Gothic, sans-serif; font-size:12px; line-height:1.45;'>" + ''.join(blocks) + "</div>"

    def to_detail_text(self, *, include_total_amount: bool = True) -> str:
        lines: list[str] = []
        if self.name:
            lines.append(f"작업지시서: {self.name}")
        if self.factory_name:
            lines.append(f"공장: {self.factory_name}")
        if self.date:
            lines.append(f"기준일: {self.date}")
        if self.order_stats is not None:
            last_order = self.order_stats.last_ordered_at or "없음"
            lines.append(f"발주이력: {self.order_stats.order_count}건 / 최근 {last_order}")
        lines.append("")
        for category in self.categories:
            lines.append(f"[{category.title}]")
            if not category.partners:
                lines.append("- 내역 없음")
                lines.append("")
                continue
            for partner_summary in category.partners:
                lines.append(partner_summary.partner)
                for item in partner_summary.items:
                    qty_text = f"{item.qty}{item.unit}".strip()
                    qty_text = qty_text or "-"
                    unit_price_text = item.unit_price or "-"
                    total_text = item.total or _format_amount(item.total_amount)
                    lines.append(f"  - {item.item or '-'} / {qty_text} / {unit_price_text} / {total_text}")
                lines.append(f"  소계: {_format_amount(partner_summary.subtotal_amount)}")
            lines.append(f"{category.title} 합계: {_format_amount(category.subtotal_amount)}")
            lines.append("")
        if include_total_amount:
            lines.append(f"총 재료비: {_format_amount(self.total_amount)}")
        if self.change_note:
            lines.append("")
            lines.append("메모")
            lines.append(self.change_note)
        return "\n".join(lines).strip()


_CATEGORY_SPECS = (
    ("fabrics", "원단"),
    ("trims", "부자재"),
    ("dyeings", "염색"),
    ("finishings", "마감"),
    ("others", "기타"),
)


def build_work_order_summary_view(
    detail: WorkOrderTemplateDetail,
    *,
    order_stats: TemplateOrderStats | None = None,
) -> WorkOrderSummaryView:
    categories: list[MaterialCategorySummary] = []
    total_amount = 0
    for attr_name, title in _CATEGORY_SPECS:
        category = _build_category_summary(attr_name, title, getattr(detail.document, attr_name, []))
        categories.append(category)
        total_amount += category.subtotal_amount
    return WorkOrderSummaryView(
        name=detail.summary.name,
        factory_name=detail.summary.factory_name,
        date=detail.summary.date,
        change_note=detail.summary.change_note,
        image_attached=bool(detail.summary.image_path),
        categories=categories,
        total_amount=total_amount,
        order_stats=order_stats,
    )


def _build_category_summary(key: str, title: str, items: Iterable[MaterialItem]) -> MaterialCategorySummary:
    grouped: dict[str, list[MaterialLineSummary]] = {}
    item_count = 0
    for item in items or []:
        if not item.has_any_value():
            continue
        item_count += 1
        total_amount = _to_amount(item.total)
        line = MaterialLineSummary(
            partner=(item.vendor or "거래처 미지정").strip() or "거래처 미지정",
            item=(item.item or "").strip(),
            qty=(item.qty or "").strip(),
            unit=(item.unit or "").strip(),
            unit_price=(item.unit_price or "").strip(),
            total=(item.total or "").strip(),
            total_amount=total_amount,
        )
        grouped.setdefault(line.partner, []).append(line)
    partners: list[MaterialPartnerSummary] = []
    subtotal_amount = 0
    for partner_name in sorted(grouped.keys()):
        lines = grouped[partner_name]
        partner_total = sum(line.total_amount for line in lines)
        subtotal_amount += partner_total
        partners.append(MaterialPartnerSummary(partner=partner_name, items=lines, subtotal_amount=partner_total))
    return MaterialCategorySummary(
        key=key,
        title=title,
        partners=partners,
        subtotal_amount=subtotal_amount,
        item_count=item_count,
    )


def _to_amount(value: str) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(Decimal(text))
    except (InvalidOperation, ValueError):
        return 0


def _format_amount(value: int) -> str:
    return f"{int(value):,}"


__all__ = [
    "WorkOrderSummaryView",
    "build_work_order_summary_view",
]
