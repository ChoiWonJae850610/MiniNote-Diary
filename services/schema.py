from __future__ import annotations

from typing import Iterable

HEADER_FIELDS: tuple[str, ...] = (
    'date',
    'style_no',
    'factory',
    'cost_display',
    'labor_display',
    'loss_display',
    'sale_price_display',
    'cost',
    'labor',
    'loss',
    'sale_price',
    'change_note',
)

REQUIRED_HEADER_FIELDS: tuple[str, ...] = (
    'date',
    'style_no',
    'factory',
    'cost_display',
    'labor_display',
    'loss_display',
    'sale_price_display',
)

MATERIAL_FIELDS: tuple[str, ...] = (
    '거래처',
    '품목',
    '수량',
    '단위',
    '단가',
    '총액',
)

REQUIRED_MATERIAL_FIELDS: tuple[str, ...] = (
    '거래처',
    '품목',
    '수량',
    '단가',
    '총액',
)

MAX_MATERIAL_ITEMS = 9
SUPPORTED_IMAGE_FILTER = 'Images (*.png *.jpg *.jpeg *.bmp)'
DEFAULT_FEEDBACK_TIMEOUT_MS = 2200


def make_empty_mapping(fields: Iterable[str]) -> dict[str, str]:
    return {field: '' for field in fields}

PARTNERS_DB_FILENAME = 'partners.json'
PARTNER_TYPES_DB_FILENAME = 'partner_types.json'
PARTNER_PICKER_TOOLTIP = '거래처 관리'
