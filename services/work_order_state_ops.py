from __future__ import annotations

from services.field_keys import MaterialTargets
from services.models import MaterialItem, WorkOrderHeader
from services.schema import MAX_MATERIAL_ITEMS
from services.work_order_state_helpers import items_have_value, needs_price_recompute, recompute_header_prices, target_attr


def reset_state(state) -> None:
    state.header = WorkOrderHeader()
    for attr in MaterialTargets.ATTRS.values():
        setattr(state, attr, [MaterialItem()])
    state.current_image_path = None
    recompute_sale_price(state)
    state.is_dirty = False


def state_has_any_data(state) -> bool:
    return bool(
        state.is_dirty
        or state.current_image_path
        or state.header.has_any_value()
        or any(items_have_value(getattr(state, target_attr(target))) for target in MaterialTargets.ALL)
    )


def update_header_fields(state, patch: dict[str, str]) -> None:
    state.header.patch(patch)
    if needs_price_recompute(patch):
        recompute_sale_price(state)
    state.mark_dirty()


def update_material_patch_fields(state, target: str, idx: int, patch: dict[str, str]) -> None:
    if idx < 0 or not isinstance(patch, dict):
        return
    items = getattr(state, target_attr(target))
    while len(items) <= idx:
        items.append(MaterialItem())
    items[idx].patch(patch)
    recompute_sale_price(state)
    state.mark_dirty()


def add_material_item_to_state(state, target: str, max_items: int = MAX_MATERIAL_ITEMS):
    items = getattr(state, target_attr(target))
    if len(items) >= max_items:
        return None
    items.append(MaterialItem())
    recompute_sale_price(state)
    state.mark_dirty()
    return len(items) - 1


def remove_material_item_from_state(state, target: str, idx: int) -> bool:
    items = getattr(state, target_attr(target))
    if 0 <= idx < len(items):
        del items[idx]
        if not items:
            items.append(MaterialItem())
        recompute_sale_price(state)
        state.mark_dirty()
        return True
    return False


def recompute_sale_price(state) -> None:
    recompute_header_prices(state.header, [getattr(state, target_attr(target)) for target in MaterialTargets.ALL])
