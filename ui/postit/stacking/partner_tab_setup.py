from __future__ import annotations

from ui.messages import SectionTitles


def build_partner_tab_defs(owner):
    return [
        (owner.TAB_FABRIC, SectionTitles.FABRIC),
        (owner.TAB_TRIM, SectionTitles.TRIM),
        (owner.TAB_DYEING, SectionTitles.DYEING),
        (owner.TAB_OTHER, SectionTitles.OTHER),
    ]


def connect_partner_stack_signals(owner) -> None:
    owner.fabric.item_deleted.connect(owner.fabric_deleted.emit)
    owner.trim.item_deleted.connect(owner.trim_deleted.emit)
    owner.dyeing.item_deleted.connect(owner.dyeing_deleted.emit)
    owner.finishing.item_deleted.connect(owner.finishing_deleted.emit)
    owner.other.item_deleted.connect(owner.other_deleted.emit)
    owner.fabric.item_changed.connect(owner.fabric_item_changed.emit)
    owner.trim.item_changed.connect(owner.trim_item_changed.emit)
    owner.dyeing.item_changed.connect(owner.dyeing_item_changed.emit)
    owner.finishing.item_changed.connect(owner.finishing_item_changed.emit)
    owner.other.item_changed.connect(owner.other_item_changed.emit)
    owner.fabric.item_added.connect(owner.fabric_item_added.emit)
    owner.trim.item_added.connect(owner.trim_item_added.emit)
    owner.dyeing.item_added.connect(owner.dyeing_item_added.emit)
    owner.finishing.item_added.connect(owner.finishing_item_added.emit)
    owner.other.item_added.connect(owner.other_item_added.emit)
