from __future__ import annotations

from services.work_order_defaults import empty_material_row


def normalized_stack_items(items):
    return list(items or []) or [empty_material_row()]


def clamp_active_index(active_index: int, items) -> int:
    if not items:
        return 0
    return max(0, min(active_index, len(items) - 1))


def should_update_in_place(items, current_items, cards) -> bool:
    return len(items) == len(current_items) == len(cards)
