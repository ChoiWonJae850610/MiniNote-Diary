from __future__ import annotations

from services.field_keys import MaterialTargets
from services.models import MaterialItem, WorkOrderHeader
from services.schema import MAX_MATERIAL_ITEMS
from services.work_order_state_helpers import (
    get_target_items,
    items_have_value,
    iter_target_items,
    needs_price_recompute,
    recompute_header_prices,
    set_target_items,
)


def reset_state(state) -> None:
    state.header = WorkOrderHeader()
    for target in MaterialTargets.ALL:
        set_target_items(state, target, [MaterialItem()])
    state.current_image_path = None
    recompute_sale_price(state)
    state.is_dirty = False


def state_has_any_data(state) -> bool:
    return bool(
        state.is_dirty
        or state.current_image_path
        or state.header.has_any_value()
        or any(items_have_value(items) for _, items in iter_target_items(state))
    )


def update_header_fields(state, patch: dict[str, str]) -> None:
    state.header.patch(patch)
    if needs_price_recompute(patch):
        recompute_sale_price(state)
    state.mark_dirty()


def update_material_patch_fields(state, target: str, idx: int, patch: dict[str, str]) -> None:
    if idx < 0 or not isinstance(patch, dict):
        return
    items = get_target_items(state, target)
    while len(items) <= idx:
        items.append(MaterialItem())
    items[idx].patch(patch)
    recompute_sale_price(state)
    state.mark_dirty()


def add_material_item_to_state(state, target: str, max_items: int = MAX_MATERIAL_ITEMS):
    items = get_target_items(state, target)
    if len(items) >= max_items:
        return None
    items.append(MaterialItem())
    recompute_sale_price(state)
    state.mark_dirty()
    return len(items) - 1


def remove_material_item_from_state(state, target: str, idx: int) -> bool:
    items = get_target_items(state, target)
    if 0 <= idx < len(items):
        del items[idx]
        if not items:
            items.append(MaterialItem())
        recompute_sale_price(state)
        state.mark_dirty()
        return True
    return False


def recompute_sale_price(state) -> None:
    recompute_header_prices(state.header, [items for _, items in iter_target_items(state)])
